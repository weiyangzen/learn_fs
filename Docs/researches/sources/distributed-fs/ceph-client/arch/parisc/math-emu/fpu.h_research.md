# sources/distributed-fs/ceph-client/arch/parisc/math-emu/fpu.h

Purpose: defines PA-RISC FPU capability flags and the emulator version field used by the floating-point instruction dispatcher.

Important APIs and types: flags include `PA83_FPU_FLAG`, `PA89_FPU_FLAG`, `PA2_0_FPU_FLAG`, `TIMEX_EXTEN_FLAG`, `ROLEX_EXTEN_FLAG`, `COPR_FP`, and `SFU_MPY_DIVIDE`. `EM_FPU_TYPE_OFFSET` gives the register-image offset where dispatch stores FPU type flags, and `EMULATION_VERSION` is returned for the `COPR,0,0` instruction.

Control flow: macro-only header. Runtime use is in `fpudispatch.c`, where `parisc_linux_get_fpu_type()` fills the type flag slot from `boot_cpu_data.cpu_type`, then decode logic gates PA1.1, PA2.0, Timex, and Rolex instruction forms.

State and persistence: this file declares constants only. Persistent state exists in the emulated FP register array at `EM_FPU_TYPE_OFFSET`, not in the header.

Dependencies and integration: uses firmware model key names for potential Timex and Rolex differentiation. `fpudispatch.c` depends on these flags for compare queue updates, fused/multi-op availability, and source-register decoding.

Risks: incorrect flag assignment changes instruction legality and status update semantics. The offset is expressed in bytes and later converted to a `u_int` index, so structure-layout drift in the register image is risky.

Test signals: validate emulator version reporting, CPU-type-to-flag mapping for pcxs, pcxt, pcxt_, and pcxu-or-newer, plus decode behavior for PA2.0-only conversions and Timex/Rolex FMPYCFXT paths.
