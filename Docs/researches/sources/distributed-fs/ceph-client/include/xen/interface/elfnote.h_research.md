<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/elfnote.h -->
# sources/distributed-fs/ceph-client/include/xen/interface/elfnote.h

## Purpose
This Xen public header defines numeric ELF note types used by Xen loaders, guests, crash notes, and dump-core files.

## Important APIs, Types, And Functions
- Notes `XEN_ELFNOTE_INFO` through `XEN_ELFNOTE_PHYS32_RELOC` describe guest metadata such as entry address, hypercall page, virtual base, paddr offset, Xen version, guest OS/version, loader, PAE mode, feature strings, symbol table need, hypervisor hole low bound, L1 MFN masks, suspend cancellation, initial P2M, initrd mapping support, supported features, PVH 32-bit entry, and PVH relocation constraints.
- `XEN_ELFNOTE_MAX` tracks the highest regular note.
- Crash notes `XEN_ELFNOTE_CRASH_INFO` and `XEN_ELFNOTE_CRASH_REGS` identify kexec/kdump data.
- Dump-core notes identify Xen dump-core marker, header, Xen version, and format version.

## Control Flow
Build/link code emits notes into a PT_NOTE segment named `Xen`; Xen tooling and hypervisors parse them when loading or dumping guests. Runtime kernel code generally consumes the consequences rather than calling functions from this header.

## State And Persistence
Notes are persistent metadata embedded in ELF binaries or dump files. They inform hypervisor load decisions and crash/dump interpretation.

## Dependencies And Integration Points
It integrates with Xen domain builders, kernel linker scripts, PV/PVH boot protocols, kexec/kdump, dump-core tooling, and feature negotiation.

## Risks And Edge Cases
Incorrect numeric note values or malformed descriptors can make kernels unbootable under Xen. Some notes are x86-only, and legacy `__xen_guest` compatibility semantics differ from modern notes. PVH relocation constraints must match actual binary relocation ability.

## Test Signals
Signals include ELF note inspection showing expected `Xen` notes, successful Xen/PVH boot, correct feature negotiation on old and new Xen versions, usable kdump crash notes, and dump-core tools recognizing header/version notes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/xen/interface/elfnote.h -->
