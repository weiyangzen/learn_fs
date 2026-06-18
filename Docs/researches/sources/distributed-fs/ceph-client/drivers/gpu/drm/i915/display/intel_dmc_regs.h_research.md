# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_dmc_regs.h

### Purpose
`intel_dmc_regs.h` defines DMC and PipeDMC event IDs, MMIO register addresses, address remapping helpers, and bitfields used by firmware loading, event handler programming, flip queues, wakelocks, package C-state controls, and adaptive DCB.

### Important APIs, Types, And Functions
The file defines `enum dmc_event_id`, a large `enum maindmc_event_id` for main DMC firmware events, and `enum pipedmc_event_id` for per-pipe firmware events. Core macros include `DMC_PROGRAM()`, `PIPEDMC_CONTROL()`, `MTL_PIPEDMC_CONTROL`, `PIPEDMC_LOAD_HTP()`, `PIPEDMC_CTL()`, `PIPEDMC_STATUS()`, `PIPEDMC_FQ_CTRL()`, `PIPEDMC_FQ_STATUS()`, PipeDMC flip queue pointer/status registers, scanline compare registers, interrupt/mask registers, package C-state block register, DMC event handler registers (`DMC_EVT_HTP()`, `DMC_EVT_CTL()`), firmware program base constants, DMC debug counters, wakelock registers, flip queue RAM entry bitfields for LNL and PTL+, PipeDMC execution timing variables, and adaptive DCB control registers.

### Control Flow
There is no executable flow, but the macros encode several control paths. Firmware load writes program dwords through `DMC_PROGRAM(start, i)` and configures handler pairs through `DMC_EVT_CTL()` and `DMC_EVT_HTP()`. Pipe enable/disable uses `PIPEDMC_CONTROL()` or `MTL_PIPEDMC_CONTROL`. Flip queue code programs RAM entries and tail/head pointers through `PIPEDMC_FPQ_*` registers. Interrupt handling reads/acks `PIPEDMC_INTERRUPT()` and checks `PIPEDMC_STATUS()`. Wakelock code toggles `DMC_WAKELOCK_CFG` and `DMC_WAKELOCK1_CTL`. DCB code writes the `PIPEDMC_DCB_*` register set.

### State, Persistence, And Dependencies
The header has no software state; it describes persistent hardware state in display MMIO. `_DMC_REG_MMIO_BASE()` and `_DMC_REG()` remap the main-DMC register layout to per-pipe DMC address spaces, with display-version-dependent PipeDMC bases. It depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, `_PICK_EVEN`, `REG_BIT`, field masks, and related register helpers.

### Integration Points
`intel_dmc.c` uses the firmware program, event, PipeDMC control, interrupt, package C-state, debug counter, and DCB definitions. `intel_dmc_wl.c` uses the wakelock registers. Flip queue code uses the FPQ register and RAM entry definitions. Power-management and debug code use DC counter and debug registers. This header is therefore the shared hardware contract across several display subsystems.

### Risks
Register definitions mix multiple hardware generations, so choosing the wrong base or display-version path can program unrelated MMIO. Event IDs are firmware ABI values; changing them breaks DMC event routing. Several macros are address factories and must be passed valid pipe/DMC IDs. The PipeDMC FPQ helper uses queue-id picking logic that assumes queue enum ordering. Magic undocumented PTL DMC variables are explicitly fragile. A typo-like macro form for `PIPEDMC_FPQ_LINES_TO_W1` and `PIPEDMC_FPQ_LINES_TO_W2` references `pipe` without a formal macro parameter, so use sites must be checked closely.

### Test Signals
Signals include successful DMC firmware load and event readback, PipeDMC enable/disable on every valid pipe, flip queue programming and completion on LNL/PTL+ formats, wakelock request/ack behavior, adaptive DCB enable/disable through DSB, package C-state workaround behavior, and register trace comparisons against hardware programming guides for each generation.
