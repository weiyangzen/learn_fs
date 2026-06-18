# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_communication_mmio_abi.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_communication_mmio_abi.h

### Purpose
`guc_communication_mmio_abi.h` documents and bounds early GuC communication through software scratch registers.

### Important APIs, Types, And Functions
The key definition is `GUC_MAX_MMIO_MSG_LEN` set to 4. The header documents that MMIO messages embed HXG messages and that Gen11+ scratch registers are preferred where available.

### Control Flow
No code executes here. Runtime users write request dwords into scratch registers, trigger a GuC interrupt, and poll the first register for GuC-originated HXG response state.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
State is hardware scratch-register contents, not header-owned memory. Integration is through `intel_guc_send_mmio()` and early CTB/self-config setup. Risks include exceeding firmware-supported length, choosing wrong scratch base per generation/GT, and confusing MMIO with CTB once CT is enabled. Test signals are successful self-config and CTB setup before CT channel use.
