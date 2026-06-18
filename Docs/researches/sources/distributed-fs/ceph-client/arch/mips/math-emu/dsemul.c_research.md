# sources/distributed-fs/ceph-client/arch/mips/math-emu/dsemul.c

Purpose: implements branch delay-slot emulation by placing a tiny `struct emuframe` in a per-process user page at `STACK_TOP`. The frame contains the instruction to execute and a `BREAK_MATH` instruction that returns control to the kernel. This avoids full instruction emulation while keeping execution in user privilege.

Important APIs and functions: `mips_dsemul()` allocates/fills a frame and redirects `regs->cp0_epc`; `do_dsemulret()` handles the break return; `dsemul_thread_cleanup()` frees a thread-owned frame; `dsemul_thread_rollback()` rewinds EPC during signal/exception paths; `dsemul_mm_cleanup()` releases the mm bitmap. The `emuframe` allocation state lives in `mm->context.bd_emupage_allocmap` protected by `bd_emupage_lock`, with waiters on `bd_emupage_queue`.

Control flow: `mips_dsemul()` fast-paths NOP and microMIPS `ADDIUPC`, otherwise allocates or reuses a frame, writes it with `access_process_vm(FOLL_FORCE|FOLL_WRITE)`, records branch/continue PCs in `current->thread`, and sets EPC to the frame. On break, `do_dsemulret()` frees the frame and jumps to `bd_emu_cont_pc`.

Dependencies and integration: called by the MIPS FPU/branch emulator and trap paths; uses `asm/branch.h`, `asm/inst.h`, `asm/fpu_emulator.h`, user access helpers, task/mm context state, and MIPS ISA mode helpers.

Risks and test signals: correctness depends on not trusting user-created break frames, atomic frame ownership, signal rollback, microMIPS halfword encoding, and frame exhaustion wait behavior. Test with branch delay-slot FPU instructions, invalid delay-slot instructions, signals during emulation, fork/exit cleanup, and concurrent threads exhausting the emupage.
