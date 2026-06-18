# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_messages_abi.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_messages_abi.h

### Purpose
`guc_messages_abi.h` defines the HXG message grammar used by both MMIO and CTB GuC communication.

### Important APIs, Types, And Functions
It defines origin/type/aux masks, host and GuC origins, request/event/fast-request/busy/retry/failure/success types, request and event action/data masks, busy/retry fields, failure hint/error fields, response data fields, and deprecated message type macros.

### Control Flow
No executable flow exists. Runtime senders construct request or event dwords; receivers inspect origin and type, then branch between busy wait, retry, failure, or success handling.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
The header owns no state but defines the wire format for `intel_guc_send_mmio()`, CT send/receive paths, SLPC requests, self-config, and G2H events. Risks are incorrect field extraction, failing to handle busy/retry, and mixing deprecated and HXG type encodings. Test signals are protocol-correct GuC replies, busy/retry handling, failure-code logging, and CT/MMIO interoperability.
