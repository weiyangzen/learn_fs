# sources/distributed-fs/ceph-client/drivers/net/ethernet/microchip/vcap/vcap_api_debugfs_kunit.c

## Purpose
`vcap_api_debugfs_kunit.c` tests the debugfs and raw decode helpers by embedding a mocked VCAP platform, generated KUnit model tables, and expected text output. It is included from `vcap_api_debugfs.c` under `CONFIG_VCAP_KUNIT_TEST`, allowing tests to reach static helpers.

## Important Fixtures and Tests
The fixture defines mock cache streams, a mock netdev, platform callbacks for keyset validation, default fields, cache read/write/update/move/init, and a print collector (`test_prf`). `vcap_api_addr_keyset_test` scans synthetic IS2 key/mask streams and expects only the real rule start to decode as `VCAP_KFS_MAC_ETYPE`. `vcap_api_show_admin_raw_test` verifies raw address output. `vcap_api_show_admin_test` validates admin metadata formatting. `vcap_api_show_admin_rule_test` verifies full decoded rule output including keysets, key/action fields, counter, state, and field formatting.

## Control Flow
Each test initializes a `vcap_admin`, attaches it to `test_vctrl`, configures cache stream pointers, invokes internal debugfs helpers, and compares collected output lines. Cache read inverts mask words to emulate hardware mask conventions before decode.

## State and Persistence Behavior
State is test-local static fixture state reset by `vcap_test_api_init`. No persistent repository state is produced. The tests exercise both in-memory rule metadata and cache-backed decode paths.

## Dependencies and Integration Points
The file depends on KUnit, `vcap_model_kunit.h`, public VCAP headers, and debugfs implementation internals exposed by textual inclusion. It mirrors the callback contract used by real platform drivers but with deterministic arrays.

## Risks and Test Signals
These tests provide strong regression signals for debug output formatting and keyset discovery. They are brittle by design: expected strings encode exact field order, names, widths, and formatting, so generated model changes require synchronized expectation updates. They do not test actual debugfs file creation failures or lifetime issues.
