# sources/distributed-fs/ceph-client/net/mac80211/tests/module.c

Purpose: provides module metadata for the mac80211 KUnit test module.

Important APIs: includes `<linux/module.h>` and declares `MODULE_LICENSE("GPL")` plus `MODULE_DESCRIPTION("tests for mac80211")`.

Control flow and state: no executable logic, persistent state, init, or exit functions are defined. It exists so linked KUnit object files have standard module metadata.

Dependencies and integration points: built through the local tests Makefile into `mac80211-tests.o` when `CONFIG_MAC80211_KUNIT_TEST` is enabled.

Risks and edge cases: missing or incompatible license metadata can affect module loading and symbol access. Otherwise this file is intentionally minimal.

Test signals: compile and module-load/KUnit discovery are sufficient validation.
