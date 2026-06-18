# subset-b-008365 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/kernel_to_common.c -->
# sources/security-integrity/selinux/libsepol/src/kernel_to_common.c

Purpose: shared support code for converting a binary kernel `policydb` into textual output. It provides safe-ish formatted allocation/printing helpers, the growable `struct strs` string-list abstraction, ebitmap/name conversion utilities, initial-SID name mapping helpers, deterministic object-context sorting, and policy-version gating used by `kernel_to_conf.c` and sibling conversion code.

Important APIs and functions: `sepol_indent` and `sepol_printf` wrap `fprintf`/`vfprintf` with libsepol error logging; `create_str` allocates formatted strings with `vasprintf`; `strs_init`, `strs_destroy`, `strs_free_all`, `strs_add`, `strs_create_and_add`, `strs_add_at_index`, `strs_to_str`, `strs_sort`, and write helpers manage lists of borrowed or owned strings; `hashtab_ordered_to_strs`, `ebitmap_to_strs`, and `ebitmap_to_str` convert policy symbol tables and bitmaps to printable names; stack wrappers (`strs_stack_*`) are used by postfix expression printers; `isids_to_strs` expands SID numeric values through SELinux/Xen fallback tables; `sort_ocontexts` sorts platform-specific object-context lists; `check_for_supported_policy` rejects unsupported policy inputs.

Control flow: callers build string lists with explicit ownership rules, optionally sort, then either join or emit one line per entry. `isids_to_strs` scans initial SID ocontexts to find the maximum numeric SID, fills an indexed string list from the static SID-name tables or `UNKNOWN<n>`, and returns ownership to the caller. `sort_ocontexts` dispatches by `pdb->target_platform`: SELinux sorts fsuse, port, netif, IPv4/IPv6 node, ibpkey, and ibendport lists; Xen sorts pirq, ioport, iomem, pcidevice, and devicetree lists. Each sort converts a linked list to an array, `qsort`s it with a domain comparator, then relinks the existing nodes.

State and persistence: there is no disk persistence. Functions mutate caller-owned `struct strs`, `policydb->ocontexts[]` linked-list order, and error state via libsepol logging. `strs` may contain borrowed pointers or owned formatted strings, so callers must choose between `strs_destroy` only and `strs_free_all` plus destroy.

Dependencies and integration points: depends on libsepol policydb internals, `ebitmap`, `hashtab`, `symtab`, protocol constants, `debug.h`, `private.h`, and `kernel_to_common.h`. It is the shared substrate for kernel-to-conf/CIL conversion; ordering must stay aligned with CIL post-processing for wildcard netif contexts.

Risks: ownership is non-uniform in `struct strs`; using `strs_free_all` on borrowed names or omitting it for allocated strings causes memory errors or leaks. `strs_add_at_index` overwrites without freeing any existing element. Several comparators assume well-formed policy ranges and names. `check_for_supported_policy` explicitly rejects policy versions 20 through 23 because attribute gaps can make textual output ambiguous.

Test signals: exercise round-trip textual conversion with SELinux and Xen policies, including initial SIDs beyond known tables, wildcard netif names, ranged ports/ioports/iomem, IPv4/IPv6 masks, InfiniBand contexts, and empty lists. Memory tests should cover all `strs` ownership paths and simulated allocation failures in list growth and sorting.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/kernel_to_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/kernel_to_common.h -->
# sources/security-integrity/selinux/libsepol/src/kernel_to_common.h

Purpose: internal header for kernel policy text conversion helpers. It defines static lookup data and declares the helper API implemented by `kernel_to_common.c` for use by policy.conf/CIL emitters.

Important APIs and types: exposes `STACK_SIZE`, fallback MLS/object constants (`DEFAULT_LEVEL`, `DEFAULT_OBJECT`), `selinux_sid_to_str`, `xen_sid_to_str`, `SELINUX_SID_SZ`, `XEN_SID_SZ`, the ordered `avtab_flavors[]` list, `AVTAB_FLAVORS_SZ`, opaque `struct strs`, formatting helpers, string-list helpers, ebitmap/name conversion helpers, stack helpers, `isids_to_strs`, `sort_ocontexts`, and `check_for_supported_policy`.

