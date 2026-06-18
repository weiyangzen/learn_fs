# subset-b-008367 research

Grouped research report for SELinux `libsepol` validation, serialization, services, record wrappers, and tests. Each section preserves the source path for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb_validate.c -->
## sources/security-integrity/selinux/libsepol/src/policydb_validate.c

### Purpose
`policydb_validate.c` is the structural integrity pass for an in-memory `policydb_t`. It rejects malformed or internally inconsistent policy databases before they are trusted by serialization, expansion, or service APIs. It covers both kernel policies and base/module policies and validates version-dependent structures such as conditional rules, filename transitions, policy capabilities, permissive/neveraudit maps, range transitions, and type/attribute maps.

### Important APIs, types, and functions
The exported functions are `value_isvalid()` and `policydb_validate()`. Internal validation state is carried by `validate_t`, which records a symbol table's primitive count and an ebitmap of value gaps derived from `*_val_to_name` arrays. `map_arg_t` packages `validate_t` arrays with a handle and policy for hash-table callbacks. `perm_arg_t` detects duplicated or inherited permission values.

Major helper families include value and bitmap validators (`validate_value`, `validate_ebitmap`, `validate_type_set`, `validate_role_set`), symbol datum validators (`validate_common_datum`, `validate_class_datum`, `validate_role_datum`, `validate_type_datum`, `validate_user_datum`, `validate_bool_datum`, `validate_level_datum`), rule validators (`validate_avtab`, `validate_cond_list`, `validate_avrules`, `validate_role_transes`, `validate_filename_trans_hashtab`, module rule-list validators), and object/context validators (`validate_context`, `validate_ocontexts`, `validate_genfs`).

### Control flow
`policydb_validate()` initializes all `validate_t` flavors from policy symbol arrays, validates policy properties and policy capabilities, then branches by `policy_type`. Kernel policydbs validate the TE avtab, conditionals, role transitions/allows, and filename transitions. Base/module policydbs validate `avrule_block_t` declarations and their scopes, rule lists, and per-declaration symbol tables. Both paths then validate object contexts, genfs entries, scopes, datum array gaps and entries, permissive/neveraudit maps, range transitions, and kernel-only type/attribute maps. Every failure reports through `ERR(handle, ...)`, destroys gap bitmaps, and returns `-1`.

### State and persistence behavior
The file does not persist state; it reads policydb structures in place and allocates temporary gap ebitmaps. It assumes value arrays, hashtabs, ebitmaps, linked rule lists, and context structures already exist. Gap handling is version-aware: kernel policy versions between `POLICYDB_VERSION_AVTAB` and `POLICYDB_VERSION_PERMISSIVE` treat type gaps specially because attributes may live only in `type_attr_map`.

### Dependencies and integration points
It depends on policydb core types, ebitmap operations, conditional expressions, policy capability names, `policydb_has_cond_xperms_feature()`, and platform constants for SELinux/Xen. It is a guardrail for readers/writers and higher-level services: invalid symbol values, invalid context references, unsupported xperms, malformed constraint RPN, or mismatched reverse lookup arrays are caught here instead of later in access decisions or binary output.

### Risks and edge cases
The validator is sensitive to one-based policy values versus zero-based arrays; most checks subtract one only after `validate_value()`. Constraint and conditional expressions are checked as stack programs with maximum depth and final depth validation. Extended permissions are only accepted on SELinux and conditionally only on policies with conditional xperms support. Access-vector checks require at least one valid permission bit, while old compiler wildcard behavior is tolerated only by masking to class permission count. A notable risk is that any structure added to `policydb_t` must be wired here or malformed instances may bypass validation.

### Test signals
Indirect coverage comes from policy read/write, downgrade, conditional, expander, linker, neverallow, and MLS test suites in `libsepol/tests`. Useful focused tests would corrupt symbol gaps, invalid bounds, malformed RPN constraints, unsupported xperms in Xen or old policy versions, bad ocontext ranges, and module scope indices, then assert `policydb_validate()` fails with `-1`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb_validate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb_validate.h -->
## sources/security-integrity/selinux/libsepol/src/policydb_validate.h

