# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/include/asic_reg/dce/dce_12_0_sh_mask.h lines 7316-9643

## Purpose

This chunk is a generated AMD DCE 12.0 display-engine register shift/mask header segment. It contains no executable C logic; its public surface is a dense set of `#define` constants named as `<REGISTER>__<FIELD>__SHIFT` and `<REGISTER>__<FIELD>_MASK`. Driver code uses these symbols to compose, update, and decode memory-mapped display-controller registers without embedding raw bit positions or masks directly at call sites.

The assigned range starts in the tail of the `DAC_FIFO_STATUS` field definitions and then covers the main DCE display I2C/DDC control block, generic I2C access, display interrupt status continuation banks, DCO/DCIO power-clock-reset controls, display-output PHY link routing, panel power sequencing and backlight PWM registers, global swaplock/genlock routing, GPU timer readback, external VSYNC routing, and the beginning of DCIO/UNIPHY/AUX impedance calibration fields. The chunk ends mid-register at `DCIO_IMPCAL_CNTL_CD__IMPCAL_ARB_STATE__SHIFT`; the matching masks and any later calibration fields are owned by the next chunk.

The constants are hardware ABI definitions. Their purpose is to preserve exact bitfield layout for the DCE 12.0 ASIC register interface used by AMDGPU display code.

## Important APIs, Types, and Register Domains

There are no functions, structs, typedefs, or runtime APIs in this chunk. The important API surface is the generated macro namespace consumed by AMDGPU/DC register helpers. Every register field generally appears as a pair:

- `*_SHIFT`: the starting bit position for a field.
- `*_MASK`: the full pre-shifted mask used to isolate or update the field.

Major register domains in this range:

