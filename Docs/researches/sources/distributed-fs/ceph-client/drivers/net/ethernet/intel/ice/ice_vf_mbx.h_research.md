# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_vf_mbx.h

## Purpose
Declares VF mailbox helper APIs and the asynchronous mailbox threshold constant. It also provides no-op stubs for most mailbox operations when SR-IOV support is disabled.

## Important APIs
`ICE_ASYNC_VF_MSG_THRESHOLD` is 63 pending async messages. Under `CONFIG_PCI_IOV`, the header exports PF-to-VF AQ send, link speed conversion, E830 counter helpers, malicious VF state handler, per-VF clear/init, and global snapshot init.

## Control Flow and Conditional Compilation
SR-IOV builds call real mailbox functions. Non-SR-IOV builds return success/zero for send and speed conversion and no-op snapshot/counter functions, preventing mailbox code from being linked into non-IOV configurations.

## State and Persistence
The header does not define the state structures directly but connects callers to `ice_mbx_vf_info`, `ice_mbx_data`, and `ice_mbx_snapshot` state stored under `ice_type.h` hardware/VF structures.

## Dependencies and Integration Points
Includes `ice_type.h` and `ice_controlq.h`; integrated by VF reset, virtchnl response sending, mailbox interrupt processing, and hardware initialization.

## Risks
Only some functions have non-IOV stubs; always-built users must call only the stubbed surface. The threshold constant is a policy decision and should match assumptions in the mailbox detector and operational monitoring.

## Test Signals
Compile with `CONFIG_PCI_IOV` on/off, verify no unresolved mailbox symbols in non-IOV builds, and test threshold behavior with the implementation.
