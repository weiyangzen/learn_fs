# sources/distributed-fs/ceph-client/arch/mips/txx9/generic/mem_tx4927.c

Purpose: TX4927/TX4938 SDRAM size discovery from controller registers.

Important APIs/types/functions: `tx4927_process_sdccr`, `tx4927_get_mem_size`.

Control flow and state: reads SDCCR values, decodes row/column/bank width, computes size per memory channel, and returns total memory detected by hardware.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: decode assumes controller register format; bad values can under/over-report RAM and corrupt boot memory setup.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