- `DAC_FIFO_STATUS`: tail fields for FIFO overwrite level, calibrated average/min/max level, calibration status, and force-recalibration/recompute bits. The chunk begins after the first few `DAC_FIFO_STATUS` shift definitions, so the full register definition spans the previous chunk and this one.
- `DC_I2C_*`: display-controller I2C engine control, arbitration, interrupt control, software status, DDC hardware status, bus speed/setup for DDC1-DDC6 and DDCVGA, multi-transaction descriptors, data FIFO/index access, EDID detect control, and read-request interrupt bits.
- `GENERIC_I2C_*`: a parallel generic I2C engine with control, interrupt, status, speed/setup, transaction, data, and pin-selection fields.
- `DCO_SCRATCH0` through `DCO_SCRATCH7`: raw 32-bit scratch registers represented by full-width value masks.
- `DCE_VCE_CONTROL`: VCE clock gating and display/VCE memory request behavior.
- `DISP_INTERRUPT_STATUS` and `DISP_INTERRUPT_STATUS_CONTINUE*`: display interrupt summary/status banks, including continuation-chain bits. These cover CRTC/vblank/vline/snapshot/trigger interrupts, SCL mode changes, blender underflows, DIG/DP fast-training and stream-disable events, HPD and HPD RX events, AUX software/light-sleep/GTC sync events, performance monitor counter interrupts, CWB buffer-manager interrupts, static-screen interrupts, generic DCO/PSP interrupts, and HDCP/AUX register-ready interrupts.
- `DCO_MEM_PWR_STATUS`, `DCO_MEM_PWR_STATUS1`, `DCO_MEM_PWR_CTRL`, and `DCO_MEM_PWR_CTRL2`: memory power status and light-sleep/shutdown/force controls for I2C, MVP, DPA-DPG, HDMI0-HDMI6, DMIF pipe memories, MCIF writeback memories, DCRX, and DCFEV memories.
- `DCO_CLK_CNTL`, `DCO_CLK_CNTL2`, and `DCO_CLK_CNTL3`: clock enable/disable and power-domain controls for display blocks such as DCO, DPP, DMIF, DCF, FBC, GPIO, HDCP, I2C, DCI, DCCG, ABM, APG, BLND, CWB, MCIFWB, DCRX, DCFEV0/1, and SCLV.
- `DCO_POWER_MANAGEMENT_CNTL`, `DCO_SOFT_RESET`, `DIG_SOFT_RESET`, and `DIG_SOFT_RESET_2`: power-management guard and soft reset controls for DCO, DCO performance, DIGA-DIGG, DP AUX engines, DCO audio, DCO memory power FSM, DCFEV front ends, DPREF clocking, and PHY-specific digital paths.
- `DCO_STEREOSYNC_SEL`, `DCO_DCFE_EXT_VSYNC_CNTL`, `DC_GENERICA`, `DC_GENERICB`, `DCIO_GSL_*`, and `DC_GPU_TIMER_*`: synchronization, generic interrupt, swaplock/genlock/GSL, CRTC external VSYNC, and GPU-timer start/readback bitfields.
- `FMT_MEMORY0_CONTROL` through `FMT_MEMORY5_CONTROL`: per-formatter memory power status, shutdown control, and light-sleep disable controls.
- `UNIPHYA_LINK_CNTL` through `UNIPHYG_LINK_CNTL` and matching `*_CHANNEL_XBAR_CNTL`: per-UNIPHY link controls for pixel-valid reset, minimum low duration, per-channel inversion, lane-stagger delay, HPD-mask based link enable, channel crossbar lane source selection, and link enable.
- `DCIO_WRCMD_DELAY`, `DC_DVODATA_CONFIG`, `DC_PAD_EXTERN_SIG`, `DC_REF_CLK_CNTL`, `DC_GPIO_DEBUG`, and `DCIO_CLOCK_CNTL`: write-command delay tuning, DVO/VIP alternate mapping, external-pad signal select, reference-clock gating, GPIO debug routing, and DCIO test-clock/gating fields.
- `LVTMA_PWRSEQ_*` and `BL_PWM_*`: embedded panel/power-sequencer controls for target state, DIGON/SYNCEN/BLON polarity and override, power-up/down delay programming, reference dividers, PWM duty/period, PWM enable, and group register lock/update behavior.
- `DCIO_SOFT_RESET` and `DCIO_DPHY_SEL`: resets for UNIPHY/DSYNC A-G, DAC, DCRXPHY, DPHY, ZCAL, LPA/LPB paths, plus DPHY lane source selection.
- `UNIPHY_IMPCAL_LINKA/B/C/D`, `UNIPHY_IMPCAL_PERIOD`, `UNIPHY_IMPCAL_PSW_AB`, `AUXP_IMPCAL`, `AUXN_IMPCAL`, `DCIO_IMPCAL_CNTL`, and partial `DCIO_IMPCAL_CNTL_CD`: impedance calibration enable/status/error/override/step-delay/value controls for UNIPHY and AUX pads, calibration period and power-switch values, global calibration soft reset/status/arbitration state, and AUX calibration interval.

## Control Flow and State Behavior

This header has no direct control flow. The effective flow is in consumers that use these symbols with MMIO helpers to perform read-modify-write updates, poll status bits, or acknowledge hardware events.

Stateful hardware behavior encoded by the masks includes:

