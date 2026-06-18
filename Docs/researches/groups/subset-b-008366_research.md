# Research: subset-b-008366

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/module_to_cil.c -->
# sources/security-integrity/selinux/libsepol/src/module_to_cil.c

## Purpose
Converts SELinux module/base policydb structures and module-package sidecar text blobs into CIL text. It is a formatter and semantic bridge: it walks policydb symbol tables, scopes, optional blocks, AV rules, role/range/file transitions, booleans/tunables, MLS data, object contexts, genfs contexts, policy capabilities, seusers, user_extra, and file_contexts, then emits CIL forms to a global `out_file`.

## Important APIs, Types, and Functions
Public entry points are `sepol_module_policydb_to_cil(FILE *, struct policydb *, int)`, `sepol_module_package_to_cil(FILE *, struct sepol_module_package *)`, and `sepol_ppfile_to_module_package(FILE *, struct sepol_module_package **)`. Internal helpers include output wrappers `cil_printf`/`cil_println`, scope helpers around `struct stack`, role/type alias gathering lists, type/role set conversion helpers, and many `*_to_cil` emitters. `func_to_cil[]` dispatches symbol kinds to class/role/type/user/boolean/sensitivity/category emitters.

## Control Flow
`sepol_module_policydb_to_cil()` validates base/module policy type, normalizes the module name, emits base-only defaults (`systemlow`, `object_r`, `cil_gen_require`, handleunknown, mls), builds role and typealias lookup lists, emits policycaps/object contexts/genfs contexts, and finally prints either unresolved module blocks (`blocks_to_cil`) or linked blocks (`linked_blocks_to_cil`). Block conversion pushes declarations on a scope stack, emits aliases and declared/required/additive symbols, then emits rules and generated attributes. Optional blocks are nested by comparing required-scope supersets; linked conversion chooses only enabled branches. `sepol_module_package_to_cil()` appends package sidecar conversions after policydb conversion.

## State and Persistence Behavior
State is transient except for output written to `FILE *out_file`. The converter mutates `pdb->name` for base policies or invalid CIL name characters, uses global caches `role_list` and `typealias_lists`, and cleans them at exit. It reads module-package buffers directly for seusers, netfilter contexts, user_extra, and file_contexts. It does not write binary policy, but it serializes a policydb/module-package view into CIL syntax.

## Dependencies and Integration Points
Depends on libsepol policydb data structures, hashtabs, ebitmaps, conditional policy, services permission string helpers, module package accessors, `kernel_to_common` SID helpers, tokenizer helpers from `private.h`, and system networking conversion functions. It integrates with the compiler/linker path that needs CIL output from `.pp` packages and with policydb version-specific structures already populated by the reader.

## Risks and Edge Cases
Output failures call `_exit(EXIT_FAILURE)`, which bypasses normal library cleanup. Unsupported constructs are dropped with warnings: fscon, netfilter_contexts, role dominance, and optional `else` branches. Non-trivial neverallow targets with `notself` are rejected. `search_attr_list()` appears to skip equal ebitmaps when `ebitmap_cmp(...) == 0`, which can prevent deduplication of generated attributes and inflate output. String parsing for package sidecars is strict and mutates token buffers. `fp_to_buffer()` doubles buffer size without an explicit overflow guard. Global `out_file` and global lists make the converter non-reentrant.

## Test Signals
Useful tests compare generated CIL for base, module, linked module, MLS/non-MLS, optional blocks, type aliases, xperms, genfs wildcard policycap, seusers/user_extra/file_contexts, and unsupported constructs. Regression tests should assert deterministic ordering for permission arrays, correct optional nesting, valid CIL for generated anonymous set attributes, proper cleanup on parse failures, and pipe/socket `.pp` input handling.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/module_to_cil.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/node_internal.h -->
# sources/security-integrity/selinux/libsepol/src/node_internal.h

## Purpose
Private include bridge for node record and node database APIs. It gives implementation files a single local header that includes the public high-level node record declarations and node policydb operation declarations.

