# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/kvm_fpu.h

Purpose: declares software floating-point helpers used by KVM instruction emulation for single-precision, double-precision, compare, fused multiply-add/subtract, select, sign, conversion, and square-root/reciprocal operations.

Important APIs/types/functions: single-precision helpers include `fps_fres`, `fps_frsqrte`, `fps_fsqrts`, `fps_fadds`, `fps_fdivs`, `fps_fmuls`, `fps_fsubs`, `fps_fmadds`, `fps_fmsubs`, `fps_fnmadds`, `fps_fnmsubs`, and `fps_fsel`. Macro families declare double-precision `fpd_*` helpers, plus `fpd_fcmpu`, `fpd_fcmpo`, `kvm_cvt_fd`, and `kvm_cvt_df`.

Control flow: instruction emulation decodes an FP instruction, passes FPSCR/CR and source/destination register storage to the matching helper, and the helper updates destination bits plus FPSCR/CR exception/condition state.

State and persistence: helpers mutate caller-provided FPSCR, CR, and FPR storage. This header does not hold state.

Dependencies and integration points: used by PowerPC KVM emulator code and depends on Linux integer types. It bridges guest FP instruction semantics to softfloat-like implementation files.

Risks: bit-exact IEEE/PPC FPSCR behavior is hard to preserve. Passing the wrong 32-bit/64-bit register slice or failing to update CR for compare operations causes guest-visible arithmetic bugs.

Test signals: KVM FP instruction emulation tests, guest libm/compiler FP test suites, FPSCR exception flag checks, compare CR-field validation, and cross-checks against hardware execution for representative operations.
