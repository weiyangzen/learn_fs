
# sources/distributed-fs/ceph-client/arch/powerpc/kvm/test-guest-state-buffer.c

## Purpose
Defines KUnit tests for the guest state buffer APIs implemented in `guest-state-buffer.c`. It validates buffer allocation, element serialization, parser lookup, bitmap flatten/unflatten iteration, message callback use, and host-wide counter retrieval through `H_GUEST_GET_STATE`.

## Important APIs, Types, And Functions
Test cases include `test_creating_buffer()`, `test_adding_element()`, `test_gs_parsing()`, `test_gs_bitmap()`, `test_gs_msg()`, `test_gs_hostwide_msg()`, and `test_gs_hostwide_counters()`. It defines mock message data structs and two `struct kvmppc_gs_msg_ops` implementations for normal and host-wide messages.

## Control Flow
Tests allocate buffers/messages, call public helpers such as `kvmppc_gsb_new()`, `__kvmppc_gse_put()`, typed put/get wrappers, `kvmppc_gse_parse()`, bitmap set/clear/test/iterate macros, `kvmppc_gsm_fill_info()`, and `kvmppc_gsm_refresh_info()`, then assert serialized IDs, lengths, and recovered values. The host-wide counter test skips unless running as a KVM-HV pseries guest, then sends a real host-wide get-state hcall and parses returned counters.

## State And Persistence
All state is test-local heap or stack data, except the host-wide counter test depends on the actual hypervisor environment. Some tests allocate `gsb` without freeing it on all paths (`test_gs_msg()` and `test_gs_hostwide_msg()` free the message but not the buffer), which is acceptable for short KUnit execution but worth noting if leak detection is strict.

## Dependencies And Integration Points
Depends on KUnit, guest state buffer headers, KVM PowerPC helpers, and optionally a pseries KVM-HV environment. The test suite is registered with `kunit_test_suites()`.

## Risks
The mock `test1_fill_info()` calls `kvmppc_gse_put_proc_table()` with `KVMPPC_GSID_PARTITION_TABLE`, which appears inconsistent with the inclusion check for `KVMPPC_GSID_PROCESS_TABLE`; the test still passes because it only refreshes GPR/CR values. The environment-dependent host-wide test can be skipped in most CI, leaving hcall behavior lightly covered.

## Test Signals
The suite name is `guest_state_buffer_test`. Passing tests indicate basic buffer encoding/parsing and bitmap mapping remain intact. Additional negative tests for bad sizes, missing callbacks, capacity errors, and duplicate IDs would improve confidence.