## Important APIs, Types, and Functions
No new functions or types are declared here. It exposes whatever is provided by `<sepol/node_record.h>` and `<sepol/nodes.h>` to local implementation files such as `node_record.c` and `nodes.c`.

## Control Flow
There is no runtime control flow. The include guard `_SEPOL_NODE_INTERNAL_H_` prevents duplicate inclusion.

## State and Persistence Behavior
No runtime state or persistence. The file only affects compilation and dependency visibility.

## Dependencies and Integration Points
Integrates the record-level API (`sepol_node_t`, `sepol_node_key_t`) with policydb CRUD operations for node contexts. This local header keeps source files coupled to both public surfaces without repeating includes.

## Risks and Edge Cases
The header is intentionally minimal; any private helper prototypes added later would widen the internal ABI. Current risk is low, limited to include-order or missing-declaration problems if public headers change.

## Test Signals
Compilation of `node_record.c` and `nodes.c` is the main signal. Include hygiene tests should catch missing public declarations or circular include changes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/node_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/node_record.c -->
# sources/security-integrity/selinux/libsepol/src/node_record.c

## Purpose
Implements the high-level `sepol_node_t` and `sepol_node_key_t` record API for SELinux network node contexts. It owns conversion between textual IPv4/IPv6 addresses, binary address/mask bytes, protocol values, and attached `sepol_context_t` records.

## Important APIs, Types, and Functions
Defines private structs `sepol_node` and `sepol_node_key`, each carrying allocated address bytes, mask bytes, byte sizes, and protocol; nodes also own a cloned context. Key APIs include `sepol_node_key_create`, `sepol_node_key_extract`, `sepol_node_key_unpack`, `sepol_node_key_free`, `sepol_node_compare`, `sepol_node_compare2`, address/mask getters and setters in string and byte form, `sepol_node_get_proto`, `sepol_node_set_proto`, `sepol_node_get_proto_str`, `sepol_node_create`, `sepol_node_clone`, `sepol_node_free`, `sepol_node_get_con`, and `sepol_node_set_con`.

## Control Flow
String address creation routes through `node_alloc_addr()` for protocol-sized buffers, then `node_parse_addr()` with `inet_pton`. String getters allocate protocol-sized text buffers and call `node_expand_addr()` with `inet_ntop`. Byte setters/getters clone caller-provided buffers without validating protocol length. Clone/create/free paths consistently allocate deep copies and release owned context/address/mask memory.

## State and Persistence Behavior
All state is heap-owned by the record or key. Setters replace old address/mask/context only after allocating and parsing/cloning replacements. No policydb persistence occurs here; persistence happens when `nodes.c` converts records into `ocontext_t` lists.

## Dependencies and Integration Points
Uses `context_internal.h`/public context APIs for context cloning and freeing, `debug.h` for handle-scoped errors, libc allocation, and `inet_pton`/`inet_ntop` for canonical network conversion. The API feeds `nodes.c` policydb operations and callers of the public libsepol node-record interface.

## Risks and Edge Cases
Byte setters accept arbitrary sizes, so malformed callers can create records whose byte length does not match `proto`; later policydb conversion assumes 4 or 16 bytes. `sepol_node_compare*()` orders by mask comparison before address comparison when sizes match, which may be surprising if callers expect address-first ordering. Protocol setters do not resize existing address/mask buffers. Error messages call `sepol_node_get_proto_str()` and may show `???` for invalid protocols.

## Test Signals
Tests should cover IPv4/IPv6 parse/expand round trips, invalid address/protocol errors, deep clone independence, key extraction and comparison behavior, byte setter misuse, context ownership replacement, and cleanup under allocation failures.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/node_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/nodes.c -->
# sources/security-integrity/selinux/libsepol/src/nodes.c

## Purpose
Implements policydb operations for node contexts: count, exists, query, modify/add, and iterate. It bridges high-level `sepol_node_t` records to low-level `ocontext_t` entries in `policydb->ocontexts[OCON_NODE]` and `policydb->ocontexts[OCON_NODE6]`.

## Important APIs, Types, and Functions
Internal converters are `node_from_record()` and `node_to_record()`, using context conversion helpers. Public operations are `sepol_node_count`, `sepol_node_exists`, `sepol_node_query`, `sepol_node_modify`, and `sepol_node_iterate`.

