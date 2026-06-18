# subset-b-008364 Research

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/debug.c -->
# sources/security-integrity/selinux/libsepol/src/debug.c

Purpose: implements libsepol's internal and compatibility message handling. It backs the deprecated process-global debug switch, exposes current message metadata, provides the default stdout/stderr printer, and installs per-handle callbacks used by `ERR`, `WARN`, and `INFO` in `debug.h`.

Important APIs and functions: `sepol_compat_handle` is the fallback global handle for legacy callers. `sepol_debug(int on)` toggles the fallback callback. `sepol_msg_get_level`, `sepol_msg_get_channel`, and `sepol_msg_get_fname` read the transient message fields on a `sepol_handle_t`. `sepol_msg_default_handler` selects `stderr` for errors/warnings and `stdout` for info, prefixes output with channel and function name, then prints a printf-format message. `sepol_msg_set_callback` replaces the callback and callback argument on a handle.

Control flow: `msg_write` in the header populates `msg_fname`, `msg_channel`, and `msg_level` on the selected handle, then invokes the callback. The default callback reads those fields through the getters, chooses the stream, performs `vfprintf`, and appends a newline. The deprecated `sepol_debug` path only changes whether the compatibility handle has a callback.

State and persistence behavior: no durable persistence. State is held in mutable `sepol_handle_t` fields and the global `sepol_compat_handle`. The message metadata fields are overwritten for each emitted message and are not thread-local.

Dependencies and integration points: depends on internal `handle.h` and `debug.h`, plus stdio/varargs. It is used by nearly every libsepol module through logging macros and by public handle setup code through `sepol_msg_set_callback`.

Risks: the compatibility handle and per-handle transient message fields make concurrent logging on a shared handle racy. `sepol_msg_get_*` assumes a non-NULL handle. Custom callbacks must obey the printf format contract and should not assume message metadata survives after the call.

Test signals: verify error and warning messages go to `stderr`, info goes to `stdout`, callback disabling suppresses output, custom callbacks receive the expected level/channel/function fields, and legacy `sepol_debug(0/1)` only affects the compatibility handle.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/debug.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/debug.h -->
# sources/security-integrity/selinux/libsepol/src/debug.h

Purpose: defines libsepol's internal status constants and logging macros. It is the glue between source modules and `debug.c`, giving callers a compact `ERR`, `WARN`, and `INFO` interface while preserving function, channel, and severity metadata.

Important APIs and types: `STATUS_SUCCESS`, `STATUS_ERR`, and `STATUS_NODATA` are local conventional return values. `msg_write(handle_arg, level_arg, channel_arg, func_arg, ...)` selects the supplied handle or falls back to `sepol_compat_handle`, populates message fields, and calls the configured callback. `ERR`, `INFO`, and `WARN` specialize `msg_write` for the `libsepol` channel and `__FUNCTION__`. It declares `sepol_msg_default_handler` and `sepol_compat_handle`.

Control flow: code calls `ERR(handle, ...)`, the macro resolves a handle, tests for `msg_callback`, writes `msg_fname`, `msg_channel`, and `msg_level`, then invokes the callback with the saved callback argument and format string.

State and persistence behavior: no storage is owned by this header, but the macro mutates the selected handle for every emitted message. This is per-handle mutable runtime state rather than persisted policy state.

Dependencies and integration points: includes public `<sepol/debug.h>`, internal `handle.h`, and stdio. It is included by policy parsing, expansion, conversion, record adapters, and utility modules for consistent diagnostics.

Risks: the macro declares a local `_sepol_h`, mutates the handle, and evaluates arguments inside a macro context. The comment correctly flags variable-shadowing concerns. Using a NULL handle intentionally routes to global compatibility state, which can surprise callers in multi-threaded or library-embedded use.

Test signals: compile with GCC format checking, exercise macro calls with NULL and explicit handles, verify no message is emitted when callback is NULL, and test callback metadata under nested or repeated logging paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/debug.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ebitmap.c -->
# sources/security-integrity/selinux/libsepol/src/ebitmap.c

Purpose: implements libsepol's sparse extensible bitmap abstraction used throughout policydb for type, role, user, category, capability, and rule-set membership. Bitmaps are stored as sorted linked nodes, each carrying a fixed-width machine map starting at `startbit`.

