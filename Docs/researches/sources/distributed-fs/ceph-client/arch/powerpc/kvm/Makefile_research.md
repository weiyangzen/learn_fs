# sources/distributed-fs/ceph-client/arch/powerpc/kvm/Makefile

## Purpose
Maps PowerPC KVM Kconfig symbols to the C and assembly objects linked into common KVM, e500, Book3S PR, Book3S HV, interrupt controller, SPAPR TCE, and built-in real-mode handler components.

## Important APIs, Types, And Functions
This file defines Kbuild object groups: `common-objs-y`, `kvm-e500-objs`, `kvm-e500mc-objs`, `kvm-pr-y`, `kvm-hv-y`, `kvm-book3s_64-builtin-objs-*`, `kvm-book3s_64-module-objs`, and `kvm-book3s_32-objs`. It also sets include flags, assembly flags for BookE interrupts, and disables KASAN for 64-bit Book3S real-mode KVM code.

## Control Flow
Kbuild expands `obj-$(CONFIG_...)` and group variables. e500 variants build `kvm.o`; Book3S 64 builds the common module plus optional `kvm-pr.o` and `kvm-hv.o`; Book3S 32 builds PR-only support into `kvm.o`. HV-capable builds add real-mode handlers, P9 entry, nestedv2, guest-state-buffer, HMI/RAS, TM, XICS, XIVE, and UV memory objects as selected.

## State And Persistence
No runtime state. Build state is the selected object graph and resulting modules/built-ins.

## Dependencies And Integration Points
Depends on `virt/kvm/Makefile.kvm`, Kconfig symbols, PowerPC assembly offsets, and object naming conventions. It integrates C/assembly files that must agree on offsets and real-mode constraints. The `obj-y += $(kvm-book3s_64-builtin-objs-y)` line ensures real-mode Book3S 64 handlers are built in when required even if KVM is modular.

## Risks And Edge Cases
Object grouping affects symbol visibility and link order. Missing built-in handler objects can break exception entry before modules load. Including sanitizer instrumentation in real-mode code would be unsafe, hence the explicit KASAN disable. Optional XICS/XIVE/TM/UV selections must match both C references and assembly branches.

## Test Signals
Cross-build Book3S 32, Book3S 64 PR, Book3S 64 HV, e500v2, e500mc, XICS, XIVE, SPAPR TCE, transactional memory, and UV configurations. Link failures, unresolved exported symbols, and early guest-entry crashes are the main signals for this file.