Control flow: this file has no runtime control flow, but the static arrays determine output order and naming for callers. `avtab_flavors[]` fixes the order for access-vector and type-rule emission, while SID tables provide stable names for numeric initial SIDs that are not stored in binary policy packages.

State and persistence: the arrays are translation-unit-local because they are `static const` in the header; each including C file receives its own copy. There is no persistent state, but changing these constants changes generated policy text and ABI-adjacent behavior for converters.

Dependencies and integration points: includes `stdio.h`, `stdarg.h`, `sys/types.h`, libsepol `avtab.h`, and `policydb.h`. It is included by `kernel_to_common.c` and `kernel_to_conf.c`; sibling emitters depend on the same prototypes and tables.

Risks: because large static arrays live in a header, every includer has a private copy; this is intentional for internal helpers but would be unsuitable for public ABI. SID mappings must remain synchronized with Linux/Xen kernel initial SID numbering. Adding or reordering `avtab_flavors[]` changes output ordering and can affect golden tests.

Test signals: compile all converter translation units with format-attribute checking enabled, verify no duplicate-symbol linkage issues from header-local arrays, and compare generated policy.conf output against expected SID and AV rule ordering.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/kernel_to_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/kernel_to_conf.c -->
# sources/security-integrity/selinux/libsepol/src/kernel_to_conf.c

Purpose: converts an in-memory kernel `policydb` into checkpolicy-style `policy.conf` text. It serializes policy metadata, class/common/default rules, MLS declarations, constraints, booleans, types, attributes, TE/RBAC rules, users, initial SIDs, and SELinux/Xen object contexts.

Important APIs and functions: the exported entry point is `sepol_kernel_policydb_to_conf(FILE *out, struct policydb *pdb)`. Core helpers include `cond_expr_to_str`, `constraint_expr_to_str`, `constraint_rules_to_strs`, `validatetrans_rules_to_strs`, `write_handle_unknown_to_conf`, class/common/default writers, MLS writers (`write_sensitivity_rules_to_conf`, `write_category_rules_to_conf`, `write_level_rules_to_conf`), declaration writers for policycaps, attributes, booleans, types, aliases, bounds, permissive/neveraudit maps, AV-rule writers (`avtab_node_to_str`, `write_avtab_to_conf`, `write_cond_nodes_to_conf`), filename and range transition writers, RBAC/user writers, `context_to_str`, and SELinux/Xen ocontext writers.

Control flow: `sepol_kernel_policydb_to_conf` first calls `check_for_supported_policy`, initializes four string lists for MLS/non-MLS constraints and validatetrans rules, precomputes and sorts those rules, then emits sections in a stable order: handle_unknown comment, class and SID declarations, class/common bodies, default rules, MLS declarations, MLS constraints, policy capabilities, type/role/boolean/type-alias/bounds/attribute/permissive/neveraudit declarations, AV rules by flavor, filename transitions, range transitions for MLS, conditionals, roles, users, non-MLS constraints, and finally sorted platform-specific object contexts. It calls `sort_ocontexts(pdb)` before ocontext output.

State and persistence: no files are opened by this module; it writes to the caller-provided `FILE *`. It allocates transient strings and `struct strs` lists, mutates `pdb->ocontexts[]` ordering via `sort_ocontexts`, and otherwise reads policydb state. Output determinism depends on explicit sorting because many inputs are hashtabs.

Dependencies and integration points: includes public `sepol/kernel_to_conf.h`, policydb `avtab`, conditional, hashtab, polcaps, services, util APIs, `debug.h`, and `kernel_to_common.h`. It consumes libsepol policydb internals and formatting helpers, and it must stay consistent with binary policy semantics, CIL conversion, and checkpolicy syntax.

