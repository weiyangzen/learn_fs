<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel/Makefile

## Purpose
Builds Intel IOSF sideband mailbox support.

## Important APIs, Types, And Functions
`iosf_mbi.o` is selected by `CONFIG_IOSF_MBI`.

## Control Flow
Kbuild adds the mailbox accessor driver to the x86 Intel platform directory when configured.

## State And Persistence
No runtime state exists in this Makefile.

## Dependencies And Integration Points
The resulting object provides exported IOSF MBI symbols used by Quark IMR and other Atom/SoC drivers.

## Risks And Edge Cases
Consumers that depend on IOSF MBI need this symbol selected or loaded; otherwise platform features fail at runtime.

## Test Signals
Kernel link coverage and module/object build with `CONFIG_IOSF_MBI` enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel/Makefile -->