Important APIs and functions: set algebra includes `ebitmap_or`, `ebitmap_union`, `ebitmap_and`, `ebitmap_xor`, `ebitmap_not`, and `ebitmap_andnot`. Queries and utilities include `ebitmap_cardinality`, `ebitmap_hamming_distance`, `ebitmap_cmp`, `ebitmap_contains`, `ebitmap_match_any`, `ebitmap_get_bit`, and `ebitmap_highest_set_bit`. Mutators include `ebitmap_cpy`, `ebitmap_set_bit`, `ebitmap_init_range`, `ebitmap_destroy`, and `ebitmap_read`.

Control flow: algebra functions walk sorted node lists and allocate destination nodes only for non-empty maps. `ebitmap_set_bit` finds or creates the node for the requested bit, removes empty nodes when clearing, and updates `highbit` when the highest node changes. `ebitmap_read` reads map size, highbit, and node count from a little-endian policy stream, then validates alignment, ordering, non-zero node maps, bounds, and final highbit consistency.

State and persistence behavior: bitmap state is in caller-owned `ebitmap_t` node chains. `ebitmap_read` is the persistence boundary for binary policy input; it destroys partially built state on malformed or truncated input. Algebra functions usually initialize the destination and expect callers to destroy it.

Dependencies and integration points: depends on public policydb ebitmap structures, policy stream helpers in `private.h`, endian conversion, and `debug.h` diagnostics. It is foundational for expansion, MLS category handling, hierarchy checks, hashtab-to-string conversion, and kernel-to-CIL output.

Risks: ownership is manual and several functions return negative errno-style values while some callers collapse them to `-1`. `ebitmap_union` replaces `dst` through a temporary, so callers must not pass aliased inputs that violate expectations. `ebitmap_get_bit` tests `e->highbit < bit`, so edge behavior depends on the convention that `highbit` is one past the represented map boundary. Allocation failures in `ebitmap_init_range` can leak already-created nodes because it returns directly without destroying `e`.

Test signals: test sparse and dense OR/AND/XOR/NOT results, node deletion when clearing the last bit in a node, highbit updates, containment and any-match with disjoint starts, range initialization across one and multiple map nodes, binary read rejection for unsorted/zero/truncated/out-of-bounds maps, and memory-failure cleanup paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ebitmap.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/expand.c -->
# sources/security-integrity/selinux/libsepol/src/expand.c

Purpose: expands a linked base/module policydb into a kernel policydb. It copies enabled declarations into output symbol tables, maps old numeric values to new values, expands attributes and role attributes, lowers semantic rules into AV tabs and transition tables, copies object contexts/genfs contexts, handles tunables, and optionally runs hierarchy and assertion checks.

Important APIs and functions: public entry points are `expand_module`, `expand_module_avrules`, `expand_rule`, `expand_convert_type_set`, `type_set_expand`, `role_set_expand`, `mls_semantic_level_expand`, `mls_semantic_range_expand`, `expand_avtab`, and `expand_cond_av_list`. The core state carrier is `expand_state_t` with type/bool/role/user maps, input/output policydb pointers, handle, verbosity, and neverallow mode. Major copy callbacks handle types, aliases, bounds, commons, classes, constraints, roles, users, booleans, MLS sensitivities/categories, role allows/transitions, filename transitions, range transitions, conditionals, and object contexts.

Control flow: `expand_module` first collapses or preserves tunables, initializes output policy metadata, allocates value maps, then copies symbols in strict dependency order: types and aliases, attribute members, commons/classes, roles and role attributes, MLS levels/categories, users, booleans, and indexes. It then expands avrule blocks into `te_avtab` and `te_cond_avtab`, copies constraints, evaluates conditionals, copies platform-specific ocontexts and genfs entries, builds `attr_type_map` and `type_attr_map`, and optionally checks hierarchy and neverallow assertions. Rule expansion converts type/role sets through maps, handles `self`, creates or merges AV tab nodes, detects transition conflicts, and skips or copies neverallow rules depending on mode.

State and persistence behavior: no disk persistence. The function mutates `out` extensively and may mutate `base` by discarding tunable branches, expanding role attributes in the base, and, when `handle->expand_consume_base` is set, destroying consumed avrule blocks. Output state includes symbol tables, value-to-name indexes, AV tabs, conditional lists, object context lists, genfs lists, policycaps, permissive/neveraudit maps, and attribute maps.

