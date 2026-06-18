<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/regs.rs -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/regs.rs

Purpose: Defines Tyr's strongly typed 32-bit register accessor wrapper and the subset of Mali GPU register offsets/bit constants needed by reset, L2 power, and GPU-info queries.

Important APIs/types/functions: `Register<const OFFSET: usize>` has `read()` and `write()` methods using devres `IoMem` access. Constants cover GPU identity/features, IRQ status/clear/mask, soft/hard reset command, thread/texture/coherency features, present masks, L2 power/ready/transition/active registers, MCU control/status, job IRQ, and MMU IRQ.

Control flow: Higher-level code passes a bound device and devres MMIO object to each register accessor. Reads and writes can return errors if the devres access fails.

State and persistence: No state is stored here; constants encode hardware layout.

Dependencies and integration points: Uses Rust kernel IO traits, bit helpers, and the `IoMem` alias from `driver.rs`.

Risks and test signals: Incorrect offsets or bit definitions break hardware bring-up. The TODO notes a future register macro with 64-bit support. Tests should compare offsets against the C driver/spec, validate soft-reset and L2 bits, and cover access-error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/tyr/regs.rs -->
