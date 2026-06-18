# sources/distributed-fs/ceph-client/arch/nios2/include/asm/asm-macros.h

Purpose: Nios II assembler convenience macros.

Important APIs/types/functions: `ANDI32`, `ORI32`, `XORI32`, bit-test/set/clear/branch macros, `PUSH`, `POP`.

Control flow and state: macros choose compact immediate sequences for 32-bit masks and provide reusable stack/bit operations for low-level assembly.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: some comments note register alias constraints; `BTR` high-half path appears suspicious using `%lo` with `andhi`, so assembler coverage matters.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
