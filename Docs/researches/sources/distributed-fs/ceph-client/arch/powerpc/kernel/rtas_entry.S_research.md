# sources/distributed-fs/ceph-client/arch/powerpc/kernel/rtas_entry.S

Purpose: low-level assembly trampoline that enters RTAS firmware with MMU translation and external interrupts disabled, then restores kernel execution state after firmware returns.

Important APIs/types/functions: exported assembly symbols `enter_rtas`, 64-bit helper labels `__enter_rtas`, `rtas_return_loc`, and `rtas_restore_regs`; 32-bit path saves LR/MSR/stack state in the thread `RTAS_SP`; 64-bit path saves TOC, nonvolatile GPRs, CR/CTR/XER/DAR/DSISR, stack pointer, and MSR in PACA fields.

Control flow: on PPC32 the routine creates an interrupt frame, loads RTAS entry/base from the global `rtas` struct, builds a physical return address, writes SRR0/SRR1 with the firmware entry and real-mode MSR, and uses `rfi` to enter firmware. On return it briefly re-enters translated kernel mode with a second `rfi`, restores LR/MSR/stack, clears the per-thread RTAS stack marker, and returns to C. On PPC64 the routine saves full kernel state because 32-bit RTAS may clobber upper register halves, clears CR as a firmware workaround, stores original stack/MSR in the PACA, computes real-mode return code, enters RTAS through `RFI_TO_KERNEL`, fixes endian on return, restores SF/translation through another RFI, then reloads saved registers and returns.

State and persistence: this file does not persist application data, but it temporarily mutates PACA save slots, SRR registers, LR, MSR, CR, and stack frames. It depends on the C-side caller holding the correct RTAS serialization and passing a physical RTAS argument block in `r3`.

Dependencies and integration points: called only through `rtas.c` (`do_enter_rtas()`), and relies on offsets from `asm-offsets.h`, PACA layout, RTAS base/entry fields, exception/real-mode macros, and endian-fixup support. The C caller invalidates SRR tracking after return because firmware uses SRRs.

Risks: any offset drift, wrong MSR bit composition, missing register save, or endian mismatch can crash the kernel or return with corrupted state. RTAS may be entered during machine-check paths on pSeries, so the real-mode and RI/HV handling must remain precise. The assembly must remain nokprobe-safe and non-instrumented.

Test signals: ppc32 and ppc64 boot tests on RTAS firmware, kernel selftests or smoke paths that perform RTAS calls, suspend/reboot/poweroff exercising return paths, and stress tracing plus machine-check/stop-self scenarios to catch missing state restoration.
