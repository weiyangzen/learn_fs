<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sysroot-private.h -->
# sources/cloud-native/ostree/src/libostree/ostree-sysroot-private.h

## Purpose
`ostree-sysroot-private.h` defines libostree's private `OstreeSysroot` layout, internal flags, transient path constants, and private helper prototypes shared by sysroot load, cleanup, deployment, bootloader, staging, and soft reboot code.

## Important APIs, Types, And Functions
`OstreeSysrootDebugFlags` controls test and debug behavior such as mutable deployments, skipping xattrs, exercising the FIFREEZE watchdog path, and suppressing device-tree discovery in tests. `OstreeSysrootGlobalOptFlags` exposes process-wide sysroot options for skipping sync, disabling early bootfs prune, and opting into the old bootloader naming scheme. `OstreeSysrootLoadState` tracks whether a sysroot is new, initialized, or fully loaded.

The private `struct OstreeSysroot` stores the public GObject parent, `GFile *path`, sysroot and boot fds, boot filesystem metadata, the sysroot lock, load state, mount namespace and physical-root flags, booted root device/inode identity, soft reboot expected device/inode identity, parsed `/run/ostree` metadata, deployment arrays, bootversion/subbootversion, pointers to booted/soft-reboot/staged deployments, staged deployment variant data, repo pointer, and debug/global option flags.

Constants define the lock file (`ostree/lock`), staged deployment state (`/run/ostree/staged-deployment` and lock path), staged initrd directory, deployment run-state directory and flags, boot/initramfs overlay locations, and the `/boot`-relative staged finalization failure stamp. Prototypes cover private deployment object creation, journal emission, bootloader config reading, subbootversion parsing, deployment directory listing, staged reload/finalization/boot-complete functions, soft reboot preparation, deployment variant deserialization, backing path creation, deployment removal, legacy var initialization, run-state path construction, sandboxed command execution inside deployments, line joining, boot fd setup, bootloader query, mtime bumping, cleanup, boot directory parsing/listing, and bootlink parsing.

## Control Flow
This header has no runtime control flow, but it defines the state transitions other files enforce. A new sysroot starts at `OSTREE_SYSROOT_LOAD_STATE_NONE`, becomes initialized once fd-backed sysroot state is available, and reaches `LOADED` after deployments, bootloader versions, booted/staged/soft-reboot state, and repo are discovered. Deployment write and staging code in `ostree-sysroot-deploy.c` assumes this structure has valid `sysroot_fd`, loaded deployment arrays, and optionally `boot_fd` after `_ostree_sysroot_ensure_boot_fd`.

## State And Persistence
The header distinguishes in-memory state from persistent and transient state. Persistent state is reachable through `sysroot_fd`, `boot_fd`, the deployment list, bootversion/subbootversion, repo, and deployment objects. Transient runtime state lives under `/run/ostree`, including staged deployments, staged lock, staged initrds, deployment flags such as unlocked-development/unlocked-transient, and soft reboot state. The failure stamp is deliberately `/boot` relative so a failed staged finalization can be reported on the next boot.

## Dependencies And Integration Points
The header includes `libglnx.h`, `ostree-bootloader.h`, and the public `ostree.h`. It is consumed by sysroot implementation files, including deployment, cleanup, load, and bootloader code. The private helper prototypes form the integration contract between the deployment transaction code and the rest of libostree: deployment object construction, bootloader parsing, cleanup, repo access, journaling, and run-state management all cross this boundary.

## Risks
Because this file exposes the internal object layout, field changes can silently break assumptions across multiple C files. File descriptor lifetime is subtle: `sysroot_fd` and `boot_fd` are initialized on demand and some cleanup paths may close or require re-ensuring them. Deployment pointers must remain consistent with `deployments` array contents, especially when staged deployments are inserted or removed. The transient path constants are consumed by services and command-line tools, so renaming or moving them is a compatibility risk. Debug flags are used in tests and can bypass production behavior such as immutable deployments or xattrs.

## Test Signals
Compilation is the primary direct signal because this header wires many private modules. Functional coverage comes from sysroot load/reload tests, staged deployment tests using `/run/ostree/staged-deployment`, soft reboot tests using run-state paths, cleanup tests using deployment removal and boot directory parsing, bootloader tests using bootversion/subbootversion helpers, and tests that toggle debug flags for mutable deployments, xattrs, fsfreeze, or no-device-tree behavior.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/src/libostree/ostree-sysroot-private.h -->
