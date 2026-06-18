# sources/distributed-fs/ceph-client/arch/nios2/include/asm/Kbuild

Purpose: Nios II asm header Kbuild export list.

Important APIs/types/functions: generic header mappings and generated header declarations.

Control flow and state: controls which asm headers are generated/exported to UAPI or generic fallbacks.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: header list drift can break userspace or internal includes.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
