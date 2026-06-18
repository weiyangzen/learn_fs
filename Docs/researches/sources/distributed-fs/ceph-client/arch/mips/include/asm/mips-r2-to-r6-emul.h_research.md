# sources/distributed-fs/ceph-client/arch/mips/include/asm/mips-r2-to-r6-emul.h

Purpose: Interface for emulating removed or changed MIPS Release 2 instructions on Release 6 CPUs.

Important APIs/types/functions: `struct mips_r2_emulator_stats` and `struct mips_r2br_emulator_stats` record per-instruction emulation counts when `CONFIG_DEBUG_FS` is enabled. `MIPS_R2_STATS(M)` and `MIPS_R2BR_STATS(M)` enumerate statistic fields or compile to no-ops. `struct r2_decoder_table` maps instruction masks and encodings to handler functions. Exposes `do_trap_or_bp()`, `mipsr2_decoder()`, `mipsr2_emulation`, and `NO_R6EMU`.

Control flow, state, and persistence: On a reserved-instruction/trap path, decoder code matches instruction words against tables, invokes handlers, updates optional debugfs stats, and can raise trap/breakpoint signals. State includes `mipsr2_emulation` policy and debug counters.

Dependencies and integration: Depends on `struct pt_regs`, signal/trap handling, debugfs configuration, CPU feature macros, and R6 exception paths.

Risks and test signals: Incorrect decode masks can emulate the wrong instruction or skip needed traps. Test with R6 kernels running R2 user binaries, debugfs stat increments, disabled-emulation `NO_R6EMU` behavior, and signal delivery for unhandled instructions.
