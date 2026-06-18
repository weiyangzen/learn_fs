# sources/distributed-fs/ceph-client/arch/m68k/fpsp040/fpsp.h

Purpose: shared assembly equate header for the Motorola 68040 FPSP. It defines the stack frame, local variable, fsave frame, FPSR/FPCR, tag, and exception-vector offsets used by all FPSP assembly files.

Important definitions: `LOCAL_SIZE`, `USER_DA`, `USER_FP0..USER_FP3`, `USER_FPCR`, `USER_FPSR`, `USER_FPIAR`, scratch areas `FP_SCR*`/`L_SCR*`, flags such as `STORE_FLG`, `BINDEC_FLG`, `DNRM_FLG`, `CU_ONLY`, fsave offsets such as `WBTEMP`, `FPTEMP`, `ETEMP`, `CMDREG1B`, `CMDREG2B`, `STAG`, `DTAG`, exception frame offsets `EXC_SR/PC/VEC/EA`, FPSR masks, FPCR rounding/precision modes, tag constants, and fsave frame sizes/versions.

Control flow and state: no executable code. It specifies the memory contract established by FPSP handlers after `link a6,#-LOCAL_SIZE`, `fsave`, saving D/A and FP registers, and saving user FPCR/FPSR/FPIAR. All assembly routines read/write state through these offsets before restoring on exit.

Dependencies and integration: every file in `fpsp040` must agree with these offsets. It also encodes hardware frame formats and exception vector constants used when transforming fsave frames.

Risks and test signals: any offset change without coordinated assembly updates corrupts user registers or exception frames. Test by building all FPSP objects and running broad FPU exception suites that cover unimplemented, underflow, overflow, inexact, NaN, packed decimal, and store-result paths.