### Purpose
This small internal header exposes policydb validation entrypoints to other libsepol compilation units.

### Important APIs
It declares `int value_isvalid(uint32_t value, uint32_t nprim);` for generic one-based symbol value checks and `int policydb_validate(sepol_handle_t *handle, const policydb_t *p);` for full policydb integrity validation.

### Dependencies and integration
The header includes `<stdint.h>`, `<sepol/handle.h>`, and `<sepol/policydb/policydb.h>`, tying callers to libsepol handles and policydb definitions. It is intentionally narrow and has no include guard in the viewed source, so repeated inclusion relies on external include patterns.

### Risks and test signals
The absence of a guard is low risk because declarations are idempotent, but it is inconsistent with sibling internal headers. Compile coverage is the main test signal; semantic coverage comes through callers of `policydb_validate()`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/policydb_validate.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/port_internal.h -->
## sources/security-integrity/selinux/libsepol/src/port_internal.h

### Purpose
`port_internal.h` is an internal aggregation header for the public port record and port collection APIs used by libsepol implementation files.

### Important APIs and dependencies
It exposes declarations from `<sepol/port_record.h>` and `<sepol/ports.h>` behind `_SEPOL_PORT_INTERNAL_H_`. No new types or functions are defined here.

### Integration and risks
`port_record.c` and `ports.c` include this file to share opaque `sepol_port_t` and `sepol_port_key_t` API declarations. Its main risk is dependency hygiene: it does not provide implementation contracts beyond the included public headers.

### Test signals
Build coverage of port record and port policydb APIs verifies this header. Runtime behavior is exercised through `sepol_port_*` tests if present in higher-level suites.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/port_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/port_record.c -->
## sources/security-integrity/selinux/libsepol/src/port_record.c

### Purpose
`port_record.c` implements the opaque high-level `sepol_port_t` and `sepol_port_key_t` records used by callers to create, compare, clone, and carry SELinux port-context mappings without directly touching `policydb_t` object contexts.

### Important APIs and types
`struct sepol_port` stores low/high port numbers, a libsepol protocol enum, and an owned `sepol_context_t *`. `struct sepol_port_key` stores the comparable range/protocol tuple. Public functions create, unpack, extract, compare, and free keys; get/set ranges and protocol; stringify protocols; create/clone/free records; and get/set cloned contexts.

### Control flow and state
All setters update the record in memory only. `sepol_port_set_con()` deep-clones the supplied context before replacing the existing one. `sepol_port_clone()` creates a new record, copies scalar fields, and clones the context if present. Comparators sort by low port, high port, then protocol.

### Dependencies and integration
The file depends on `context_internal.h` for context cloning/freeing and `debug.h` for `ERR()` messages. `ports.c` consumes these records to translate between public records and `ocontext_t` entries in `policydb->ocontexts[OCON_PORT]`.

### Risks and edge cases
There is no validation that port numbers are within 0-65535 or that low is less than high; policydb insertion code performs the low/high ordering check. Unknown protocols stringify as `"???"`, which is useful for diagnostics but can hide validation mistakes if callers do not check errors elsewhere.

### Test signals
Focused tests should cover deep clone ownership, replacing contexts, duplicate role-free behavior, comparator ordering, invalid protocol strings in diagnostics, and port range validation in `ports.c`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/port_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ports.c -->
## sources/security-integrity/selinux/libsepol/src/ports.c

### Purpose
`ports.c` maps high-level `sepol_port_t` records to and from low-level SELinux `OCON_PORT` object contexts in a `policydb_t`.

### Important APIs and functions
Internal conversion helpers are `sepol2ipproto()`, `ipproto2sepol()`, `port_from_record()`, and `port_to_record()`. Public API functions include `sepol_port_count()`, `sepol_port_exists()`, `sepol_port_query()`, `sepol_port_modify()`, and `sepol_port_iterate()`.

### Control flow
Queries unpack a port key, convert the libsepol protocol enum to the corresponding `IPPROTO_*`, then linearly scan `policydb->ocontexts[OCON_PORT]` for an exact protocol/low/high match. `sepol_port_modify()` converts the input record into a newly allocated `ocontext_t`, validates range ordering, converts the context record into `context_struct_t`, and prepends the object context to the port list. Iteration converts each `ocontext_t` back to a public record, calls the user callback, frees the temporary record, and stops early if the callback returns positive.

