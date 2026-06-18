## sources/distributed-fs/ceph-client/arch/arm/vfp/vfpinstr.h

### Purpose
Defines VFP instruction decoding masks, register extraction macros, FPSCR condition flags, and inline accessors for VFP system registers.

### Important APIs, Types, And Functions
Macros include `INST_CPRTDO`, `INST_CPRT`, `FOP_*`, `FEXT_*`, `vfp_get_sd/dd/sm/dm/sn/dn`, `vfp_single`, `FPSCR_N/Z/C/V`, `fmrx`, and `fmxr`. It declares `vfp_single_cpdo`, `vfp_single_cprt`, and `vfp_double_cpdo`.

### Control Flow
Consumers mask opcode fields to decide CPDO/CPRT class, precision, operation index, and register numbers. `fmrx`/`fmxr` emit VFP system-register transfer instructions.

### State, Persistence, And Dependencies
No storage is declared. It depends on ARM VFP instruction encoding and compiler support for inline assembly with `.fpu vfpv2`.

### Integration Points
Shared by VFP exception entry and the single/double emulators; it is the decode vocabulary for bounced VFP instructions.

### Risks
Incorrect bit masks route instructions to wrong emulation handlers or wrong registers. Inline system register access is privileged/context-sensitive and must only run when VFP access is enabled.

### Test Signals
Decode known instruction encodings, run CPDO/CPRT emulation tests, and build with GCC/Clang assemblers.
