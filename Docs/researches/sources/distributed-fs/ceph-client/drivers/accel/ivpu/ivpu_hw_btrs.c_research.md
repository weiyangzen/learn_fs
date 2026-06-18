## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_hw_btrs.c

### Purpose
`ivpu_hw_btrs.c` implements buttress-side hardware control for fuses, PLL/workpoint requests, D0i3, IP reset, LNL arbitration and profiling settings, idle/frequency queries, buttress IRQ handling, dynamic clock throttling mailbox, telemetry registers, global/local interrupt masks, diagnostics, and platform reading.

### Important APIs, Types, And Functions
Public functions match `ivpu_hw_btrs.h`: info/frequency init, interrupt clear workaround detection, workpoint drive, D0i3 enable/disable, clock ownership wait, idle checks, IP reset, profiling/ATS/clock-relinquish controls, frequency getters, MTL/LNL IRQ handlers, DCT request/status, telemetry getters, IRQ mask controls, diagnostics, and platform read. Internal helpers split MTL and LNL register programming.

### Control Flow
Init reads fuses and PLL ratios, clamps them with module parameters, and records tile/SKU/config data. Workpoint drive syncs the request command, writes generation-specific payloads, polls PLL lock/status ready, and on disable waits for CDYN deassertion on LNL. D0i3 drive polls in-progress, toggles the I3 bit, and polls completion. IRQ handlers read status, log frequency/error details, clear source error registers, clear local status, and trigger PM recovery for fatal errors or queue DCT work for survivability interrupts.

### State, Persistence, And Dependencies
Buttress state includes PLL ratios, workpoint, D0i3 state, tile fuse/SKU, telemetry registers, port weights, interrupt masks/status, PCODE mailbox status, and error logs. Dependencies include MTL/LNL buttress register headers, generic reg I/O helpers, PM recovery/DCT work, units constants, and ivpu generation helpers.

### Integration Points
`ivpu_hw.c` uses this layer for platform/frequency info, power transitions, reset, idle checks, telemetry boot params, IRQ dispatch, and diagnostics. Debugfs/PM use DCT and profiling-related hooks.

### Risks
MTL and LNL semantics differ: interrupt clear behavior, PLL lock, CDYN, tile fuse, and platform registers are generation-specific. The diagnostic LNL helper reads `VPU_HW_BTRS_MTL_INTERRUPT_STAT` while using LNL masks, which is suspicious and should be reviewed against intended register offset. Workpoint request timeouts prevent boot. Fatal IRQ handling must clear sources before status to avoid retrigger storms.

### Test Signals
Test fuse parsing, PLL clamp parameters, workpoint enable/disable, D0i3 transitions, IP reset, idle polling, MTL interrupt-clear workaround detection, ATS/UFI/CFI/IMR/SURV IRQ handling, DCT mailbox parsing, telemetry reads, and PM recovery triggers.