### State and persistence behavior
State is stored only in the in-memory `policydb_t` object-context list. Persistence happens later through `write.c` object context serialization. `sepol_port_modify()` does not replace or remove matching entries; it prepends a new mapping, so duplicate keys are possible unless the caller checks existence.

### Dependencies and integration
The file depends on socket protocol constants, `context_from_record()`/`context_to_record()`, libsepol handle diagnostics, and `port_record.c` APIs. It integrates with runtime SID lookup in `services.c`, where `sepol_port_sid()` scans the same `OCON_PORT` list by protocol and range.

### Risks and edge cases
Unsupported protocols produce `STATUS_ERR`. DCCP/SCTP constants are defined locally if missing from system headers. Duplicate port mappings can affect first-match behavior in services because modify prepends. Error handling must destroy partially converted contexts to avoid leaks.

### Test signals
Tests should cover protocol conversion, invalid protocol rejection, low > high rejection, query not found returning `NULL`, callback early stop, and duplicate insertion ordering effects on later SID resolution.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/private.h -->
## sources/security-integrity/selinux/libsepol/src/private.h

### Purpose
`private.h` centralizes libsepol internal portability helpers for endian conversion, array sizing, overflow-safe input accounting, compatibility lookup, policy-file I/O helpers, and `reallocarray()` fallback.

### Important definitions
Endian macros convert CPU values to/from little-endian 16/32/64-bit policy encoding. `ARRAY_SIZE`, `min`, `max`, `spaceship_cmp`, `is_saturated`, and `zero_or_saturated` are utility macros. `exceeds_available_bytes()` checks whether an element count and size would exceed remaining memory-backed policy input and handles multiplication overflow. `ignore_unsigned_overflow_` annotates intentional hash overflows for Clang UBSAN.

### Integration
`services.c` implements `next_entry()`, `put_entry()`, and `str_read()` declared here. `write.c`, `symtab.c`, and read-side code use the endian and overflow helpers. `policydb_lookup_compat()` is consumed by binary read/write logic to choose version/platform layout.

### Risks and edge cases
The macros evaluate arguments more than once for `min`/`max`, so side effects are unsafe. `exceeds_available_bytes()` protects only `PF_USE_MEMORY`; stdio callers rely on `fread()` failure. The local `reallocarray()` fallback is important for overflow safety on platforms without the libc function.

### Test signals
Cross-endian build or emulation, memory-backed short input tests, oversized string/count tests, and UBSAN builds exercise this header indirectly.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/private.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/services.c -->
## sources/security-integrity/selinux/libsepol/src/services.c

### Purpose
`services.c` implements libsepol security services over a global active `policydb_t` and `sidtab_t`: access-vector computation, transition SID computation, context/SID conversion, policy reload, object SID lookup, user SID enumeration, and policy-file read/write primitives.

### Important APIs and functions
State setters are `sepol_set_sidtab()`, `sepol_set_policydb()`, and `sepol_set_policydb_from_file()`. Access APIs include `sepol_compute_av_reason()`, `sepol_compute_av_reason_buffer()`, `sepol_compute_av()`, and `sepol_validate_transition_reason_buffer()`. Conversion APIs include `sepol_string_to_security_class()`, `sepol_string_to_av_perm()`, `sepol_av_perm_to_string()`, `sepol_sid_to_context()`, and `sepol_context_to_sid()`. SID derivation APIs include `sepol_transition_sid()`, `sepol_member_sid()`, and `sepol_change_sid()`. Object lookup APIs include `sepol_fs_sid()`, `sepol_port_sid()`, `sepol_netif_sid()`, `sepol_node_sid()`, `sepol_genfs_sid()`, `sepol_fs_use()`, `sepol_ibpkey_sid()`, and `sepol_ibendport_sid()`. Binary I/O helpers are `next_entry()`, `put_entry()`, and `str_read()`.

