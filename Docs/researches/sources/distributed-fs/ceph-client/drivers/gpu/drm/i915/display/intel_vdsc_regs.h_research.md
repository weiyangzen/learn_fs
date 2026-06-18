# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/display/intel_vdsc_regs.h

### Purpose
`intel_vdsc_regs.h` defines the MMIO addresses and bitfield helpers for Intel VDSC, display stream splitter, joiner, PPS, RC threshold/range, and Lunar Lake selective-update parameter registers. It is the register contract consumed by `intel_vdsc.c` and related display code.

### Important APIs, Types, And Functions
The header defines `DSS_CTL1/2`, pipe-local `ICL_PIPE_DSS_CTL1/2`, joiner bits such as `BIG_JOINER_ENABLE`, `PRIMARY_BIG_JOINER_ENABLE`, `ULTRA_JOINER_ENABLE`, and VDSC engine enable bits. It also defines PPS register selectors (`DSCA_PPS`, `DSCC_PPS`, `ICL_DSC0_PPS`, `ICL_DSC1_PPS`, `BMG_DSC2_PPS`) and field macros for PPS 0-10, 16, 17, and 18. RC buffer threshold and range parameter register groups are declared for DSCA/DSCC and pipe-local ICL DSC engines.

### Control Flow
There is no executable flow. Callers compose register values with `REG_FIELD_PREP()` macros and select address families based on whether DSC is pipe-local or transcoder/shared. The PPS macros encode the register spacing where PPS indices after 11 have gaps on DSCA/DSCC but not pipe-local ICL/BMG engines.

### State, Persistence, And Dependencies
State persists in hardware registers. This header depends on `intel_display_reg_defs.h` for `_MMIO`, `_MMIO_PIPE`, `_PICK_EVEN`, `REG_BIT`, and `REG_GENMASK`. It does not store driver state.

### Integration Points
`intel_vdsc.c` uses these definitions to program PPS, RC thresholds, RC ranges, DSS joiner controls, and PSR SU DSC parameters. Joiner bits interact with bigjoiner/ultrajoiner pipe composition and uncompressed joiner support.

### Risks
Incorrect address selection can program the wrong engine, especially around pipe B/C offsets and BMG DSC2. Field-width errors in PPS macros can truncate DSC parameters. The DSCA/DSCC PPS index gap is easy to overlook. Joiner bit combinations must stay synchronized with `intel_vdsc.c` topology logic.

### Test Signals
Register write traces, display engine register dumps, DSC PPS readback comparisons, multi-engine DSC bring-up, and BMG/MTL/LNL platform coverage are useful. Static build coverage catches macro name drift but not wrong offsets.