- I2C/DDC transaction sequencing: `DC_I2C_CONTROL__DC_I2C_GO`, `*_SOFT_RESET`, `*_SEND_RESET`, `*_SW_STATUS_RESET`, DDC selection, transaction count, transaction start/stop/read/write/count fields, and indexed data access describe how software stages I2C transactions and starts hardware execution.
- I2C ownership and arbitration: `DC_I2C_ARBITRATION` fields distinguish software and DMCU ownership requests/done signals, software priority, queued-go behavior, and software/hardware transfer aborts.
- I2C completion/error state: software and hardware status fields expose done, aborted, timeout, interrupted, overflow, NACK, request, urgent, EDID detect status, number of valid detect tries, and EDID detect state. These are read by polling paths and interrupt handlers.
- Interrupt aggregation: `DISP_INTERRUPT_STATUS*` fields form a chained summary tree. The continuation bit at bit 31 in many banks indicates another status register has active bits, so interrupt walkers must follow the chain rather than checking only the root register.
- Power and clock state: memory power status and control fields track or force light sleep/shutdown for DCO sub-block memories. Clock-control bits enable, disable, or power down display sub-block clocks. These are persistent hardware states until rewritten or reset by power-management paths.
- Reset sequencing: DCO, DIG, and DCIO soft reset fields can hold sub-blocks in reset. Callers must assert and release them in hardware-defined order around PHY/link/power transitions.
- Link routing and lane state: UNIPHY channel crossbar and inversion fields persistently define how logical lanes map to physical channels, which links are enabled, and whether HPD masking participates in link enable. These values are central to connector bring-up.
- Panel sequencing and backlight PWM: LVTMA and BL PWM fields describe staged panel power-up/power-down, backlight enable, override, polarity, duty cycle, period, and double-buffered update locking. `BL_PWM_GRP1_REG_UPDATE_PENDING` is a latch/status signal for safe brightness updates.
- Synchronization and timing: genlock/swaplock/GSL select fields, external VSYNC mux fields, GPU timer start-position fields, and CRTC manual-flow-control bits determine how display pipes synchronize timing, flips, and timer capture.
- Impedance calibration: UNIPHY/AUX calibration fields initiate calibration, report calout/error status, acknowledge error, set step delays, override measured values, and choose calibration targets. These influence electrical characteristics and must be managed with reset/PHY state.

Persistence is entirely in hardware registers after driver writes. The macros themselves have no memory ownership, allocation, locking, I/O, or persistent on-disk state.

## Dependencies and Integration Points

This chunk has no `#include` dependencies and no standalone compile unit. It depends on generated register-address headers for the matching DCE 12.0 register offsets and on the companion enum/value headers for legal field encodings. It is tightly coupled to the AMD DCE 12.0 hardware specification and to AMDGPU display code that uses generated `*_SHIFT`/`*_MASK` names in register-programming macros.

Expected integration points include:

- Display I2C/DDC and EDID probing code uses `DC_I2C_*`, `GENERIC_I2C_*`, and DDCVGA/DDC1-DDC6 speed/setup/status fields for monitor detection, EDID reads, AUX/DDC fallback paths, and DMCU/software arbitration.
- Interrupt handlers and diagnostics use `DISP_INTERRUPT_STATUS*` fields to route vblank/vline, CRTC trigger, underflow, HPD, AUX, DP, performance monitor, CWB, HDCP, static-screen, PSP, and generic interrupt events.
- Display power-management and clock-gating code uses `DCO_MEM_PWR_*`, `DCO_CLK_CNTL*`, `DCO_POWER_MANAGEMENT_CNTL`, formatter memory controls, and DCO/DCIO reset registers during suspend/resume, mode set, idle gating, and hardware bring-up.
- Link encoder and PHY setup code uses `UNIPHY*_LINK_CNTL`, `UNIPHY*_CHANNEL_XBAR_CNTL`, `DCIO_SOFT_RESET`, `DIG_SOFT_RESET*`, `DCIO_DPHY_SEL`, `DCIO_WRCMD_DELAY`, and impedance calibration fields during DisplayPort/HDMI/eDP link initialization.
- Panel/backlight code uses `LVTMA_PWRSEQ_*`, `BL_PWM_*`, and `DC_REF_CLK_CNTL` to sequence embedded panel power and apply backlight updates.
- Multi-display synchronization and flip-timing code uses `DCO_STEREOSYNC_SEL`, `DCIO_GSL_*`, `DCO_DCFE_EXT_VSYNC_CNTL`, and `DC_GPU_TIMER_*`.
- Debug and firmware/secure-processor paths can consume DCO scratch registers, DCO generic interrupt message/clear fields, DCO PSP interrupt status/clear, GPIO debug selection, and VCE/display memory request controls.

