# sources/distributed-fs/ceph-client/arch/m68k/ifpsp060/fskeleton.S

Purpose: adapts the Motorola 68060 Floating-Point Software Package to Linux/m68k. It defines OS call-outs, public FPSP entry stubs, a 128-byte call-out table, and includes the converted `fpsp.sa` package body.

Important APIs/types/functions: exported call-outs include `_060_fpsp_done`, `_060_real_ovfl`, `_060_real_unfl`, `_060_real_operr`, `_060_real_snan`, `_060_real_dz`, `_060_real_inex`, `_060_real_bsun`, `_060_real_fline`, `_060_real_fpu_disabled`, and `_060_real_trap`. Exported entry stubs include `_060_fpsp_snan`, `_060_fpsp_operr`, `_060_fpsp_ovfl`, `_060_fpsp_unfl`, `_060_fpsp_dz`, `_060_fpsp_inex`, `_060_fpsp_fline`, `_060_fpsp_unsupp`, and `_060_fpsp_effadd`.

Control flow: normal FPSP completion branches to `_060_isp_done`. Real enabled FP exceptions mostly `fsave`, write `0x6000` into the state frame, `frestore`, and branch to the generic `trap` handler. BSUN clears the NaN bit in FPSR before trapping. FPU-disabled call-out clears the PCR FPU-disabled bit, copies the causing instruction PC into the current PC slot, and returns with `rte`. Entry stubs branch to fixed offsets after `_FP_CALL_TOP+0x80`. `_FP_CALL_TOP` contains relative offsets to call-outs and memory access routines, then `fpsp.sa` is included.

State and persistence: no persistent state. Runtime state is the exception stack/FPU state frame, FPSR/PCR, and the static call-out table consumed by the package.

Dependencies/integration: includes `<linux/linkage.h>` and `fpsp.sa`; references `_060_isp_done`, `trap`, `_060_real_trace`, `_060_real_access`, and memory call-outs implemented in `os.S`.

Risks: the call-out section must remain exactly 128 bytes as required by the Motorola package. Fixed branch offsets are ABI with `fpsp.sa`; adding entries or changing order breaks package calls. The sample real exception handlers are generic trap bridges rather than rich Linux signal-specific implementations.

Test signals: assemble/link with `fpsp.sa`, invoke each `_060_fpsp_*` vector, verify call-out table size/order, enabled FP exceptions reach `trap`, FPU-disabled path re-enables PCR and resumes, and BSUN clears FPSR NaN before handling.
