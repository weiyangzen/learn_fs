# sources/distributed-fs/ceph-client/arch/mips/vdso/Makefile

Purpose: MIPS vDSO build rules for native, O32, and N32 images.

Important APIs/types/functions: object lists `elf.o vgettimeofday.o sigreturn.o`, `genvdso` host tool, ABI-specific object/link/image rules, vDSO checks for generic validity and `jalr t9` PIC calls.

Control flow and state: builds raw debug and stripped shared objects with restricted PIC flags, copies raw outputs, runs `genvdso` to emit kernel C images, and conditionally builds O32/N32 variants with `config-n32-o32-env.c` include.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: compiler/linker flags are ABI-sensitive; unsupported PIC calls are fatal; generated debug artifacts have a FIXME install path; disabling vDSO time changes object list.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