Risks: many helpers trust that value-to-name arrays are populated for referenced numeric IDs; malformed policies can trigger null dereferences unless caught earlier. `write_filename_trans_rules_to_conf` is called without checking its return value, so a filename transition serialization error can be lost. The conversion mutates ocontext order, which can surprise callers that expect original insertion order. String ownership is dense and error paths must free partially built values. Generated genfscon wildcard handling enforces the `genfs_seclabel_wildcard` policycap by requiring trailing `*`.

Test signals: golden-output tests should cover MLS and non-MLS policies, constraints and validatetrans expressions, all AVTAB flavors including xperms and dontaudit bit inversion, conditionals, long role type sets, aliases/bounds, default range variants, filename/range transitions, SELinux ocontexts (fsuse, genfscon, ports, netif, node/node6, ibpkey, ibendport), Xen ocontexts, unknown policycaps/protocols, and unsupported policy versions 20-23. Allocation-failure and malformed-policy tests should verify cleanup and error propagation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/kernel_to_conf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/libsepol.map.in -->
# sources/security-integrity/selinux/libsepol/src/libsepol.map.in

Purpose: linker version script template for libsepol. It declares the `LIBSEPOL_1.0` symbol version and controls which libsepol functions are exported from the shared library while hiding everything else as local.

Important APIs and symbols: exports the original `LIBSEPOL_1.0` public CIL, policydb, context/bool/user/port/node/iface/InfiniBand, MLS, module package, linking/expansion, and handle/message APIs, with `local: *;` hiding non-listed symbols in that base version. Later version blocks add newer APIs: `LIBSEPOL_1.1` includes CIL compile/build/write helpers and kernel/module conversion functions such as `sepol_kernel_policydb_to_conf`; `LIBSEPOL_3.0` adds policydb optimization and AST write/setter helpers; `LIBSEPOL_3.4` adds access-vector, SID, context, and transition validation services; `LIBSEPOL_3.6` adds post-AST writing; `LIBSEPOL_3.11` adds declaration-to-CIL and neverallow checking against policydb.

Control flow: there is no runtime logic. During the build, the linker consumes this template-derived script to assign symbol visibility and version metadata to the shared object.

State and persistence: affects persistent ABI of produced `libsepol.so`. Adding, removing, or renaming entries changes what downstream binaries can link against and what versioned symbols they require; placing a symbol in the wrong version block changes ABI compatibility even if the name is exported.

Dependencies and integration points: integrated by libsepol build rules, usually after configure/meson substitution for `.map.in` templates. It must match public headers and actual compiled definitions in `src/`.

Risks: missing a new public API here causes link failures or hidden symbols despite header declarations. Exporting internal helpers by mistake expands ABI surface permanently. Removing or changing an exported symbol is ABI-breaking for existing SELinux tooling.

Test signals: shared-library build should fail on undefined exported symbols when linker checks are enabled; ABI tests should compare exported symbol lists with expected baselines; downstream smoke tests should link representative tools against the generated library.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/libsepol.map.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/libsepol.pc.in -->
# sources/security-integrity/selinux/libsepol/src/libsepol.pc.in

Purpose: pkg-config template for libsepol consumers. It describes include and library flags needed to compile and link software against libsepol.

Important fields: `prefix`, `exec_prefix`, `libdir`, and `includedir` are substituted by the build/install system. `Name`, `Description`, `Version`, and `URL` identify the package. `Libs: -L${libdir} -lsepol` supplies linker flags, and `Cflags: -I${includedir}` supplies include flags.

Control flow: no runtime control flow. The template becomes `libsepol.pc` at install/configure time and is read by `pkg-config`.

State and persistence: persists as installed metadata. Incorrect substituted paths or version values affect all downstream builds using `pkg-config --cflags --libs libsepol`.

Dependencies and integration points: depends on build-system substitution for `@prefix@`, `@libdir@`, `@includedir@`, and `@VERSION@`. Used by package managers and external SELinux consumers.

Risks: stale version or install directories can make consumers build against the wrong headers or fail to find the library. The file intentionally does not list private libs; if libsepol gains additional public link dependencies, this template may need updates.