Dependencies and integration points: uses policydb, conditional, hashtab, hierarchy, avrule-block, context, MLS, ebitmap, avtab, assertion, and indexing APIs. `handle` options (`disable_dontaudit`, `preserve_tunables`, `expand_consume_base`) directly alter output. Its output is consumed by kernel policy writers, assertion checkers, services, and kernel-to-text/CIL converters.

Risks: ordering is critical; many callbacks assume prior indexing and populated maps. Some error paths after partial output construction rely on the caller destroying the policydb. `discard_tunables` intentionally mutates linked policy state, which can surprise analysis tools unless `preserve_tunables` is set. `constraint_node_clone` copies constraint source type sets for diagnostics but has partial-allocation cleanup complexity. Rule conflict detection for transitions and named transitions is security-sensitive because contradictory type transitions must not be silently merged. Attribute expansion loops must detect cycles. Extended-permission AV tab entries are non-unique and require driver/specified matching.

Test signals: expand base policies with aliases, nested/cyclic attributes, role attributes, tunables preserved and discarded, disabled dontaudit, type/role/user bounds, MLS users and invalid category ranges, filename/range transitions, duplicate and conflicting type transitions, conditional true/false branches, extended permissions, SELinux and Xen object contexts, genfs contexts, consume-base mode, assertion failures, and allocation-failure cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/expand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/flask.h -->
# sources/security-integrity/selinux/libsepol/src/flask.h

Purpose: generated header defining numeric initial security identifier constants for SELinux policydb use. It provides stable indices for kernel, security, unlabeled, filesystem, networking, sysctl, module, policy, packet, and device-null initial SIDs.

Important APIs and types: constants `SECINITSID_KERNEL` through `SECINITSID_DEVNULL` assign one-based SID values, and `SECINITSID_NUM` records the maximum known SID count.

Control flow: none; this is a compile-time constant header.

State and persistence behavior: no runtime state. The numeric values are part of the binary/textual policy contract and must remain aligned with generated SID-name tables and kernel expectations.

Dependencies and integration points: included by policydb and conversion code that needs known initial SID numbers. It complements generated SID name arrays used by kernel-to-CIL/conf conversion and initial SID context handling.

Risks: manual edits would desynchronize libsepol from generated Flask/security class data. Off-by-one mistakes are especially risky because SIDs are one-based in policy structures.

Test signals: build-time generated-header consistency checks, policy read/write round trips with all known initial SIDs, and conversion output that preserves SID declaration/order and context mapping.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/flask.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/handle.c -->
# sources/security-integrity/selinux/libsepol/src/handle.c

Purpose: implements allocation, destruction, and option accessors for `sepol_handle_t`, the central libsepol object carrying diagnostics and expansion behavior flags.

Important APIs and functions: `sepol_handle_create` allocates a handle, installs `sepol_msg_default_handler`, and initializes `disable_dontaudit`, `expand_consume_base`, and `preserve_tunables` to zero. `sepol_get_preserve_tunables`/`sepol_set_preserve_tunables`, `sepol_get_disable_dontaudit`/`sepol_set_disable_dontaudit`, and `sepol_set_expand_consume_base` expose option fields. `sepol_handle_destroy` frees the handle.

Control flow: creation performs one allocation, initializes fields, and returns NULL on allocation failure. Accessors assert non-NULL handles, then read or write simple integer fields.

State and persistence behavior: no persistent storage. The handle owns only its struct memory; callback argument ownership belongs to the caller. Options persist for the life of the handle and influence later expansion/logging calls.

Dependencies and integration points: includes internal `handle.h` and `debug.h`. `expand.c` reads `disable_dontaudit`, `expand_consume_base`, and `preserve_tunables`; `debug.c` and `debug.h` use callback fields.

Risks: accessors abort on NULL because they use `assert`, which may disappear in release builds if `NDEBUG` is set. There is no getter for `expand_consume_base` in this file. Destroy does not invoke callback-argument cleanup.

Test signals: handle creation defaults, option round trips, behavior of expansion with each option, custom callback survival across handle lifecycle, NULL allocation handling, and sanitizer checks for use-after-free by callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/handle.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/handle.h -->
# sources/security-integrity/selinux/libsepol/src/handle.h

