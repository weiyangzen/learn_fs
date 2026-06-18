<!-- BEGIN_FILE_RESEARCH: sources/compression/xz/src/common/my_landlock.h -->
# sources/compression/xz/src/common/my_landlock.h

Purpose: header-only Linux Landlock helper for creating deny-all ruleset attributes and syscall wrappers.

Important APIs/types/functions: `my_landlock_ruleset_attr_forbid_all`, `my_landlock_create_ruleset`, `my_landlock_restrict_self`, fallback `LANDLOCK_ACCESS_FS_*` macros, and cached ABI version state.

Control flow: query ABI version once with `landlock_create_ruleset(... VERSION)`, optionally detect buggy RHEL 9 ABI 6 signal scope, fill `landlock_ruleset_attr` with all known restrictions, then mask fields unsupported by the runtime ABI.

State and persistence: static cached ABI version and RHEL detection flag; no filesystem persistence.

Dependencies and integration: included by sandbox code only when Landlock support is configured. Requires Linux Landlock, syscall numbers, `prctl`, and `uname`.

Risks: note says only one file should include it and only one thread should call it because of static state. ABI/version backport quirks are explicitly handled but future ABI changes may need updates.

Test signals: sandbox tests on kernels with no Landlock, ABI 1-9 features, and RHEL backport variants; verify unsupported access bits are not passed.
<!-- END_FILE_RESEARCH: sources/compression/xz/src/common/my_landlock.h -->
