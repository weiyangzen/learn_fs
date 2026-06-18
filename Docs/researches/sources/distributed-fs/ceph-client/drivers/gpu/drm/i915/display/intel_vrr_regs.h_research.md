# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vrr_regs.h

### Purpose
`intel_vrr_regs.h` defines MMIO addresses and bitfields for VRR timing generator control, status, push, Adaptive Sync SDP timing, CMRR, and DC-balance adjustment/live registers.

### Important APIs, Types, And Functions
Key macros include `TRANS_VRR_CTL`, `TRANS_VRR_VMAX`, `TRANS_VRR_VMIN`, `TRANS_VRR_FLIPLINE`, `TRANS_VRR_STATUS`, `TRANS_PUSH`, `TRANS_VRR_VSYNC`, `EMP_AS_SDP_TL`, CMRR M/N register selectors, and DCB config/live selectors for adjusted flipline/vmax and final flipline/vmax. Bit helpers cover VRR enable, flipline enable, CMRR enable, DCB adjustment enable, pipeline-full or Xe_LPD guardband fields, status FSM bits, push send/enable bits, and AS SDP line fields.

### Control Flow
There is no executable flow. `intel_vrr.c` uses these macros to compose timing-control values, poll status, send push commands, program AS SDP positions, and read live DCB adjustment registers.

### State, Persistence, And Dependencies
State persists in transcoder MMIO and DCB live/config register blocks. The header depends on `intel_display_reg_defs.h` for transcoder MMIO selection and bitfield macros.

### Integration Points
Integrated with VRR enable/disable, DSB push scheduling, vblank safe-window logic, PSR frame-change pushes, DMC DC-balance support, and CMRR read/write code.

### Risks
Transcoder register selection must match the active CPU transcoder. Several fields are 13-, 16-, or 20-bit line counters; invalid values can truncate timings. Live DCB registers use different offsets from config registers, and mixing them would break vblank scheduling. Platform-specific interpretation of `VRR_CTL` fields is handled outside this header and must stay aligned.

### Test Signals
MMIO traces during VRR enable/disable, status polling on disable, DSB push-send clearing, AS SDP timing validation, DCB live-register readback, and platform coverage from Gen12 through newer always-VRR-TG platforms are useful.