### Control flow
Access-vector computation looks up source and target contexts from the SID table, initializes `sepol_av_decision`, scans source and target type-attribute maps against `te_avtab`, applies conditional avtab decisions, evaluates constraints/MLS constraints, checks process role transitions, and finally applies type-bound masking. Constraint reason-buffer generation evaluates RPN constraint expressions while collecting readable infix diagnostics. SID computation starts with default user/role/type rules, applies type transition/member/change avtab rules, applies role transitions for process transitions, delegates MLS range handling to `mls_compute_sid()`, validates the context, and interns it in the SID table.

### State and persistence behavior
The file owns static defaults `mypolicydb` and `mysidtab` and global pointers `policydb` and `sidtab`, so the service layer is process-global rather than per-handle. `sepol_load_policy()` reads a new policy from memory, verifies class/permission compatibility, clones and converts existing SIDs, swaps the active policydb and SID table, and frees old state. Object SID lookups cache computed SIDs in `ocontext_t->sid[]` fields. `put_entry()` supports stdio output, memory output, and length-counting mode (`PF_LEN`).

### Dependencies and integration
This file depends on policydb, sidtab, conditional policy, MLS helpers, context conversion, avtab operations, and private policy-file helpers. It is the read/write bridge for `policydb_read()` and `policydb_write()` via `next_entry()` and `put_entry()`. It uses `services.h` public contracts and supplies behavior analogous to kernel SELinux services for offline policy tooling.

### Risks and edge cases
Global mutable service state is not thread-isolated; `latest_granting` and reason-buffer globals are shared. Stack helpers for reason strings dynamically resize but are global. Invalid SIDs remap through sidtab search to unlabeled when possible. `str_read()` assigns the allocated string before `next_entry()` succeeds, so callers must handle failure ownership carefully. Policy reload shuts down the old sidtab before clone/conversion and removes contexts that fail conversion unless enforcing causes hard errors.

### Test signals
Existing test suites cover conditionals, downgrade, expansion, linker behavior, and MLS/non-MLS runs. Additional high-value tests include reason-buffer resizing, invalid class/permission conversion, class compatibility failure on policy reload, memory-backed short reads/writes, SID caching for object contexts, IPv4/IPv6 node matching, and permissive handling of invalid contexts when enforcing is disabled.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/services.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/sidtab.c -->
## sources/security-integrity/selinux/libsepol/src/sidtab.c

### Purpose
`sidtab.c` implements the SID-to-context table used by libsepol services to resolve, intern, enumerate, convert, and destroy security IDs.

### Important APIs and functions
The public functions are `sepol_sidtab_init()`, `sepol_sidtab_insert()`, `sepol_sidtab_search()`, `sepol_sidtab_map()`, `sepol_sidtab_map_remove_on_error()`, `sepol_sidtab_context_to_sid()`, `sepol_sidtab_hash_eval()`, `sepol_sidtab_destroy()`, `sepol_sidtab_set()`, and `sepol_sidtab_shutdown()`.

### Control flow and state
The table is a fixed-size hash array indexed by `sid & SIDTAB_HASH_MASK`; each bucket is sorted by SID. Insert rejects duplicate SIDs and deep-copies contexts. Search returns the matching context or remaps unknown SIDs to `SECINITSID_UNLABELED` if that SID exists. `context_to_sid()` performs a full-table context scan, then allocates `next_sid` and inserts a new entry unless the table is shutdown or exhausted. Map-remove deletes nodes for which the callback returns nonzero.

### Dependencies and integration
The implementation depends on context copy/compare/destroy helpers and Flask initial SID constants. `services.c` uses it for all SID lookups, policy reload conversion, and object/context SID interning.

### Risks and edge cases
Lock macros are currently empty, so the apparent double-check locking in `context_to_sid()` is not real synchronization in this build. Full-table context search is O(number of SIDs). `sepol_sidtab_set()` transfers pointers without deep copy, so ownership must be clear to avoid double frees or leaks. Unknown SID remapping can mask caller mistakes if unlabeled exists.

### Test signals
Tests should cover duplicate insert `-EEXIST`, remap to unlabeled, SID allocation after explicit insert, shutdown preventing allocation, map-remove deletion and count updates, and ownership transfer during policy reload.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/sidtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/symtab.c -->
## sources/security-integrity/selinux/libsepol/src/symtab.c