Test signals: after installation, run `pkg-config --modversion libsepol`, `pkg-config --cflags --libs libsepol`, and compile a minimal program including a public libsepol header and linking with the returned flags.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/libsepol.pc.in -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/link.c -->
# sources/security-integrity/selinux/libsepol/src/link.c

Purpose: implements libsepol module linking: merging one or more policy modules into a base policy while remapping all symbol values, permissions, declarations, rules, scope metadata, MLS semantic ranges, conditionals, and optional-block enablement.

Important APIs and types: exported entry point is `link_modules(sepol_handle_t *handle, policydb_t *b, policydb_t **mods, int len, int verbose)`. Internal `policy_module_t` stores the source policy plus symbol maps, avrule declaration maps, permission maps, and base placement; `link_state_t` carries the mutable linking context, current module, current declaration/class state, declaration-to-module mapping, and error handle; `missing_requirement_t` describes unmet requirements. Major phases are `prepare_module`, `prepare_base`, `copy_module`, `copy_identifiers`, symbol-specific copy callbacks, alias/bounds copy callbacks, bitmap fix callbacks, rule copy helpers, `copy_scope_index`, `enable_avrules`, and `cond_normalize`.

Control flow: `link_modules` validates that the target is a base policy and every input is a module with matching MLS mode, upgrades the base policy version if a module is newer, prepares per-module remap arrays and normalized conditionals, prepares the base declaration table, copies each module into the base, reindexes classes and other symbols, then enables avrules according to requirements. Copying is staged: first global identifiers and maps are created, then avrule blocks/declarations and local identifiers are copied, scope tables are merged, base indexes are rebuilt, and optional/global requirements determine which declarations remain enabled.

State and persistence: this is an in-memory mutator of the base `policydb_t`. It appends avrule blocks, inserts symbols into base hashtabs, expands `decl_val_to_struct`, updates `scope[]`, changes class permission tables for required-but-not-base-declared classes, merges role/type/user bitmaps, normalizes conditionals, and may raise the base policy version. It does not write files; callers such as `module.c` persist the resulting policy/package later.

Dependencies and integration points: depends on libsepol policydb internals, avrule blocks, conditionals, hashtabs, link headers, utility functions such as `is_id_enabled`, `is_perm_existent`, `add_i_to_a`, policydb indexing, and MLS semantic helpers from `mls.c`. `module.c` exposes this via `sepol_link_modules` and `sepol_link_packages`.

Risks: linking is highly order-dependent and contains many `assert(map[...])` assumptions after earlier copy phases; malformed modules or missed requirements can become aborts in debug builds. Permission scoping has documented limitations for optionals: a required missing permission on an existing class can force a requirement error even in an optional. Memory ownership is complex for partially copied rules, filename transitions, conditionals, and range transitions. The function mutates the base even if a later module fails, so callers needing rollback must clone first. `copy_filename_trans_list` can leak a partially linked rule on late failure.

Test signals: test base/module combinations for duplicate declarations, role/user multi-declarations, type aliases and self-alias rejection, bounds conflicts, boolean versus tunable mismatches, MLS/non-MLS mismatch, policy version upgrade, optional blocks with unmet requirements and else branches, class/permission remapping through commons, xperms, filename/range transitions, conditional expression remapping, and failure cleanup under allocation faults. Integration tests should link real policy modules and then expand/index/write the resulting base.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/link.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/mls.c -->
# sources/security-integrity/selinux/libsepol/src/mls.c

Purpose: implements Multi-Level Security support for libsepol contexts. It parses and prints MLS ranges, validates context ranges against policy sensitivity/category/user constraints, converts MLS values between policies, computes new object ranges for transitions, exposes public MLS check/contains APIs, and manages semantic MLS range helper structures.