Purpose: defines the internal layout of `struct sepol_handle` behind the public opaque handle type.

Important APIs and types: `struct sepol_handle` contains transient message metadata (`msg_level`, `msg_channel`, `msg_fname`), a printf-style message callback and callback argument, and expansion flags `disable_dontaudit`, `expand_consume_base`, and `preserve_tunables`.

Control flow: none; the header provides fields consumed by `debug.c`, `debug.h`, `handle.c`, and expansion logic.

State and persistence behavior: instances are heap-allocated by `sepol_handle_create` or statically allocated for compatibility in `debug.c`. Message fields are overwritten during logging; option fields persist on the handle.

Dependencies and integration points: includes public `<sepol/handle.h>` for the opaque typedef. It is the internal contract between public handle APIs, message handling, and policy expansion.

Risks: any ABI-exposed misuse of the internal struct would couple callers to private fields, but the header is internal. Shared handles are not thread-safe for message metadata updates. Callback format attributes only apply under GCC.

Test signals: compile users of internal handle fields, verify callback format warnings, and exercise handle options through expansion and logging paths.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/handle.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/hashtab.c -->
# sources/security-integrity/selinux/libsepol/src/hashtab.c

Purpose: implements libsepol's generic chained hash table used by policydb symbol tables and auxiliary maps. Buckets are sorted by caller-provided comparison to support deterministic lookup traversal within chains.

Important APIs and functions: `hashtab_create` allocates a table with caller-supplied hash and compare callbacks. `hashtab_insert`, `hashtab_remove`, `hashtab_search`, `hashtab_destroy`, and `hashtab_map` provide core operations. `hashtab_check_resize` doubles the bucket array when element count reaches size. `hashtab_hash_eval` prints bucket statistics for diagnostics.

Control flow: insertion resizes if needed, hashes the key, walks the sorted chain until an equal or larger key, rejects duplicates, and splices a new node. Resize rehashes every node into a new bucket array while preserving sorted-chain insertion. Removal/search use the sorted chain to stop early when comparison passes the target. Map iterates bucket order and stops on first non-zero callback result.

State and persistence behavior: table state is heap-resident only. The table owns nodes and bucket arrays, but key and datum ownership is external unless `hashtab_remove` is supplied a destroy callback. `hashtab_destroy` frees nodes only, not pointed-to keys/data.

Dependencies and integration points: depends on public hashtab types and `private.h` error constants. Used pervasively for policydb symbol tables, range transitions, filename transitions, and generated string maps.

Risks: resize silently keeps the old table if allocation fails, which preserves correctness but may degrade performance. Callers must keep hash callbacks valid after `h->size` changes because hash values are bucket indexes. `hashtab_destroy` not freeing keys/data is a common ownership trap. `hashtab_hash_eval` prints directly to stdout and uses `%d` for unsigned table fields.

Test signals: insert/search/remove duplicates and ordered keys, resize boundaries including overflow guard at `UINT32_MAX`, map early exit, destroy ownership expectations, hash distribution diagnostics, and allocation-failure behavior during resize and node allocation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/hashtab.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/hierarchy.c -->
# sources/security-integrity/selinux/libsepol/src/hierarchy.c

Purpose: enforces SELinux hierarchical namespace bounds for types, roles, and users. It can infer parent bounds from dotted names, expand parent allow rules, compare child permissions against parent coverage, and report violations.

Important APIs and functions: public functions are `bounds_check_type`, `bounds_check_types`, `bounds_check_roles`, `bounds_check_users`, `bounds_destroy_bad`, `hierarchy_add_bounds`, and `hierarchy_check_constraints`. Internal helpers build parent global/conditional AV tabs (`bounds_expand_parent_rules`), check child global/conditional rules (`bounds_check_child_rules`), identify uncovered permissions (`bounds_not_covered`), and report bad AV entries (`bounds_report`).

Control flow: type checking first expands all rules where a parent type participates into a temporary global AV tab plus per-conditional true/false tables. It then walks child rules and verifies that each allowed permission is covered by the parent rule, accounting for bounded target types. Role and user checks are simpler ebitmap containment checks against parent roles/types. `hierarchy_add_bounds` derives missing bounds from dotted identifiers by stripping the final component and looking up the parent. `hierarchy_check_constraints` adds inferred bounds, runs user/role/type checks, and returns `SEPOL_ERR` on violations.