### Purpose
`symtab.c` wraps generic hashtable creation/destruction for policy symbol tables.

### Important APIs
`symtab_init()` creates a `hashtab_t` using `symhash()` and `symcmp()` and sets `nprim` to zero. `symtab_destroy()` destroys the underlying table if present. `symhash()` is a djb2-style XOR hash and masks by `h->size - 1`; `symcmp()` is `strcmp`.

### Dependencies and integration
It depends on libsepol hashtab and symtab definitions plus `ignore_unsigned_overflow_` from `private.h`. Policydb symbol arrays for commons, classes, roles, types, users, booleans, sensitivities, and categories are built on this abstraction.

### Risks and edge cases
The hash mask assumes table size is a power of two. Hash overflow is intentional and annotated for UBSAN. Destroy does not null `s->table`, so callers that reuse a symtab after destroy must reinitialize it.

### Test signals
Compile/UBSAN builds, symbol insertion/search through policy parsing, and policydb destroy paths exercise this file.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/symtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/user_internal.h -->
## sources/security-integrity/selinux/libsepol/src/user_internal.h

### Purpose
`user_internal.h` is the internal aggregation header for SELinux user record and collection APIs.

### Important APIs and dependencies
It includes `<sepol/user_record.h>` and `<sepol/users.h>` behind `_SEPOL_USER_INTERNAL_H_`. It defines no additional functions or types.

### Integration and risks
`user_record.c` and `users.c` use it to share the public opaque user API declarations. Its risk profile is minimal; dependency correctness is verified at build time.

### Test signals
Build coverage of user record and policydb user management APIs is the primary signal.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/user_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/user_record.c -->
## sources/security-integrity/selinux/libsepol/src/user_record.c

### Purpose
`user_record.c` implements opaque high-level SELinux user records and keys, including names, MLS default level/range strings, and role-name arrays.

### Important APIs and types
`struct sepol_user` owns `name`, `mls_level`, `mls_range`, a dynamic `roles` array, and `num_roles`. `struct sepol_user_key` owns a user name. APIs create/unpack/extract/free keys; compare records by name; get/set name and MLS strings; add, test, set, get, and delete roles; create, clone, and free user records.

### Control flow and state
All fields are heap-owned and deep-copied on setters and clone. `sepol_user_add_role()` is idempotent for existing roles and grows the role array with `reallocarray()`. `sepol_user_set_roles()` copies a full replacement array before swapping it into the object. `sepol_user_get_roles()` returns a newly allocated array of borrowed role string pointers.

### Dependencies and integration
The file uses `private.h` for `reallocarray()` fallback and `debug.h` for diagnostics. `users.c` converts these public records into `user_datum_t` entries and back.

### Risks and edge cases
`sepol_user_del_role()` compacts by moving the last role into the removed slot and does not shrink allocation. In `sepol_user_add_role()`, freeing `roles_realloc` on failure is safe only when it is a newly allocated pointer not installed; after successful `reallocarray`, ownership transfer is handled before any later failure. MLS strings are not parsed here; validation is deferred to `users.c`.

### Test signals
Focused tests should cover clone independence, idempotent role add, role deletion ordering, returned role-array ownership, MLS string setters, and key extraction for records without names.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/user_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/users.c -->
## sources/security-integrity/selinux/libsepol/src/users.c

### Purpose
`users.c` translates high-level `sepol_user_t` records to and from `policydb_t` user datums and implements user query/modify/count/iterate APIs.

### Important APIs and functions
Internal `user_to_record()` converts a `user_datum_t` by index into a public record, including role names and MLS strings. Public APIs are `sepol_user_modify()`, `sepol_user_exists()`, `sepol_user_count()`, `sepol_user_query()`, and `sepol_user_iterate()`.

### Control flow
Modify unpacks the key and input roles, finds or creates `user_datum_t`, resets existing datums while preserving numeric value, validates each role name, expands dominated roles into the user role set, parses MLS default/range strings when MLS is enabled, rejects MLS strings when MLS is disabled, and for new users grows reverse lookup arrays, inserts the hashtable entry, and expands the role set cache. Query and iteration convert internal users back into records with `user_to_record()`.