Important APIs and functions: public/internal functions include `mls_to_string`, `mls_from_string`, deprecated string-context helpers `mls_compute_context_len`, `mls_sid_to_context`, `mls_context_to_sid`, validation via `mls_context_isvalid`, range setup via `mls_setup_user_range`, migration via `mls_convert_context`, transition computation via `mls_compute_sid`, public wrappers `sepol_mls_contains` and `sepol_mls_check`, and semantic object helpers `mls_semantic_cat_init/destroy`, `mls_semantic_level_init/destroy/cpy`, and `mls_semantic_range_init/destroy/cpy`.

Control flow: string output computes the required MLS length, writes a leading colon plus low/high levels, compresses consecutive categories into comma/dot ranges, and omits the high level when it equals low. Parsing tokenizes the caller-provided string in place on `:`, `-`, `,`, and `.`, maps sensitivity/category names through policy hashtabs, expands category ranges, and copies low to high if no high is supplied. Validation checks high dominates low, category membership is valid for each sensitivity, and non-object roles use users authorized for the range. `mls_compute_sid` applies explicit range transition rules first, then class default-range policy, then fallback behavior for transition/change/member rules.

State and persistence: no persistent storage. Functions mutate `context_struct_t` ebitmaps, caller string buffers during parsing, and semantic linked lists. Public wrappers allocate temporary contexts and destroy them before returning. Conversion destroys old category ebitmaps and replaces them with mapped ebitmaps.

Dependencies and integration points: depends on public and internal libsepol context/policydb/services headers, `handle.h`, `debug.h`, `private.h`, and `mls.h`. It is used by context parsing/printing, policy linking (`link.c` semantic MLS conversion), policy expansion/services, and public libsepol MLS APIs exported in the map file.

Risks: `mls_context_to_sid` modifies the input buffer and advances the pointer in non-obvious ways, so callers must pass writable storage. Several array lookups assume valid sensitivity/category values from policydb; corrupted contexts can underflow indexes before validation if used incorrectly. `mls_to_string` uses deprecated helpers and pointer rewinding after `mls_sid_to_context`, which is fragile. `mls_convert_context` can leak the temporary `bitmap` if an error occurs after bits are set but before assignment. Range computation correctness is security-sensitive because it controls labels for created/member objects.

Test signals: parse/print round trips for single levels, low-high ranges, category singleton/two-item/long ranges, invalid names, reversed category ranges, missing MLS components, and non-MLS policies. Validate dominance, sensitivity-category authorization, object role bypass, and user range authorization. Test transition defaults (`source low`, `source high`, `target low-high`, `glblub`), explicit range transitions, policy conversion with renamed/missing levels/categories, and public `sepol_mls_check`/`sepol_mls_contains` error paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/mls.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/mls.h -->
# sources/security-integrity/selinux/libsepol/src/mls.h

Purpose: internal MLS header declaring libsepol's MLS parsing, printing, validation, conversion, transition, and user-range setup functions for other policydb components.

Important APIs and types: declares `mls_from_string`, `mls_to_string`, deprecated `mls_compute_context_len`, `mls_sid_to_context`, and `mls_context_to_sid`, plus `mls_context_isvalid`, `mls_convert_context`, `mls_compute_sid`, and `mls_setup_user_range`. It references `sepol_handle_t`, `policydb_t`, `context_struct_t`, `user_datum_t`, and `sepol_security_class_t`.

Control flow: none directly; it defines the callable contract used by context and service code. The declarations distinguish modern string conversion wrappers from deprecated lower-level helpers retained for compatibility inside the library.

State and persistence: no state. The declared functions mutate caller-supplied contexts, writable string pointers, and MLS ranges as described by `mls.c`.

Dependencies and integration points: includes `policydb_internal.h`, public context and policydb headers, and `handle.h`. Used by MLS implementation clients including services, link/expand code, and context conversion paths.

Risks: exposing deprecated helper prototypes internally can perpetuate fragile pointer-buffer semantics. Any signature change would ripple through policydb services and ABI-adjacent internals, though the header itself is not the public installed API.

