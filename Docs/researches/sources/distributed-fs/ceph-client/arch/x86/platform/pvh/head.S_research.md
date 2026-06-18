<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/head.S -->
# sources/distributed-fs/ceph-client/arch/x86/platform/pvh/head.S

## Purpose
Implements the Xen PVH 32-bit physical entry point that sets up minimal CPU state, page tables, and handoff to generic x86 startup.

## Important APIs, Types, And Functions
Defines `pvh_start_xen`, PVH GDT entries/selectors, early stack, 64-bit PVH identity/kernel page tables, and Xen ELF notes for physical entry/relocation.

## Control Flow
Entry starts with Xen-specified registers, obtains a position-independent base without a normal stack, loads a private GDT, copies `hvm_start_info`, sets up stack, enables PAE/long mode as needed, applies relocation fixups to prebuilt page tables on x86_64, calls `xen_prepare_pvh()` through the high mapping, passes `pvh_bootparams`, and jumps to `startup_64` or resets paging state before `startup_32`.

## State And Persistence
Populates `pvh_start_info`, `phys_base` on relocation, temporary page tables, GDT, and stack in init sections. These are early boot artifacts.

## Dependencies And Integration Points
Depends on Xen PVH ABI, x86 paging constants, startup entry points, `enlighten.c`, and linker support for ELF notes.

## Risks And Edge Cases
No normal stack exists at entry; relocation arithmetic must avoid unsupported absolute relocations. Incorrect page-table fixups break PIE/KASLR PVH boot. Instrumentation is disabled by the Makefile for this reason.

## Test Signals
Booting PVH kernels in 32-bit, 64-bit, relocated, and non-relocated configurations is the meaningful validation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/pvh/head.S -->