### State and persistence behavior
The file mutates `policydb->p_users`, `user_val_to_struct`, `p_user_val_to_name`, role bitmaps, MLS ranges, and per-user caches. Persistence is indirect through `write.c` symbol-table serialization. Existing user modifications destroy and reinitialize the datum in place, preserving the stable value.

### Dependencies and integration
It depends on hashtab, ebitmap role maps, role expansion, MLS parsing/formatting, and user record APIs. It is the user-management peer to `ports.c` and feeds policydb validation and writing paths.

### Risks and edge cases
Error logging in the final `err` path uses `name`, which is often `NULL` for existing users; diagnostics may be less useful than `cname`. For new users, partial growth of reverse arrays before insertion must be handled carefully. Role expansion is only performed in the new-user path; existing-user cache correctness depends on destroy/init and later consumers. MLS parsing requires valid context fragments and can fail with allocated temporary context state.

### Test signals
Tests should cover adding new users, modifying existing users, undefined roles, MLS enabled without MLS fields, MLS disabled with MLS fields, reverse lookup array updates, query conversion back to strings, and iteration callback stop/error behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/users.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/util.c -->
## sources/security-integrity/selinux/libsepol/src/util.c

### Purpose
`util.c` contains general libsepol utilities for dynamic integer arrays, formatting access vectors and extended permissions, and tokenizing strings without `sscanf`.

### Important APIs and functions
`add_i_to_a()` appends a `uint32_t` to a dynamically resized array. `sepol_av_to_string()` formats permission bits for a class by mapping permission values back to names across class-specific and common permissions. `sepol_extended_perms_to_string()` formats xperm ioctl or netlink bitmaps as ranges. `tokenize()` splits a line into a fixed number of allocated fields using `tokenize_str()`.

### Control flow and state
Formatting functions grow heap buffers by retrying after `realloc()` when `snprintf()` would overflow. `sepol_av_to_string()` walks permission bit positions and uses `hashtab_map()` with `perm_name()` to find the matching symbol name. Extended permission formatting compresses adjacent bits into ranges and handles driver/function modes differently. `tokenize()` allocates each requested token and leaves the final argument as the remainder of the string.

### Dependencies and integration
Access-vector formatting is used by services diagnostics and likely by user-facing tools. The file depends on policydb class structures, hashtab mapping, xperm test macros, and `private.h` for `reallocarray()`.

### Risks and edge cases
`add_i_to_a()` reallocates on every append and resets `*cnt` to zero when `*a` is `NULL`. Callers own all token strings from `tokenize()`, including partial outputs on failure. `sepol_av_to_string()` assumes a valid class index. Extended permission formatting returns `NULL` for unsupported xperm kinds.

### Test signals
Good tests include formatting common and class-specific permissions, empty permission vectors, long permission names causing resize, xperm singleton/range compression, tokenization with whitespace and explicit delimiters, and allocation-failure paths under fault injection.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/util.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/write.c -->
## sources/security-integrity/selinux/libsepol/src/write.c

### Purpose
`write.c` serializes an in-memory `policydb_t` into the binary policy formats used for kernel policies and base/module policies. It is the persistence counterpart to policydb read logic and is heavily version- and platform-gated.

### Important APIs, types, and functions
The exported entrypoint is `policydb_write(policydb_t *p, struct policy_file *fp)`. `struct policy_data` packages the target `policy_file` and policydb for hash callbacks. Major helpers serialize ebitmaps, avtabs, MLS levels/ranges, symbol datums, constraints, conditionals, contexts, object contexts, genfs entries, range transitions, module avrules, scope indices, declarations, and blocks. `write_f[SYM_NUM]` maps symbol table kinds to their datum writers.

### Control flow
`policydb_write()` rejects unsupported formats, builds the config flags, writes magic/string/version/config/symbol/object-context counts, writes module name/version when needed, writes policycaps and kernel permissive/neveraudit maps, serializes all symbol tables with version-specific item counts, then branches by policy type. Kernel policies write avtab, conditionals, role transitions/allows, and filename transitions. Module/base policies write avrule blocks and scope tables. Both paths write platform object contexts, genfs entries, applicable range transitions, and kernel type-attribute maps.

