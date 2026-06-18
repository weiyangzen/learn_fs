<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-cmd-private.c -->
# sources/cloud-native/ostree/src/libostree/ostree-cmd-private.c

## Purpose
Exports a private vtable used to share selected libostree internals with the OSTree command-line binary without making their headers public API.

## Important APIs and Types
`ostree_cmd__private__()` returns a static `OstreeCmdPrivateVTable`. It maps command-side hooks to `_ostree_impl_system_generator`, a local wrapper around `_ostree_bootloader_grub2_generate_config()`, static delta dump/query/delete helpers, repo binding verification, sysroot staged finalization, boot-complete handling, and soft reboot preparation.

## Control Flow
The function initializes a static table literal and returns its address. The only wrapper delegates GRUB2 generation to the bootloader implementation.

## State and Persistence
The static vtable is process-lifetime immutable state. Called functions perform the actual repository, sysroot, bootloader, or static-delta mutations.

## Dependencies and Integration Points
Depends on private headers for GRUB2, core, repo, static deltas, sysroot, and command declarations. It is a bridge between libostree and command code while preserving a narrow exported symbol.

## Risks
The symbol is exported but intentionally not public API; vtable layout changes require command/library version alignment. A stale command binary could call mismatched function slots.

## Test Signals
Tests should verify CLI operations that use each vtable slot, especially GRUB generation, static delta commands, staged finalization, and boot-complete paths.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-cmd-private.c -->