## Control Flow
`node_from_record()` allocates an `ocontext_t`, clones binary address/mask from the record, stores them in IPv4 or IPv6 union fields based on protocol, converts the high-level context to a policydb `context_struct_t`, and returns ownership to the caller. `node_to_record()` does the reverse. Exists/query unpack the key and scan the matching IPv4 or IPv6 list with `memcmp`. Modify converts the record and prepends it to the matching list. Iterate walks IPv4 first, then IPv6, converts each low-level node to a record, calls the callback, and stops early on positive callback status.

## State and Persistence Behavior
The persistent policy state is the linked list inside `policydb_t`. `sepol_node_modify()` only prepends; it does not replace or remove an existing matching node even though it accepts a key. Query/exists see the first matching entry by list order. Contexts are copied into low-level policydb storage and freed through policydb destruction.

## Dependencies and Integration Points
Depends on `sepol/policydb/policydb.h` ocontext layout, record APIs from `node_internal.h`, and context conversion helpers from `context.h`. It integrates with binary policy read/write through the shared `ocontexts` arrays and with CIL conversion through nodecon emitters in `module_to_cil.c`.

## Risks and Edge Cases
`sepol_node_modify()` ignores key address/mask when building the stored node and only uses key protocol to choose the list, so callers can provide a key and data that disagree. Duplicate entries are possible because modify does not check existing entries. Byte lengths are assumed to be valid for protocol; malformed records can cause partial or overbroad `memcpy` into low-level fields. Callback errors during iteration abort after freeing the current record.

## Test Signals
Tests should cover IPv4/IPv6 count/query/exists, modify plus query round trip, duplicate modify behavior, key/data mismatch, callback early exit, callback error cleanup, and conversion of invalid protocol or malformed byte-size records.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/nodes.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/optimize.c -->
# sources/security-integrity/selinux/libsepol/src/optimize.c

## Purpose
Performs binary kernel policy optimization by removing AV and xperm rules that are covered by more general rules, preserving effective policy while reducing rule table size and potentially lookup cost.

## Important APIs, Types, and Functions
The public entry point is `policydb_optimize(policydb_t *p)`. Internal `struct type_vec` stores sorted type/attribute ids. `build_type_map()` maps each type or attribute to all attributes that are supersets of it. `process_avtab_datum()` subtracts covered permissions/xperms from a candidate datum. `is_avrule_redundant()`, `is_cond_rule_redundant()`, `optimize_avtab()`, `optimize_cond_av_list()`, and `optimize_cond_avtab()` remove redundant unconditional and conditional rules.

## Control Flow
`policydb_optimize()` accepts only kernel policies and rejects versions 20 through 23 where attribute gaps make optimization unsafe. It builds the type-map from `type_attr_map`/`attr_type_map`, removes redundant entries from `te_avtab`, then optimizes conditional true/false lists and removes corresponding nodes from `te_cond_avtab`. Redundancy checks search for a rule with the same class and kind whose source/target are equal or covering attributes; when a covering rule is found, covered bits are cleared from the candidate and the candidate is removed only when no bits remain.

## State and Persistence Behavior
The function mutates the in-memory policydb destructively: it unlinks `avtab` entries, frees xperm payloads, decrements `nel`, may remove empty conditional nodes, and adjusts conditional rule lists. It does not write the policy; persistence occurs only if callers later call policydb write/image functions.

## Dependencies and Integration Points
Requires a fully indexed and validated kernel `policydb_t` with populated `type_val_to_struct`, `type_attr_map`, `attr_type_map`, `te_avtab`, `te_cond_avtab`, and `cond_list`. Public API exposure comes through `sepol_policydb_optimize()` in `policydb_public.c`.

## Risks and Edge Cases
Optimization depends on sorted type vectors; `build_type_map()` appends ids in increasing loops, preserving binary-search assumptions. `process_avtab_datum()` intentionally mutates the candidate while testing coverage, so partial coverage can shrink a rule even when not fully redundant. AUDITDENY uses inverse bit logic and is sensitive to full-mask semantics. Conditional optimization moves attribute rules to the end to limit complexity, but still has nested scans. Unsupported policy versions return failure rather than leaving policy unchanged silently.