### State and persistence behavior
All data is written through `put_entry()`, which supports stdio, memory, and length-only policy files. Scalar fields are little-endian encoded with `cpu_to_le*()`. The writer may omit or warn about fields unsupported by the target policy version, such as role attributes, type attributes in old kernel policy, non-process role/range transitions in old formats, booleans in old policies, permissive/neveraudit maps, GLBLUB defaults, filename transitions, and xperms.

### Dependencies and integration
It depends on `private.h` endian/I/O helpers, ebitmap, avtab, conditional policy, expand helpers for old avtab formats, MLS serialization, policy compatibility lookup, and diagnostic macros. It must remain aligned with `policydb_validate.c` and read-side binary layout.

### Risks and edge cases
Downgrade paths intentionally discard data with warnings; callers must treat those warnings as semantic loss. Old avtab writing expands attributes and merges nodes, using `merged` flags that must be reset. Extended permissions are rejected for old versions, conditional policies without xperm support, and non-SELinux targets. Object-context serialization differs sharply between SELinux and Xen and preserves network-order address fields. Buffer counts must match actual emitted entries or readers will desynchronize.

### Test signals
Existing downgrade and policy test suites are directly relevant. High-value tests include write/read round trips for kernel and module policies, old-version downgrade warnings, xperm rejection, object context SELinux/Xen layouts, filename transition compact and compat formats, MLS semantic versus expanded user data, and `PF_LEN` length calculation matching actual output.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/write.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/Makefile -->
## sources/security-integrity/selinux/libsepol/tests/Makefile

### Purpose
The test Makefile builds and runs the libsepol CUnit test binary and generates standard/MLS policy fixtures from source policy fragments.

### Important targets and variables
`EXE` defaults to `libsepol-tests`. `LIBSEPOL` points to `../src/libsepol.a` for static linkage against internal functions. `CHECKPOLICY` supplies parser objects from `../../checkpolicy/`. `all` builds the test binary and generated policies, `policies` builds policy fixtures, `clean` removes objects/binaries/generated policies, and `test` creates downgrade output directories, builds a reference policy with `checkpolicy`, and runs the test binary.

### Control flow and integration
Policy fixture rules produce `.std` and `.mls` files through `m4`, adding `-D enable_mls` for MLS variants. The test binary links all local `*.c` objects plus checkpolicy parser/util objects and `-lcunit`. `CPPFLAGS` includes libsepol headers and checkpolicy sources.

### Risks and edge cases
Tests depend on generated parser objects and CUnit availability. The `test` target runs `mkdir` through a clean `env -i` to avoid ASan preload ordering issues. Static linkage allows tests to reach internal functions but also couples the suite tightly to libsepol internals.

### Test signals
Successful `make test` validates fixture generation, source policy parsing, static libsepol linkage, and all registered CUnit suites in both non-MLS and MLS modes.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/debug.c -->
## sources/security-integrity/selinux/libsepol/tests/debug.c

### Purpose
`debug.c` provides lightweight debugging helpers for libsepol tests.

### Important APIs
`print_ebitmap()` prints every bit up to `bitmap->highbit` as `0` or `1`. `display_expr()` prints conditional expression nodes in RPN-ish order using boolean names from the policydb and operator tokens for NOT/OR/AND/XOR/EQ/NEQ.

### Dependencies and integration
It includes `debug.h`, which brings in policydb and conditional types. Test suites can call these helpers while diagnosing bitmap or conditional expression failures.

### Risks and edge cases
The functions are diagnostic only and do not validate indices. `display_expr()` assumes boolean expression values are valid one-based indexes into `p_bool_val_to_name`.

### Test signals
Manual/verbose test diagnostics are the primary signal. Compile coverage verifies prototype consistency with `debug.h`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/debug.h -->
## sources/security-integrity/selinux/libsepol/tests/debug.h

### Purpose
`debug.h` declares test debugging helpers for bitmaps and conditional expressions.

