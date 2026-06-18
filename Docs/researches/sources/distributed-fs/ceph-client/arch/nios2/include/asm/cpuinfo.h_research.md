# sources/distributed-fs/ceph-client/arch/nios2/include/asm/cpuinfo.h

Purpose: Nios II CPU information definitions.

Important APIs/types/functions: `struct cpuinfo`, per-CPU CPU data declarations, cache/MMU feature fields.

Control flow and state: shares detected CPU/cache/TLB capability data between setup, procfs, and low-level code.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: fields must align with detection code and compiler feature flags.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
