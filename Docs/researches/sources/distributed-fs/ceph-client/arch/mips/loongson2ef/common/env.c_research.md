<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/env.c -->
# sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/env.c

Purpose: Initializes Loongson2E/2F early environment variables from PMON firmware and CPU revision defaults.

Important APIs/types/functions: Exports `cpu_clock_freq`; `prom_init_env()` reads `cpuclock`, `memsize`, and `highmemsize` with `fw_getenvl()`.

Control flow: Firmware values are accepted first. Missing `memsize` defaults to 256 MiB. Missing `cpuclock` falls back by `processor_id` revision: 533.08 MHz for 2E, 797 MHz for 2F, and 100 MHz otherwise.

State and persistence: Populates global boot-time state `cpu_clock_freq`, `memsize`, and `highmemsize`. Values persist for timer setup and memory initialization.

Dependencies and integration: Called from `prom_init()` before memory and timer setup. Consumers include `time.c` and `mem.c`.

Risks: Firmware values are trusted without range validation. Wrong CPU frequency skews the R4K timer and scheduler clock.

Test signals: Boot logs should print expected `memsize`, `highmemsize`, and `CpuClock`; timer rate should match wall-clock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/loongson2ef/common/env.c -->