State and persistence behavior: no disk persistence. The code mutates `bounds` fields when inferring hierarchy parents. It allocates temporary avtabs and bad-node lists that must be destroyed. Errors are reported through the handle.

Dependencies and integration points: depends on policydb, conditional rules, avtab, expand, util, ebitmap, hashtab, and `debug.h`. `expand_module` calls `hierarchy_check_constraints` when requested after building output type/attribute maps.

Risks: checks are security-sensitive because a child type, role, or user must not gain authority beyond its parent. Temporary AV tab construction for conditionals must correctly account for permissions common to true and false branches. Dotted-name inference mutates policy state and can convert naming mistakes into orphan errors. Failure cleanup around partially allocated `bounds_cond_info` must remain correct.

Test signals: policies with valid and violating type bounds, bounded target types, role and user containment failures, conditional allow rules with permissions in one or both branches, dotted-name inferred parents, orphan dotted identifiers, empty rule sets, and memory-failure paths in temporary AV tab/list allocation.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/hierarchy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibendport_internal.h -->
# sources/security-integrity/selinux/libsepol/src/ibendport_internal.h

Purpose: private include shim for InfiniBand end-port record and collection APIs.

Important APIs and types: it includes `<sepol/ibendport_record.h>` and `<sepol/ibendports.h>` under an internal include guard; no new types or functions are declared here.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: used by `ibendport_record.c` and `ibendports.c` so those modules can share the public record/collection declarations through a local internal header.

Risks: minimal; it mainly centralizes includes. Header drift would affect compilation of end-port modules.

Test signals: compile the InfiniBand end-port record and policydb adapter modules against public headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibendport_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibendport_record.c -->
# sources/security-integrity/selinux/libsepol/src/ibendport_record.c

Purpose: implements the high-level `sepol_ibendport_t` and `sepol_ibendport_key_t` record API for SELinux InfiniBand end-port contexts, keyed by IB device name and port.

Important APIs and functions: key APIs include `sepol_ibendport_key_create`, `sepol_ibendport_key_unpack`, `sepol_ibendport_key_extract`, and `sepol_ibendport_key_free`. Record APIs include `sepol_ibendport_create`, `sepol_ibendport_clone`, `sepol_ibendport_free`, compare functions, port get/set, device-name get/set, context get/set, and `sepol_ibendport_alloc_ibdev_name`.

Control flow: creation allocates zeroed record/key objects, copies device names into fixed `IB_DEVICE_NAME_MAX` buffers, and stores port integers. Cloning deep-copies device name and context. Setters allocate new storage before replacing existing fields. Context assignment clones the supplied `sepol_context_t`.

State and persistence behavior: records are heap objects owned by callers. Device names and contexts are deep-owned by records/keys. No policydb persistence occurs here; low-level policy insertion is handled by `ibendports.c`.

Dependencies and integration points: includes policydb for `IB_DEVICE_NAME_MAX`, internal context conversion header for context cloning/freeing, `ibendport_internal.h`, and diagnostics. It feeds the collection APIs that convert to and from `ocontext_t`.

Risks: device names are truncated with `strncpy` to `IB_DEVICE_NAME_MAX - 1`, so callers may not notice truncation. Compare order sorts primarily by port, using device-name comparison only when ports match/equal checks need it, which may differ from lexical device-first expectations. Error messages include minor wording mistakes but not behavior impact.

Test signals: create/free keys and records, long device-name truncation, compare ordering by port and name, clone independence, context setter deep-copy behavior, allocation failures, and key extraction from records with unset fields.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibendport_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibendports.c -->
# sources/security-integrity/selinux/libsepol/src/ibendports.c

Purpose: adapts high-level InfiniBand end-port records to policydb `OCON_IBENDPORT` object-context linked lists. It supports count, existence, query, modify, and iteration operations over end-port contexts.

Important APIs and functions: public APIs are `sepol_ibendport_count`, `sepol_ibendport_exists`, `sepol_ibendport_query`, `sepol_ibendport_modify`, and `sepol_ibendport_iterate`. Internal converters are `ibendport_from_record` and `ibendport_to_record`.