Test signals: compile coverage should ensure all declarations match definitions and callers. Behavioral tests belong to `mls.c` consumers: context string conversion, transition range computation, and policy conversion.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/mls.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/module.c -->
# sources/security-integrity/selinux/libsepol/src/module.c

Purpose: implements the public module package API for libsepol. It creates, frees, reads, writes, inspects, and links SELinux module packages that contain a policydb section plus optional file contexts, seusers, user_extra, and netfilter context sections.

Important APIs and functions: package lifecycle and accessors include `sepol_module_package_create`, `sepol_module_package_free`, `sepol_module_package_get_*`, `sepol_module_package_set_*`, and `sepol_module_package_get_policy`. Linking APIs are `sepol_link_packages`, `sepol_link_modules`, and `sepol_expand_module`. Serialization APIs are `sepol_module_package_read`, `sepol_module_package_info`, and `sepol_module_package_write`. Internal helpers include `policy_file_seek`, `policy_file_length`, `module_package_init`, `set_char`, `link_file_contexts`, `link_netfilter_contexts`, `read_helper`, `module_package_read_offsets`, and `write_helper`.

Control flow: creating a package allocates and initializes a policydb with package version 1. Reading first parses the package header and section offset table, validates magic and monotonic offsets, seeks to each section, reads known sections by magic, rejects duplicate known sections, ignores unknown section magics with an error log, and requires one policy module section. `sepol_module_package_info` performs a lighter scan to extract module type/name/version from the policy section. Writing first computes policy length with a `PF_LEN` policy file, counts optional sections, writes header and offsets, writes the policydb, then writes each present auxiliary section with its magic. Linking packages delegates policy linking to `link_modules`, then appends file and netfilter contexts into the base package.

State and persistence: package objects own heap buffers for auxiliary sections and a `sepol_policydb_t`. Read/write operate on `struct sepol_policy_file`, supporting stdio and memory-backed policy files. Linking mutates the base package policy and extends base auxiliary buffers. No global state is used.

Dependencies and integration points: depends on `policydb_internal.h`, `module_internal.h`, public policydb link/expand/module headers, low-level policy file I/O (`next_entry`, `put_entry`, endian conversion), `debug.h`, and `private.h`. `libsepol.map.in` exports this module package API. `link.c` and expand code provide the underlying policy merge/expansion behavior.

Risks: section offsets are bounded by `MAXSECTIONS` and monotonic checks, but malformed package data exercises many allocation and partial-read paths. `link_file_contexts` calls `realloc(base->file_contexts, fc_len)` and treats NULL as failure even when `fc_len` could be zero. The setters copy raw buffers without adding terminators, so callers must use length-aware accessors. `sepol_module_package_read` can leave partially populated fields on failure unless the caller frees the package. Package write uses fixed five-entry offset arrays, matching the current maximum section count; adding a section requires updating that storage.

Test signals: read/write round trips for base and module packages with each optional section, memory-backed and stdio-backed policy files, duplicate section rejection, missing policy section rejection, unknown section handling, truncated headers/offset arrays/sections, decreasing or out-of-file offsets, seusers/user_extra only allowed in base on write, package info for base and module types, package linking with auxiliary context concatenation, and expand/link failure code mapping.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/module.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/module_internal.h -->
# sources/security-integrity/selinux/libsepol/src/module_internal.h

Purpose: tiny internal shim header for module package implementation. It includes the public `<sepol/module.h>` declaration set for internal source files.

Important APIs and types: no new APIs or types are defined here; all visible declarations come from `<sepol/module.h>`, including `sepol_module_package_t` and module package function prototypes.

Control flow: none.

State and persistence: none.

Dependencies and integration points: used by `module.c` to pull in module package declarations through a local internal include path. It can serve as an extension point if libsepol later needs private module-package declarations without changing every source include.

Risks: the file has no include guard, but because it only includes a public header that should have its own guard, practical risk is low. Adding private declarations here should include a guard to avoid duplicate definition issues.

Test signals: compile-only coverage is sufficient; any future additions should be validated by the source files that include this shim.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/module_internal.h -->