## Test Signals
Tests should compare access-vector equivalence before/after optimization, verify count reductions for redundant allow/audit/xperm rules, check partial permission subtraction, cover AUDITDENY inverse logic, verify conditional true/false deletion and empty conditional removal, and assert rejection for non-kernel and unsupported version ranges.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/optimize.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/polcaps.c -->
# sources/security-integrity/selinux/libsepol/src/polcaps.c

## Purpose
Maps SELinux policy capability numeric ids to CIL/kernel string names and back. This supports policy parsing, CIL generation, and callers that expose policy capabilities by name.

## Important APIs, Types, and Functions
`polcap_names[]` is an indexed table from `POLICYDB_CAP_*` enum values through `POLICYDB_CAP_MAX` to canonical strings. `sepol_polcap_getnum(const char *name)` performs case-insensitive lookup and returns the numeric capability or `-1`. `sepol_polcap_getname(unsigned int capnum)` returns the name or `NULL` for out-of-range or undefined slots.

## Control Flow
Name lookup linearly scans all possible capability slots, skips `NULL` entries, and compares with `strcasecmp`. Number lookup bounds-checks against `POLICYDB_CAP_MAX` and returns the table slot.

## State and Persistence Behavior
The mapping is static read-only process state. No allocation or persistence occurs. Binary persistence is handled elsewhere as ebitmap bits in `policydb->policycaps`; CIL conversion uses this file to emit names.

## Dependencies and Integration Points
Depends on `<sepol/policydb/polcaps.h>` for enum bounds and `<string.h>` for `strcasecmp`. `module_to_cil.c` calls `sepol_polcap_getname()` when emitting `(policycap ...)`, and parsers may call `sepol_polcap_getnum()`.

## Risks and Edge Cases
Adding a new `POLICYDB_CAP_*` requires updating this table or lookups will return `NULL`/`-1`. String matching is case-insensitive but does not normalize punctuation or aliases. Unknown set bits cause CIL conversion to fail when `getname()` returns `NULL`.

## Test Signals
Tests should assert every defined policycap enum has a non-null name, round-trip name-to-number-to-name for all entries, case-insensitive lookup, out-of-range `getname()` behavior, and failure behavior for unknown names.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/polcaps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb.c -->
# sources/security-integrity/selinux/libsepol/src/policydb.c

## Purpose
Core implementation of SELinux/Xen policy database lifecycle, indexing, binary reading, compatibility handling, symbol/scoping management, and destruction. It is the central deserializer and in-memory contract for libsepol policydb users.

## Important APIs, Types, and Functions
Key exported functions include `policydb_lookup_compat`, datum init/destroy helpers, `policydb_init`, `symtab_insert`, `type_set_cpy`, `type_set_or_eq`, `policydb_index_classes`, `policydb_index_bools`, `policydb_index_others`, `policydb_destroy`, `symtabs_destroy`, `scope_destroy`, `policydb_load_isids`, `avrule_read_list`, `policydb_read`, `policydb_reindex_users`, `policy_file_init`, `policydb_set_target_platform`, and `policydb_sort_ocontexts`. Static reader functions cover every serialized component: symbols, constraints, MLS levels/ranges, AV rules, filename/range/role transitions, ocontexts, genfs, scopes, and module blocks.

## Control Flow
`policydb_init()` creates symbol and scope tables, an initial global avrule block/declaration, object_r, AV tables, conditional policy state, filename/range transition hash tables, and ebitmaps. `policydb_read()` validates magic/string/version/config/table sizes, resolves compatibility info, reads optional module name/version and policy capability maps, reads symbol tables, indexes classes and other symbols, reads kernel AV/conditional/transition tables or module avrule blocks and scopes, reads ocontexts/genfs/range transitions, builds kernel type/attribute maps, and finally validates the policy. Destruction mirrors allocation through symbol destroy callbacks and specialized ocontext/genfs/transition cleanup.

