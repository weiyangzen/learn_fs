# sources/distributed-fs/eos/namespace/ns_quarkdb/tests/NextInodeProviderTest.cc

Purpose: Unit/integration tests for `InodeBlock` and QDB-backed `NextInodeProvider`.
Important APIs/types/functions: `NextInodeProviderTest` fixture, `qclient::QHash`, `NextInodeProvider`, and `InodeBlock`.
Control flow: provider tests create a QDB hash counter, clear it, reserve sequences, destroy/recreate providers, blacklist thresholds, and assert reserved values/high-water marks. Block tests construct ranges, reserve and peek IDs, and blacklist within/across the range.
State/persistence: validates QDB hash field `counter` as persistent largest-reserved value; also validates local block state and restart gaps caused by pre-reserved blocks.
Dependencies/integration: depends on live QuarkDB through `NsTestsFixture::createQClient`, qclient `QHash`, and the allocator implementation.
Risks: `firstRunLimit`/`secondRunLimit` loops are large and can be slow; assertions intentionally allow wasted IDs after restart, so gaps are accepted behavior.
Test signals: excellent coverage of monotonicity, blacklisting semantics, 64-bit boundary behavior, off-by-one correctness, and reset persistence.
