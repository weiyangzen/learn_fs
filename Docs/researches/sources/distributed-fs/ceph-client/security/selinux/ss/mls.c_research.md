<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls.c -->
# sources/distributed-fs/ceph-client/security/selinux/ss/mls.c

## Purpose
Implements SELinux Multi-Level Security operations: context string formatting/parsing, MLS level/range validation, default range setup, policy conversion of levels/categories, MLS range computation during transitions, and optional NetLabel MLS import/export.

## Important APIs, Types, and Functions
Public APIs include `mls_compute_context_len()`, `mls_sid_to_context()`, `mls_level_isvalid()`, `mls_range_isvalid()`, `mls_context_isvalid()`, `mls_context_to_sid()`, `mls_from_string()`, `mls_range_set()`, `mls_setup_user_range()`, `mls_convert_context()`, `mls_compute_sid()`, and NetLabel helpers. It relies on `mls_context_cpy*()` helpers from `context.h` and bitmap operations from `ebitmap`.

## Control Flow
Formatting computes or emits `:sensitivity[:cats][-high[:cats]]`, compacting consecutive categories with ranges. Parsing splits the context string in place into low/high range parts, resolves sensitivities and categories through policy symbol tables, expands category ranges, and defaults high to low when no high range is specified. Validation checks sensitivity existence, category authorization for the level, range dominance, and user authorization. Transition computation honors explicit range transition rules, class default ranges, process/object defaults, or source effective low range depending on AVTAB operation and object class.

## State and Persistence
MLS state is embedded in `struct context` as two `mls_level`s with ebitmap categories. Policydb stores level/category/user range definitions and range transition rules. NetLabel helpers persist only through packet/socket security attributes managed elsewhere.

## Dependencies and Integration Points
Depends on policydb symbols, SID table default-context lookup, services range transition search, NetLabel, ebitmap category conversion, and context helpers. Used by SID/context conversion, policy reload conversion, user context setup, transition labeling, and NetLabel mapping.

## Risks
Parsing mutates the input string and requires callers to pass writable buffers. Category ranges are one-based in policy values but zero-based in bitmaps. `mls_import_netlbl_cat()` shallow-copies the low category bitmap struct to high after import; ownership assumptions are delicate because both levels then describe the same node list. Default range behavior must match class policy semantics or transitions get wrong labels.

## Test Signals
Test non-MLS policies, MLS context formatting/parsing with single categories and ranges, invalid sensitivities/categories/reversed ranges, user range authorization, default SID fallback, range transition rules, every class default range mode, policy conversion with renamed/missing levels/categories, and NetLabel level/category import/export.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls.c -->
