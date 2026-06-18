<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Kbuild -->
# sources/distributed-fs/ceph-client/arch/riscv/Kbuild

## Purpose
Selects the top-level RISC-V architecture subdirectories that participate in kernel builds.

## Important APIs, Types, And Functions
Exports `obj-y` for `kernel/`, `mm/`, `net/`, always includes `errata/`, conditionally includes `crypto/`, `kvm/`, and `purgatory/`, and marks `boot` as a clean-only subdirectory.

## Control Flow
Kbuild evaluates config symbols and descends into selected directories while linking arch objects into vmlinux.

## State And Persistence
State is build graph state only: selected object directories and clean traversal.

## Dependencies And Integration Points
Integrated with global Linux kbuild, RISC-V Kconfig symbols, crypto, KVM, kexec purgatory, networking, MM, and errata subsystems.

## Risks And Edge Cases
Missing a directory here can silently omit architecture functionality. Adding unconditional directories can break configs that lack dependencies.

## Test Signals
Signals are `make ARCH=riscv` object traversal, clean coverage for boot artifacts, and config-specific inclusion of crypto/KVM/purgatory objects.

Source read size: 11 lines, 233 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/Kbuild -->