### Important APIs
It declares `print_ebitmap(ebitmap_t *bitmap, FILE *fp)` and `display_expr(policydb_t *p, cond_expr_t *exp, FILE *fp)`.

### Dependencies and integration
The header includes policydb and conditional definitions and is used by test implementation files. It intentionally exposes only diagnostic utilities.

### Risks and test signals
The file lacks a traditional include guard in the viewed source, but duplicate declarations are benign. Build coverage and any verbose test diagnostics exercise it.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/helpers.c -->
## sources/security-integrity/selinux/libsepol/tests/helpers.c

### Purpose
`helpers.c` implements common CUnit helper routines for loading source policies and finding declarations by symbol.

### Important APIs
`test_load_policy()` initializes a `policydb_t`, sets policy type, MLS flag, and max module policy version, builds the generated fixture path (`.std` or `.mls`), and calls `read_source_policy()`. `test_find_decl_by_sym()` looks up a symbol scope entry and returns the unique declaring `avrule_decl_t`.

### Control flow and state
Policy loading builds paths under `policies/<test_name>/<policy_name>.std|.mls`, initializes the policydb, and destroys it on read failure. Declaration lookup requires scope kind `SCOPE_DECL` and exactly one declaration ID, then indexes `p->decl_val_to_struct`.

### Dependencies and integration
It depends on checkpolicy `parse_util.h`, policy expansion/declaration types, and CUnit headers. All test suites that need fixture policies can share this logic.

### Risks and edge cases
Path construction checks only `snprintf() < 0`, not truncation equal to or greater than `PATH_MAX`. `test_find_decl_by_sym()` returns `NULL` for ambiguous or required-only scopes, which is useful but may hide the specific failure reason in tests.

### Test signals
Every suite using generated source policies exercises `test_load_policy()`. Scope/declaration tests exercise `test_find_decl_by_sym()`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/helpers.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/helpers.h -->
## sources/security-integrity/selinux/libsepol/tests/helpers.h

### Purpose
`helpers.h` declares shared test helpers and adjusts CUnit fatal assertions for static analysis.

### Important APIs and definitions
It declares `test_load_policy()` and `test_find_decl_by_sym()`. Under `__CHECKER__`, it redefines selected `CU_*_FATAL` macros to also call `assert()`, helping static analyzers understand control flow after fatal assertions.

### Dependencies and integration
The header includes policydb, conditional policy, and `<CUnit/Basic.h>`. Test suites include it to load policies and find module declarations.

### Risks and edge cases
The include guard name `__COMMON_H__` is generic and could collide. The static-analysis overrides only apply under `__CHECKER__`, so runtime behavior remains CUnit-defined.

### Test signals
Build coverage with and without `__CHECKER__`, plus any test suite loading source policies, verifies this header.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/helpers.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/libsepol-tests.c -->
## sources/security-integrity/selinux/libsepol/tests/libsepol-tests.c

### Purpose
`libsepol-tests.c` is the CUnit test runner for libsepol. It registers all local suites and runs them twice: once without MLS and once with MLS.

### Important APIs and control flow
`DECLARE_SUITE(name)` adds a suite using `name##_test_init`, `name##_test_cleanup`, and `name##_add_tests()`. `do_tests()` initializes CUnit, registers `ebitmap`, `cond`, `linker`, `expander`, `deps`, `downgrade`, and `neverallow`, chooses verbose or normal basic mode, runs either console or basic tests, collects failures, and cleans up. `main()` parses `--verbose` and `--interactive`, sets global `mls` to `0` and `1` for two passes, and returns failure if either pass fails.

### State and integration
Global `int mls` is shared with suites to choose standard versus MLS fixtures. The runner depends on CUnit basic/console APIs and suite headers. It is invoked by the tests Makefile after fixture generation.

### Risks and edge cases
`verbose` defaults to enabled even without `-v`. Usage mentions only `-v` and `-i`; `-h` is handled as default/error but not listed in getopt options. A failure to add any suite cleans up and returns the CUnit error code.

### Test signals
The runner is itself the aggregate signal: passing execution means all registered suites pass in both MLS modes and CUnit reports zero failed tests.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/tests/libsepol-tests.c -->
