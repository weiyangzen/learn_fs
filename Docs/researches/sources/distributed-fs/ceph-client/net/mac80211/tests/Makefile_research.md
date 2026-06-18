# sources/distributed-fs/ceph-client/net/mac80211/tests/Makefile

Purpose: builds the mac80211 KUnit test module when `CONFIG_MAC80211_KUNIT_TEST` is enabled.

Important APIs/targets: assigns `mac80211-tests-y` to include `module.o`, `util.o`, `elems.o`, `mfp.o`, `tpe.o`, `chan-mode.o`, and `s1g_tim.o`, then adds `mac80211-tests.o` to `obj-$(CONFIG_MAC80211_KUNIT_TEST)`.

Control flow and state: this is declarative kbuild state only. Object order controls which compilation units are linked into the KUnit module; runtime suite registration happens inside each test source through `kunit_test_suite()`.

Dependencies and integration points: depends on the kernel kbuild system, KUnit, the local `util` test harness, and exported-for-KUnit mac80211 symbols.

Risks and edge cases: adding a test source without listing it here means the suite will not run. Removing `module.o` would drop module metadata. The list currently includes `tpe.o`, which is outside this work item but part of the same test module.

Test signals: successful build of `CONFIG_MAC80211_KUNIT_TEST=m/y` and KUnit discovery of all named suites are the relevant signals.
