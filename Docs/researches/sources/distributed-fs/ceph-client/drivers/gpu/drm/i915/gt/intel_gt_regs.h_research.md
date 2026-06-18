# sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_regs.h

## sources/distributed-fs/ceph-client/drivers/gpu/drm/i915/gt/intel_gt_regs.h

### Purpose
`intel_gt_regs.h` is the GT register definition catalog. It defines MMIO and MCR register offsets and bitfields for GT clocks, MCR steering, context state, workaround registers, performance counters, fault reporting, PAT/MOCS, CCS mode, PM/RPS/RC6, forcewake, interrupt registers, media offsets, and many generation-specific chicken/debug registers.

### Important APIs, Types, And Functions
The file is macro-only. Important groups include `MTL_MIRROR_TARGET_WP1`, `RPM_CONFIG0`, MCR selector/semaphore fields, context-size registers, ring fault and TLB fault registers, PAT and MOCS macros, XeHP/Xe_LPG MCR registers, RPS/RC6 registers, `XEHP_CCS_MODE`, forcewake ack/control registers, Gen11+ interrupt enable/mask/identity registers, and `MTL_MEDIA_GSI_BASE`.

### Control Flow
There is no direct control flow. Other GT files use these macros to select registers and bit masks for platform-specific read/write/RMW operations. Some macros compute offsets from engine class, PAT/MOCS index, stream index, or CCS slice.

### State, Persistence, And Dependencies
The header stores no runtime state. It depends on `i915_reg_defs.h` and its `_MMIO`, `MCR_REG`, `REG_BIT`, `REG_GENMASK`, and field-prep helpers.

### Integration Points
This header feeds almost every GT subsystem: initialization, workarounds, MCR, PM, IRQ, RPS/RC6, renderstate/context setup, debugfs/sysfs, fault clearing, and media GT support.

### Risks
Incorrect offsets or masks can corrupt hardware state, break interrupts, misdecode faults, or apply workarounds to the wrong register. MCR registers must be accessed through MCR helpers even though they are defined next to normal MMIO registers. Generation comments and duplicate legacy fields require careful use.

### Test Signals
Hardware bring-up on supported generations, register read/write selftests, workaround verification, interrupt delivery, RPS/RC6 sysfs/debugfs output, MCR steering tests, and fault decode validation are the main signals.
