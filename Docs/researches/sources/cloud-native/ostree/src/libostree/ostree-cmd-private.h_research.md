<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-cmd-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-cmd-private.h

## Purpose
Declares the private command vtable contract exported from libostree to OSTree command-line code.

## Important APIs and Types
Declares `_ostree_impl_system_generator()` and `OstreeCmdPrivateVTable`, whose function pointers cover systemd generator output, GRUB2 config generation, static delta operations, repo binding verification, staged finalization, boot complete, and soft reboot preparation. Declares `_OSTREE_PUBLIC const OstreeCmdPrivateVTable *ostree_cmd__private__(void)`.

## Control Flow
No implementation flow; this file defines ABI shape for the private bridge.

## State and Persistence
No state directly. Function pointers may trigger persistent repo/sysroot/bootloader changes when invoked.

## Dependencies and Integration Points
Includes `ostree-types.h`. The command binary uses this header while regular external consumers should not.

## Risks
Although private, the exported symbol and struct layout are ABI-sensitive for the matching command binary. Adding/reordering fields can break mixed-version execution.

## Test Signals
Build/link tests for the command binary and integration coverage for each vtable function are the key signals.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-cmd-private.h -->
