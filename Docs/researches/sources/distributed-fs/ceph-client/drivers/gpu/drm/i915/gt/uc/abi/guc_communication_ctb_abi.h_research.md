# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_communication_ctb_abi.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_communication_ctb_abi.h

### Purpose
`guc_communication_ctb_abi.h` defines the command transport buffer ABI used for GuC host/firmware message streaming after early MMIO setup.

### Important APIs, Types, And Functions
It defines `struct guc_ct_buffer_desc`, CTB status bits, CTB header length/min/max constants, `GUC_CTB_MSG_0_*` field masks, `GUC_CTB_FORMAT_HXG`, and CTB HXG min/max lengths.

### Control Flow
There is no executable flow. The descriptor contract assigns `head` to the receiver and `tail` to the sender, while each stream record carries a header with fence, format, reserved bits, and payload length followed by embedded HXG dwords.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
Persistent shared state is the descriptor and circular buffer memory managed by `intel_guc_ct`. It depends on `guc_messages_abi.h` and packed layout rules. Integration points include GuC self-config KLVs, CT send/receive workers, and G2H event handling. Risks are head/tail corruption, overflow/underflow status handling, length mismatch, and firmware/header ABI drift. Test signals are CTB enablement, successful H2G/G2H traffic, status remaining `NO_ERROR`, and robust recovery from overflow or mismatch.