Control flow: `ibendport_from_record` allocates an `ocontext_t`, allocates/copies the device name, copies the port, converts the high-level context to `context_struct_t`, and stores it in `context[0]`. Query/existence linearly scan `policydb->ocontexts[OCON_IBENDPORT]` for exact device and port. Modify converts the record and prepends it to the list. Iterate converts each low-level entry to a high-level record, invokes a callback, and stops if the callback returns positive.

State and persistence behavior: modifies in-memory policydb ocontext lists only; actual policy serialization is elsewhere. `modify` always prepends and does not replace an existing matching end-port, so duplicate keys can be introduced.

Dependencies and integration points: depends on context conversion (`context_from_record`, `context_to_record`), handle/debug, policydb ocontext layout, and `ibendport_record.c` APIs. Kernel-to-CIL and expand code also understand `OCON_IBENDPORT`.

Risks: lack of duplicate replacement can make query return the most recently prepended match while older duplicates remain. Error cleanup for allocated `u.ibendport.dev_name` is incomplete in some paths because the err block frees the `ocontext_t` but not always nested name storage. Linear scans are acceptable for small policy object lists but can be costly if many entries exist.

Test signals: count/query/exists/iterate on empty and populated lists, modify duplicate behavior, context conversion failures, callback early-stop and failure handling, memory cleanup under allocation failure, and CIL output round trips for `ibendportcon`.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibendports.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibpkey_internal.h -->
# sources/security-integrity/selinux/libsepol/src/ibpkey_internal.h

Purpose: private include shim for InfiniBand partition-key record and collection APIs.

Important APIs and types: includes `<sepol/ibpkey_record.h>` and `<sepol/ibpkeys.h>` under an include guard. It declares no additional implementation detail.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: used by `ibpkey_record.c` and `ibpkeys.c` to share public pkey declarations through a local internal header.

Risks: minimal compile-time include coupling only.

Test signals: compile pkey record and policydb adapter modules with public headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibpkey_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibpkey_record.c -->
# sources/security-integrity/selinux/libsepol/src/ibpkey_record.c

Purpose: implements high-level `sepol_ibpkey_t` and `sepol_ibpkey_key_t` records for InfiniBand partition-key context entries, keyed by subnet prefix and pkey range.

Important APIs and functions: key APIs are `sepol_ibpkey_key_create`, `sepol_ibpkey_key_unpack`, `sepol_ibpkey_key_extract`, and `sepol_ibpkey_key_free`. Record APIs include create, clone, free, compare functions, low/high getters, single pkey and range setters, subnet-prefix string and byte getters/setters, and context get/set. Internal helpers parse/format subnet prefixes with `inet_pton`/`inet_ntop` and allocate string buffers.

Control flow: string subnet prefixes are parsed as IPv6 addresses and the first 64 bits are copied into a `uint64_t`. Formatting builds an IPv6 address with the stored prefix in the leading bytes. Creation initializes prefix/range to zero; setters update numeric fields; context assignment clones the supplied context. Key extraction formats then reparses the subnet prefix through the public key constructor.

State and persistence behavior: records and keys are heap-owned caller objects. Contexts are deep-cloned. No policydb mutation occurs here.

Dependencies and integration points: uses networking address conversion, public pkey headers, internal context cloning, and debug logging. `ibpkeys.c` converts these records to `OCON_IBPKEY` entries, while kernel-to-CIL writes them as `ibpkeycon`.

Risks: subnet prefix byte ordering is subtle because bytes are copied directly between `struct in6_addr` and `uint64_t`; cross-platform endianness assumptions must match policydb storage. Range setters do not validate low <= high; validation happens in `ibpkeys.c`. Error message formatting has minor missing spacing but no functional effect.

Test signals: parse/format subnet prefixes, byte getter/setter round trips, invalid IPv6 strings, low/high and single-pkey setters, range ordering deferred validation, compare ordering by prefix/low/high, clone independence, and context deep-copy behavior.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibpkey_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibpkeys.c -->
# sources/security-integrity/selinux/libsepol/src/ibpkeys.c

Purpose: adapts high-level InfiniBand pkey records to policydb `OCON_IBPKEY` object-context lists, supporting count, existence, query, modify, and iteration.

