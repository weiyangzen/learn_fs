# sources/distributed-fs/ceph-client/include/linux/license.h

Purpose: provides a helper for deciding whether a module license string is GPL-compatible.

Important APIs and types: `license_is_gpl_compatible()` compares a string against accepted GPL-compatible spellings: GPL, GPL v2, GPL with additional rights, Dual BSD/GPL, Dual MIT/GPL, and Dual MPL/GPL.

Control flow: module/license checking code calls this helper when determining whether GPL-only exports may be used or whether tainting should apply.

State and persistence: no state is stored; behavior is pure string comparison.

Dependencies and integration points: depends on `strcmp()` being available to includers; integrates module metadata with export policy.

Risks and test signals: risks include missing accepted license aliases, case/exact-string mismatch, and NULL input misuse. Test module loading with each accepted string, rejected proprietary strings, and GPL-only symbol access policy.
