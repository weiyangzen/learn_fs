# sources/distributed-fs/ceph-client/arch/nios2/include/asm/entry.h

Purpose: Nios II assembly entry save/restore macros.

Important APIs/types/functions: macros to save/restore trap frame registers and switch-stack callee-saved registers using `PT_*`/`SW_*` offsets.

Control flow and state: entry code uses these macros to capture user SP/status/EA, preserve registers on exceptions/syscalls, and restore before return.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: offsets must match generated asm offsets; restore order and SP handling are exception-return critical.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
