# sources/distributed-fs/ceph-client/arch/mips/sibyte/common/sb_tbprof.c

Purpose: character-device module exposing SiByte SCD trace-buffer/ZBbus profiling through major 240 and `/dev/tb`.

Important APIs/types/functions: `sbprof_tb_open`, `sbprof_tb_read`, `sbprof_tb_ioctl`, `sbprof_zbprof_start/stop`, `arm_tb`, trace-freeze and perf-counter IRQ handlers, global `struct sbprof_tb sbp`, and ioctl commands `SBPROF_ZBSTART`, `SBPROF_ZBSTOP`, `SBPROF_ZBWAITFULL`.

Control flow and state: open allocates a large vmalloc trace buffer and initializes wait queues; start requests trace-freeze and perf-counter IRQs, configures SCD performance counters, address traps, trace events/sequences, and arms delayed sampling; the trace-freeze interrupt drains 256 bundles into `sbprof_tbbuf`, re-arms until full/disabled, and wakes waiters; read copies captured samples to userspace by file offset; cleanup unregisters the class/device/char major.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: very hardware-specific MMIO and interrupt assumptions; busy interaction with global SCD counters and trace buffer can conflict with other users; open/release state is fragile, including a release check that returns when `sbp.open != SB_CLOSED`, which appears inverted for normal cleanup; stop has a documented wakeup race window; fixed major and large allocation can fail or conflict.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