Important APIs and functions: public APIs are `sepol_ibpkey_count`, `sepol_ibpkey_exists`, `sepol_ibpkey_query`, `sepol_ibpkey_modify`, and `sepol_ibpkey_iterate`. Internal converters `ibpkey_from_record` and `ibpkey_to_record` bridge `sepol_ibpkey_t` and `ocontext_t`.

Control flow: conversion from record allocates an `ocontext_t`, copies subnet prefix bytes and low/high range, rejects low > high, converts the high-level context into `context[0]`, and returns the low-level node. Existence/query scan the `OCON_IBPKEY` list for exact prefix and range. Modify prepends the converted node. Iterate converts each node to a high-level record, calls the callback, frees the temporary record, and stops on positive callback status.

State and persistence behavior: mutates the in-memory policydb ocontext list only. Modify does not replace existing matching entries, so duplicate pkey ranges can remain. Persistence to binary or CIL is handled by other modules.

Dependencies and integration points: depends on `context_from_record`, `context_to_record`, public/internal pkey APIs, policydb ocontext layout, and debug logging. `expand.c` copies `OCON_IBPKEY`, and `kernel_to_cil.c` emits `ibpkeycon`.

Risks: duplicate entries are possible. Error paths include an unused `subnet_prefix_buf` and must destroy partially initialized contexts. Exact matching does not check overlapping ranges, so policy-level conflict validation must happen elsewhere. Endianness of stored subnet prefixes must align with record conversion and CIL output.

Test signals: empty/non-empty count, exact query/exists, duplicate modify behavior, low > high rejection, callback early-stop/failure, subnet prefix round trip through CIL, overlapping range policy validation elsewhere, and allocation-failure cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/ibpkeys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/iface_internal.h -->
# sources/security-integrity/selinux/libsepol/src/iface_internal.h

Purpose: private include shim for network interface record and collection APIs.

Important APIs and types: includes `<sepol/iface_record.h>` and `<sepol/interfaces.h>` under an internal include guard. No additional declarations are introduced.

Control flow: none.

State and persistence behavior: none.

Dependencies and integration points: used by `iface_record.c` and `interfaces.c` to share public interface declarations.

Risks: minimal; it is compile-time include plumbing.

Test signals: compile interface record and adapter modules against public headers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/iface_internal.h -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/iface_record.c -->
# sources/security-integrity/selinux/libsepol/src/iface_record.c

Purpose: implements high-level `sepol_iface_t` and `sepol_iface_key_t` records for SELinux network interface contexts. Each interface has a name, an interface context, and a message context.

Important APIs and functions: key APIs include `sepol_iface_key_create`, `sepol_iface_key_unpack`, `sepol_iface_key_extract`, and `sepol_iface_key_free`. Record APIs include `sepol_iface_create`, `sepol_iface_get_name`, `sepol_iface_set_name`, `sepol_iface_get_ifcon`, `sepol_iface_set_ifcon`, `sepol_iface_get_msgcon`, `sepol_iface_set_msgcon`, `sepol_iface_clone`, `sepol_iface_free`, and compare functions.

Control flow: key and name setters duplicate strings. Context setters clone supplied contexts before replacing existing ones. Clone creates a new record, copies the name, and deep-clones both contexts when present.

State and persistence behavior: records are caller-owned heap objects with owned name and context pointers. No policydb state is changed here.

Dependencies and integration points: depends on internal context APIs and public interface headers. `interfaces.c` uses these objects to convert to/from `OCON_NETIF` entries.

Risks: setters assume non-NULL input strings/contexts unless lower layers handle NULL. Compare is simple `strcmp`, so NULL names are unsafe. Callers must free keys/records to avoid leaks.

Test signals: key extraction, create/free, name setter ownership, compare ordering, context setter deep-copy behavior for both contexts, clone independence, and failure handling when context clone or string allocation fails.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/iface_record.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/interfaces.c -->
# sources/security-integrity/selinux/libsepol/src/interfaces.c

Purpose: adapts high-level network interface records to policydb `OCON_NETIF` object-context entries. It supports existence, query, modify, count, and iteration operations.

