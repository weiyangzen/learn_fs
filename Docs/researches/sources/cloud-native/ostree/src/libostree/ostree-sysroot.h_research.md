# sources/cloud-native/ostree/src/libostree/ostree-sysroot.h

## Purpose
Public libostree API declaration for `OstreeSysroot`, the object used to inspect, lock, initialize, load, write, stage, deploy, unlock, pin, cleanup, and soft-reboot OSTree sysroots.

## Important APIs, Types, And Functions
The header exposes `OSTREE_PATH_BOOTED`, `OSTREE_TYPE_SYSROOT`, type-check macros, and `ostree_sysroot_get_type`. It declares constructors, initialization/loading APIs, fd/path accessors, deployment getters, repo accessors, locking APIs, cleanup APIs, origin writing, kernel argument mutation, deployment writing, overlay initrd staging, deploy/stage tree APIs, finalization, mutable/pinned/unlocked state APIs, deployment query helpers, post-copy update, simple write flags, and soft-reboot/kexec functions.

Important public option types are `OstreeSysrootWriteDeploymentsOpts`, `OstreeSysrootDeployTreeOpts`, and `OstreeSysrootSimpleWriteDeploymentFlags`. The option structs reserve unused bool/int/pointer fields for ABI-compatible growth.

## Control Flow
Consumers generally create a sysroot, initialize or load it, acquire the lock for mutation, use repo/deployment APIs to compute changes, then call deploy/stage/write helpers and cleanup. Read-only callers load and query deployments. Staging and deployment APIs accept origins, merge deployments, kernel argv overrides, overlay initrds, and locking options.

## State And Persistence Behavior
The header does not implement state, but it defines which persistent sysroot concepts are externally mutable: deployment lists, origins, bootloader state, staged deployment data, pinning, unlock mode, cleanup/prune state, and soft reboot metadata. Public APIs imply caller responsibility for ordering and locking around persistent mutations.

## Dependencies And Integration Points
It includes `ostree-deployment.h` and `ostree-repo.h`, exposing `GFile`, `GPtrArray`, `GKeyFile`, `GCancellable`, and `GError` integration. It is consumed by admin tools and other libostree modules that need stable ABI access to sysroot functionality.

## Risks
The API surface is broad and ABI-stable, so option struct layout and enum values must be preserved. Many functions require prior load/initialize or a loaded deployment list; callers can misuse them if lifecycle requirements are ignored. Locking is advisory but essential for multi-process mutation safety.

## Test Signals
Header-level tests are indirect: ABI/API checks, introspection generation, compile coverage for public declarations, option struct compatibility, and behavioral tests against the implementations declared here.
