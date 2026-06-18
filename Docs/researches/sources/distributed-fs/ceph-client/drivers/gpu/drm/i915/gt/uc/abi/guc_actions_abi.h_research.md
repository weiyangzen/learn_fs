# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_actions_abi.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/uc/abi/guc_actions_abi.h

### Purpose
`guc_actions_abi.h` defines GuC host-to-firmware action IDs and message field layouts for self-configuration, CTB control, legacy GuC actions, logging, reset, HuC auth, scheduling, capture, TLB invalidation, and power-management commands.

### Important APIs, Types, And Functions
Key definitions include `GUC_ACTION_HOST2GUC_SELF_CFG`, `HOST2GUC_SELF_CFG_*`, `GUC_ACTION_HOST2GUC_CONTROL_CTB`, `GUC_CTB_CONTROL_*`, `enum intel_guc_action`, response/status enums, log-control bit masks, state-capture event status, and TLB invalidation type/mode flags.

### Control Flow
The header has no executable flow; it encodes request and response dword contracts used by GuC MMIO/CT senders and G2H handlers.

### State, Persistence, Dependencies, Integration, Risks, And Test Signals
No state is stored here. It depends on HXG message definitions included by users and integrates with `intel_guc.c`, CT communication, SLPC, HuC auth, and submission code. Risks are ABI drift with firmware, wrong bit masks, and legacy action compatibility. Test signals are successful GuC boot/self-config, CTB enablement, expected firmware responses, and error handling for retry/failure statuses.