Important APIs and functions: public APIs are `sepol_iface_exists`, `sepol_iface_query`, `sepol_iface_modify`, `sepol_iface_count`, and `sepol_iface_iterate`. Internal converters are `iface_from_record` and `iface_to_record`.

Control flow: `iface_from_record` allocates an `ocontext_t`, duplicates the interface name, converts interface and message contexts into `context[0]` and `context[1]`, and returns the node. Query/existence scan `OCON_NETIF` by name. Modify converts the new record, replaces an existing same-name node if found, or prepends the node otherwise. Iterate converts each node to a temporary high-level record and invokes a callback.

State and persistence behavior: mutates the in-memory `policydb->ocontexts[OCON_NETIF]` linked list. Unlike pkey/endport modify, interface modify replaces existing keys and frees the old name and contexts. Serialization is handled elsewhere.

Dependencies and integration points: depends on context conversion, handle/debug, public interface APIs, policydb object contexts, `expand.c` object-context copying, and kernel-to-CIL `netifcon` output.

Risks: replacement frees only the old node fields expected for `OCON_NETIF`, so the list must contain valid interface contexts. All operations are linear scans. Error cleanup must destroy both contexts if conversion partially succeeds.

Test signals: modify insert and replace paths, query after replacement, count stability, two-context conversion round trips, callback early-stop/failure, empty list behavior, and allocation/context-conversion failure cleanup.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/interfaces.c -->

<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/kernel_to_cil.c -->
# sources/security-integrity/selinux/libsepol/src/kernel_to_cil.c

Purpose: converts an in-memory binary/kernel `policydb` into CIL text. It emits declarations, defaults, MLS data, constraints, attributes, booleans, types, AV rules, transitions, conditionals, RBAC/user rules, and platform-specific object-context rules in deterministic order where possible.

Important APIs and functions: public entry points are `sepol_kernel_policydb_to_cil` for full output and `sepol_kernel_policydb_decls_to_cil` for declarations only. Major helpers stringify conditional and constraint postfix expressions, write class/common/SID/default/MLS/policycap/type/role/user declarations, write type aliases/bounds/attribute sets/permissive/neveraudit rules, stringify AV tab nodes including xperms, write filename and range transitions, write conditionals, and emit SELinux or Xen object contexts.

Control flow: full conversion first checks policy-version support, precomputes sorted MLS and non-MLS constraint/validatetrans strings, writes top-level policy metadata and declarations, emits MLS constraints before policy rules, writes capabilities, types/attributes/booleans/AV rules/transitions/conditionals/RBAC/users, emits non-MLS constraints, sorts object contexts in-place, then dispatches to SELinux or Xen object-context writers. Declaration-only conversion runs a shorter sequence for SID/class/MLS/boolean/type/attribute/role/user declarations.

State and persistence behavior: output is written to the caller-provided `FILE *`. The input policydb is mostly read-only, but `sepol_kernel_policydb_to_cil` calls `sort_ocontexts(pdb)`, which reorders object-context linked lists in place for deterministic output. Temporary `struct strs` lists own many formatted strings and are destroyed before return.

Dependencies and integration points: uses `kernel_to_common.h` utilities (`sepol_printf`, `create_str`, `strs`, `ebitmap_to_str`, SID maps, `sort_ocontexts`, `check_for_supported_policy`), policydb/avtab/conditional/services utilities, network address formatting, polcap names, and debug logging. It consumes output from policy expansion and binary policy readers.

Risks: CIL syntax correctness is security-sensitive because conversion should preserve policy semantics. Many helper functions assume valid one-based indexes into value-to-name arrays. `sort_ocontexts` mutates caller state, which can affect later consumers expecting original order. Extended-permission formatting dynamically grows buffers and must preserve range semantics. Genfs wildcard policycap handling rejects paths not ending in `*`. Non-MLS policies still emit a synthetic default MLS level because CIL requires one.

Test signals: full conversion and declaration-only conversion for SELinux and Xen policies; policies with constraints, MLS validatetrans, aliases, bounds, attributes, permissive/neveraudit maps, xperms, filename/range transitions, conditionals, role transitions/allows, users with MLS ranges, all SELinux context kinds including InfiniBand, all Xen context kinds, genfs wildcard capability, unsupported policy versions, malformed indexes, and output determinism across repeated runs.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libsepol/src/kernel_to_cil.c -->