## State and Persistence Behavior
This file owns the binary policy persistence format reader. Endianness is normalized with `le32_to_cpu`/`le64_to_cpu`, and many reads are version-gated by kernel/base/module policy version and target platform. In-memory persistent state includes hashtabs, ebitmaps, val-to-name/struct indexes, scope metadata, ocontext/genfs lists, transition tables, AV tables, role/user caches, and type/attribute maps. On read failure it returns `POLICYDB_ERROR`; callers are responsible for final cleanup unless specific helper paths clean partial objects.

## Dependencies and Integration Points
Integrates with policydb public wrappers, binary writer functions, conditional policy code, avtab, ebitmap, MLS helpers, expand/cache logic, policy validation, kernel/common target definitions, debug logging, and module/CIL conversion. `policydb_compat[]` is the compatibility matrix for serialized layout across policy versions and target platforms.

## Risks and Edge Cases
The reader is large and failure cleanup is uneven: many nested read errors return immediately after partial allocation, relying on later `policydb_destroy()` by callers. `symtab_insert()` comments that post-insert failures can leave inconsistent state. Version gates are numerous, so adding a policy feature requires coordinated updates to compatibility, read/write, validation, CIL conversion, and public bounds. Filename transition compact format validation prevents duplicate otypes or overlapping stypes, while compat mode intentionally ignores old duplicate rules. Scope reads reject symbols absent from symbol tables and zero/saturated decl lists. Kernel type_attr_map construction rejects attributes associated with attributes.

## Test Signals
High-value tests include binary policy corpus read/validate across min/max kernel and module versions, malformed length/count/bitmap fuzzing, duplicate symbol/scope/genfs/filename transition rejection, MLS and non-MLS context reads, SELinux versus Xen ocontext reads, role/user cache expansion, type/attribute map construction, round-trip read/write validation, and leak/error-path tests under allocation failure.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb_convert.c -->
# sources/security-integrity/selinux/libsepol/src/policydb_convert.c

## Purpose
Provides memory-image conversion helpers for policydbs: read a binary image into an initialized `policydb_t`, and write a `policydb_t` into a newly allocated memory image with verification.

## Important APIs, Types, and Functions
`policydb_from_image(sepol_handle_t *handle, void *data, size_t len, policydb_t *policydb)` wraps a memory-backed `policy_file_t` and calls `policydb_read`. `policydb_to_image(sepol_handle_t *handle, policydb_t *policydb, void **newdata, size_t *newlen)` runs `policydb_write` once in length-counting mode, allocates a buffer, writes into it, then verifies by reading the buffer into a temporary policydb.

## Control Flow
From-image initializes a `policy_file_t` as `PF_USE_MEMORY`, points it at caller memory, attaches the handle, and destroys the policydb on read failure before returning `STATUS_ERR`. To-image initializes `PF_LEN` to compute required size, switches to `PF_USE_MEMORY` with allocated storage, preserves original pointer/length because writing advances fields, writes the policy, then reinitializes the file view over the produced buffer and validates it with `policydb_read` into `tmp_policydb`.

## State and Persistence Behavior
The file is a persistence boundary between in-memory policydb state and serialized memory buffers. To-image transfers ownership of the allocated buffer to the caller only on success; on failure it frees the temporary buffer. Verification creates and destroys a temporary policydb. Error paths set `errno` to `EINVAL` for invalid policy/write/read failures and `ENOMEM` for temporary policydb initialization failure.

## Dependencies and Integration Points
Depends on `policy_file_init`, `policydb_read`, `policydb_write`, `policydb_init`, and `policydb_destroy`. Public wrappers in `policydb_public.c` expose these helpers as `sepol_policydb_from_image` and `sepol_policydb_to_image`.

## Risks and Edge Cases
If verification `policydb_read()` fails after `policydb_init(&tmp_policydb)` succeeds, the temporary policydb is not destroyed on that error path, creating a leak. From-image destroys the caller-supplied policydb on invalid image, which is important ownership behavior for callers. Zero-length images will fail in `policydb_read`; no precheck is done here. `policydb_to_image()` relies on writer length mode exactly matching writer memory mode.

