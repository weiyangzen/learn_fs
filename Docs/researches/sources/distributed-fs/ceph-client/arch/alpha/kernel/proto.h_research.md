# sources/distributed-fs/ceph-client/arch/alpha/kernel/proto.h

## Purpose
`proto.h` is the internal Alpha kernel cross-file declaration hub. It collects prototypes, global variables, low-level assembly entry declarations, platform host-bridge hooks, SRM console hooks, SMP hooks, RTC hooks, trap/signal/ptrace functions, and machine-check helpers used among files in `arch/alpha/kernel`.

## Important APIs, Types, And Declarations
- Volatile pointer aliases `vucp`, `vusp`, `vip`, `vuip`, and `vulp` support memory-mapped register access in board files.
- Host bridge sections declare CIA/PYXIS, Irongate, Marvel, MCPCIA, Polaris, T2, Titan, Tsunami, and Wildfire operations including PCI ops, architecture init/kill, machine checks, and PCI TBI callbacks.
- Console declarations expose VGA hose discovery when `CONFIG_VGA_HOSE` is enabled.
- Setup globals include `srm_hae`, `boot_cpuid`, optional `alpha_verbose_mcheck`, `move_initrd()`, and `vgacon_screen_info`.
- SRM console declarations are conditional no-ops when unavailable.
- SMP declarations expose `setup_smp()`, `handle_ipi()`, and `smp_callin()`.
- RTC declarations expose `rtc_timer_interrupt()`, `init_clockevent()`, `common_init_rtc()`, and `est_cycle_freq`.
- Super I/O init declarations expose `SMC93x_Init()` and `SMC669_Init()`.
- Assembly/PAL declarations include FP register helpers, `wrmces`, console-service enable/disable, `__smp_callin`, and trap entry symbols.
- Ptrace/signal/trap declarations expose syscall tracing, signal returns, pending-work processing, register display, trap handlers, and unaligned access handlers.
- `__alpha_remap_area_pages()` builds Alpha kernel page protections and calls `ioremap_page_range()`.
- `mcheck_expected/taken/extra` macros abstract machine-check state for SMP and UP builds.

## Control Flow
The header has little direct flow. Its main executable helper, `__alpha_remap_area_pages()`, constructs a kernel read/write, ASM-valid `pgprot_t` and maps a physical range. The machine-check macros route to per-CPU `cpu_data` under SMP or a single `__mcheck_info` structure under UP.

## State And Persistence
The header declares shared global boot state and machine-check state but does not allocate most of it. The inline remap helper changes kernel page tables through generic ioremap APIs. All state is volatile kernel runtime state.

## Dependencies And Integration Points
Nearly every file in this subset includes `proto.h` for cross-module hooks. It depends on Linux interrupt, screen, and I/O headers plus Alpha-specific structures. It is especially coupled to `setup.c`, `smp.c`, `rtc.c`, `signal.c`, `ptrace.c`, trap handling, host bridge files, and board support vectors.

## Risks
- Because this is a broad internal declaration header, stale prototypes can hide cross-file ABI changes until link or runtime failures.
- Conditional no-op SRM/VGA helpers must match call-site expectations in generic builds.
- Low-level assembly prototypes need exact signatures; mismatches can corrupt registers or stack state.
- Machine-check state macros evaluate CPU arguments differently in SMP/UP builds, so side effects in arguments would be dangerous.

## Test Signals
- Full Alpha kernel build across generic, SMP, SRM, VGA, and board-specific configs.
- Link-time coverage for all weak or conditional symbols.
- Boot tests that exercise setup, trap, signal, ptrace, RTC, and SMP hooks.
- I/O remapping users successfully map and access expected physical ranges.
