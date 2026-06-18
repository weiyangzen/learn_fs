# sources/distributed-fs/ceph-client/arch/mips/tools/loongson3-llsc-check.c

Purpose: host validator for Loongson3 LL/SC sequences in `vmlinux`.

Important APIs/types/functions: `is_ll`, `is_sc`, `is_sync`, `is_branch`, `check_ll`, `check_code`, `main` ELF section scan.

Control flow and state: maps vmlinux read-only, validates ELF64 little-endian MIPS sections, scans executable code for LL instructions, and enforces expected sync/branch/SC patterns used by Loongson3 workarounds.

Dependencies and integration: Control flow/state: this file is boot-time or build-time architecture support; persistent effects are kernel configuration, registered platform devices, IRQ/controller state, generated image artifacts, or hardware register programming rather than application data. Dependencies are Linux arch hooks, MIPS/NIOS2 low-level headers, Kbuild/Kconfig, and SoC/board registers. Test signals are mostly compile/link coverage for the relevant config plus boot smoke tests on matching hardware or emulator, IRQ/timer/device enumeration logs, and driver probe success.

Risks: assumes instruction encoding and ELF layout; false positives can fail builds, false negatives weaken erratum protection; only active under relevant config.

Test signals: build the owning architecture/configuration, inspect boot logs for the named device or subsystem, and exercise the specific hardware path where available. For build helpers, validate generated artifacts and failure handling with representative inputs.
