# sources/distributed-fs/ceph-client/arch/sparc/include/asm/thread_info_64.h

Purpose: sparc64 `thread_info` layout with packed flag/status bytes, saved windows, FPU/VIS register storage, utraps, fault metadata, and assembly offsets.

Important APIs/types/functions: types `task_struct`, `thread_info`; functions/helpers `asm`; macros/constants `_ASM_THREAD_INFO_H`, `NSWINS`, `TI_FLAG_BYTE_FAULT_CODE`, `TI_FLAG_FAULT_CODE_SHIFT`, `TI_FLAG_BYTE_WSTATE`, `TI_FLAG_WSTATE_SHIFT`, `TI_FLAG_BYTE_NOERROR`, `TI_FLAG_BYTE_NOERROR_SHIFT`, `TI_FLAG_BYTE_FPDEPTH`, `TI_FLAG_FPDEPTH_SHIFT`, `TI_FLAG_BYTE_CWP`, `TI_FLAG_CWP_SHIFT`, `TI_FLAG_BYTE_WSAVED`, `TI_FLAG_WSAVED_SHIFT`, `TI_TASK`, `TI_FLAGS`, `TI_FAULT_CODE`, `TI_WSTATE`, plus 77 more.

Control flow: The file is driven by preprocessor gates such as `_ASM_THREAD_INFO_H`, `__KERNEL__`, `__ASSEMBLER__`, `PAGE_SHIFT == 13`, `BUILD_VDSO`. Callers normally reach it through generic Linux architecture hooks or SPARC wrapper headers, so behavior changes propagate into memory-management, TLB/MMU, syscall/ptrace, VDSO paths rather than through standalone functions.

State and persistence behavior: Per-task state persists in kernel stack/thread storage; high bytes of `flags` encode fault code, wstate, no-error, fpdepth, cwp, and wsaved for trap-return fast paths.

Dependencies and integration points: Includes/dependencies: `asm/page.h`, `asm/ptrace.h`, `asm/types.h`. Integration points include memory-management, TLB/MMU, syscall/ptrace, VDSO; many consumers rely on exact macro names matching Linux generic MM, scheduler, trap, PCI, signal, or VDSO contracts.

Risks and test signals: Main risks are register/window layout drift, MMU/TLB encoding regressions. Test signals: Trap return work masks, 32-bit compat flagging, FPU/VIS save/restore, MCD faults, utraps, and offset-generation checks are critical.
