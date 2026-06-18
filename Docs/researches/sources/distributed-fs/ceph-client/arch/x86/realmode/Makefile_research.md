<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/realmode/Makefile

## Purpose
Builds the x86 real-mode trampoline blob and piggyback object used by early boot and low-level transitions.

## Important APIs, Types, And Functions
The Makefile includes `rm/Makefile`, adds `init.o` and `rmpiggy.o`, and wires real-mode targets into the object tree.

## Control Flow
Kbuild descends into real-mode build rules, creates the real-mode binary, and links the piggy object into the kernel.

## State And Persistence
No runtime state exists in the Makefile, but it controls generation of the embedded real-mode code image used at boot/resume.

## Dependencies And Integration Points
Integrates with `arch/x86/realmode/rm` build rules, early boot trampoline allocation, and users such as EFI boot-services memory handling that may reserve space for the trampoline.

## Risks And Edge Cases
Build ordering is important because `rmpiggy.o` depends on generated real-mode artifacts. Missing trampoline artifacts can break boot paths requiring real mode.

## Test Signals
Successful x86 build, presence of generated real-mode image, and boot paths using the trampoline validate the Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/realmode/Makefile -->