## Test Signals
Tests should cover valid image read, invalid image cleanup and errno, write length computation, write/read verification, ownership of returned buffer, failure injection for allocation and write errors, and leak checks for verification failure paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb_convert.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb_internal.h -->
# sources/security-integrity/selinux/libsepol/src/policydb_internal.h

## Purpose
Small private header that includes the public policydb API and exposes `policydb_target_strings[]` to internal source files needing target platform names.

## Important APIs, Types, and Functions
Declares `extern const char *const policydb_target_strings[];`, which is defined in `policydb.c` and indexed by target platform ids such as SELinux and Xen.

## Control Flow
No runtime control flow; only include guard `_SEPOL_POLICYDB_INTERNAL_H_`.

## State and Persistence Behavior
No owned state. It declares read-only global string storage owned by `policydb.c`.

## Dependencies and Integration Points
Includes `<sepol/policydb.h>` and is used by wrappers or helpers that need internal access to target platform display strings without depending directly on `policydb.c`.

## Risks and Edge Cases
The declaration exposes a global array without its size; callers must use valid target platform indexes and should rely on policydb bounds helpers where possible. Any change to target platform enum ordering must keep the definition in sync.

## Test Signals
Compilation and linker resolution are primary. Runtime tests that report target platform names through xperm or read errors indirectly cover this declaration.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb_public.c -->
# sources/security-integrity/selinux/libsepol/src/policydb_public.c

## Purpose
Implements the public libsepol wrapper API for policy files and policydb objects. It hides internal `policy_file_t`/`policydb_t` layout behind `sepol_policy_file_t` and `sepol_policydb_t` handles.

## Important APIs, Types, and Functions
Policy-file APIs: `sepol_policy_file_create`, `sepol_policy_file_set_mem`, `sepol_policy_file_set_fp`, `sepol_policy_file_get_len`, `sepol_policy_file_set_handle`, and `sepol_policy_file_free`. Policydb APIs: `sepol_policydb_create`, `sepol_policydb_free`, version bounds accessors, `sepol_policydb_set_typevers`, `sepol_policydb_set_vers`, `sepol_policydb_set_handle_unknown`, `sepol_policydb_set_target_platform`, `sepol_policydb_optimize`, `sepol_policydb_read`, `sepol_policydb_write`, `sepol_policydb_from_image`, `sepol_policydb_to_image`, `sepol_policydb_mls_enabled`, and `sepol_policydb_compat_net`.

## Control Flow
Creation allocates wrappers and initializes internal structures. File setters configure backing mode as memory, stdio, or length-counting mode when memory length is zero. Version/type setters validate requested values against kernel or module min/max ranges. Read/write/optimize/image functions delegate to internal policydb functions. `sepol_policydb_compat_net()` checks for absence of the `packet` class to enable older network-check compatibility mode.

## State and Persistence Behavior
Wrappers own their internal policydb and must be freed with `sepol_policydb_free()`. `sepol_policy_file_set_mem()` does not copy caller memory; it stores the pointer and length. `sepol_policy_file_get_len()` only succeeds after length-counting writes. Read/write persist through the configured policy file mode, and image conversion allocates caller-owned output buffers on success.

## Dependencies and Integration Points
Depends on `policydb_internal.h` for public structures and internal helpers, `debug.h`, policydb read/write/convert/optimize implementations, and hashtab lookup for compatibility mode. This is the stable C API layer used by external libsepol consumers.

## Risks and Edge Cases
`sepol_policy_file_set_mem(..., len=0)` switches to `PF_LEN`, which is a non-obvious overload: a zero-length memory input cannot be represented by this wrapper. The wrappers do little null checking beyond create/free. Callers must set policy type before `sepol_policydb_set_vers()` or version validation fails. `sepol_policydb_set_typevers()` sets max version as a side effect.

## Test Signals
API tests should cover create/free, memory and stdio read/write paths, length-counting writes and `get_len`, type/version validation, handle_unknown and target validation, optimize delegation, image round trip, MLS query, and `compat_net` behavior with and without a `packet` class.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb_public.c -->
