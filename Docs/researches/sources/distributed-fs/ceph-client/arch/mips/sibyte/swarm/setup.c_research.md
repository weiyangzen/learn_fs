# sources/distributed-fs/ceph-client/arch/mips/sibyte/swarm/setup.c

Purpose: SWARM board setup for system type, bus-error handling, RTC persistent clock, memory setup, and LED writes.

Important APIs/types/functions: `get_system_type`, `swarm_be_handler`, `read_persistent_clock64`, `update_persistent_clock64`, `plat_mem_setup`, `setleds`.

Control flow and state: setup installs bus-error handler, selects Xicor or M41T81 clock through probe order, wires restart/halt/power hooks, declares board resources, and writes LED strings through board registers.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: RTC fallback depends on low-level probes; bus-error handling may hide or report platform errors differently; LED and board register writes assume SWARM-compatible hardware.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
