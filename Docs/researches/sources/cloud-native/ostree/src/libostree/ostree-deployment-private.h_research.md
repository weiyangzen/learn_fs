# sources/cloud-native/ostree/src/libostree/ostree-deployment-private.h

## Purpose
This private header defines the full `OstreeDeployment` instance layout and internal helpers that are not part of the public deployment API. It represents one bootable deployment in a sysroot.

## Important APIs, Types, And Functions
`struct _OstreeDeployment` stores GObject base state plus bootloader index, stateroot/osname, commit checksum, deploy serial, boot checksum, boot serial, `OstreeBootconfigParser`, origin `GKeyFile`, unlocked/staged/finalization/soft-reboot state, overlay initrd checksums and derived ID, and cached device/inode identity. Internal functions include `_ostree_deployment_set_bootcsum()`, `_ostree_deployment_set_overlay_initrds()`, `_ostree_deployment_get_overlay_initrds()`, and `_ostree_deployment_get_kargs()`.

## Control Flow, State, And Persistence
The structure mirrors persistent sysroot state: deployment paths, `.origin` keyfiles, bootloader config, and boot artifacts under `/boot/ostree`. The dev/inode cache is process-local and used to compare deployment backing identity.

## Dependencies And Integration Points
It includes `ostree-deployment.h` and is used by deployment/sysroot/admin code that needs mutation beyond the public getters/setters.

## Risks And Test Signals
Because this exposes private layout to sibling C files, field changes can break assumptions in sysroot code. Overlay initrd ID generation currently concatenates checksums, so tests should cover ordering and collision-sensitive comparison behavior. Tests should also cover staged/finalization/soft-reboot flag propagation and kargs parsing from bootconfig.