## Risks and Edge Cases

- Bit masks and shifts are hardware ABI. Any numeric change can silently program the wrong register bits even if the kernel still compiles.
- The chunk boundaries are not semantic boundaries. `DAC_FIFO_STATUS` starts in the previous chunk, and `DCIO_IMPCAL_CNTL_CD` continues in the next chunk. Per-file synthesis must merge adjacent chunks before treating either register family as complete.
- Many repeated register families differ only by instance number, for example DDC1-DDC6, DIGA-DIGG, DPA-DPG, CRTC1-CRTC6, UNIPHYA-UNIPHYG, HDMI0-HDMI6, and DCFE0-DCFE5. Mechanical copy errors in generated headers or hand edits could map a field to the wrong instance while preserving a plausible mask pattern.
- Interrupt continuation bits use bit 31 in many status registers. Interrupt handling that ignores continuation bits can miss events in later banks; code that assumes every bit is a leaf event can misinterpret the continuation flag.
- Some status names encode historical spelling from hardware documentation, such as `OCCURED`. These names should not be corrected locally unless all generated headers and call sites are regenerated together.
- Mask polarity is not uniform. Fields named `*_MASK`, `*_DIS`, `*_GATE_DIS`, `*_LIGHT_SLEEP_DIS`, `*_FORCE`, `*_OVRD`, and `*_ACK` have different semantics even though they are all represented as masks. Callers must follow the register meaning, not infer boolean polarity from the C macro pattern.
- I2C arbitration exposes software and DMCU ownership. Incorrect request/done ordering or failure to abort/reset on error can stall EDID/DDC access or conflict with firmware.
- Panel power and backlight controls have ordering requirements outside this header. Misprogramming target state, delay fields, polarity, or override bits risks blank panels, flicker, or unsafe panel sequencing.
- Clock, memory power, and soft reset controls are cross-domain. Gating or resetting an active block can cause underflows, link loss, stuck interrupts, or failed resume.
- Impedance calibration override and error acknowledgement fields affect PHY electrical behavior. Forced override values or mishandled calibration errors can produce marginal DisplayPort/HDMI/AUX signaling.
- Full-width masks such as scratch registers, timer reads, calibration periods, and I2C data/count fields need correct value range validation at call sites; the header only exposes field layout.

## Test Signals

Useful validation is mainly compile-time plus hardware-facing display behavior:

- Kernel build or targeted header inclusion should catch syntax errors, duplicate macro definitions, and missing generated identifiers used by AMDGPU/DC code.
- Static checks can compare selected `*_SHIFT` and `*_MASK` pairs against expected DCE 12.0 register documentation, especially for repeated DDC, interrupt, UNIPHY, and power-control families.
- EDID/DDC tests should cover DDC1-DDC6 and DDCVGA selection, normal read completion, NACK handling, timeout handling, software status reset, transaction chaining, and arbitration with firmware/DMCU users.
- Hotplug and AUX/DP tests should verify HPD, HPD RX, AUX SW done, AUX LS done, AUX GTC sync lock/error, DP fast-training complete, and DP stream-disable interrupt reporting through the continuation chain.
- Display mode-set and page-flip tests should exercise vblank/vline, CRTC trigger/snapshot/force-count interrupts, blender underflow status, GPU timer start/readback, external VSYNC routing, genlock/swaplock, and GSL selections.
- Suspend/resume and runtime power-management tests should inspect DCO memory power status, light-sleep/shutdown force bits, clock gating controls, formatter memory controls, and soft reset sequencing.
- Embedded panel tests should validate LVTMA power-up/down delays, DIGON/SYNCEN/BLON state, PWM period/duty programming, frame-start update behavior, and backlight group-lock update pending behavior.
- Link bring-up tests should cover UNIPHY lane crossbar/inversion programming, link-enable behavior, DCIO/DIG soft resets, DPHY lane selection, and UNIPHY/AUX impedance calibration status/error handling.
