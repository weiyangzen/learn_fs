# sources/distributed-fs/glusterfs/xlators/cluster/dht/src/unittest/dht_layout_mock.c

## Purpose
Provides minimal mock/stub definitions needed to link the DHT layout unit test without pulling the full GlusterFS runtime. The stubs return neutral success values and suppress logging/xattr behavior.

## Important APIs and Functions
- `dht_hash_compute`: stubbed to return success.
- `dht_inode_ctx_layout_get` / `dht_inode_ctx_layout_set`: no-op inode context stubs.
- `dict_get_ptr` / `dict_get_ptr_and_len`: no-op dict lookup stubs.
- `_gf_log`, `_gf_log_callingfn`, `_gf_msg`: logging stubs returning success.
- `gf_uuid_unparse`: empty UUID conversion stub.

## Control Flow
There is no meaningful control flow. Every stub immediately returns 0 or does nothing. The file exists to satisfy external symbol references from the DHT layout code under test.

## State and Persistence
No state is read or written. Output parameters are not populated, so tests relying on these helpers must avoid paths where real values are required.

## Dependencies and Integration Points
Includes GlusterFS and xlator headers plus `dht-common.h`. It is linked with `dht_layout_unittest.c` and the production layout implementation selected by the unit-test build.

## Risks
- Returning success without setting output values can hide bugs if tests expand into code paths that expect populated pointers or UUID strings.
- Logging and dict APIs are not behaviorally faithful.
- The mock is tightly scoped to `dht_layout_new`; broader layout tests would need richer mocks.

## Test Signals
The paired unit test currently exercises layout allocation defaults. This mock should remain intentionally small unless additional DHT layout functions are tested.
