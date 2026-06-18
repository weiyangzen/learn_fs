# sources/cloud-native/ostree/src/libostree/ostree-deployment.c

## Purpose
This file implements the `OstreeDeployment` GObject: creation, cloning, identity/equality, origin management, bootconfig ownership, transient-origin cleanup, overlay initrd tracking, and public state queries.

## Important APIs, Types, And Functions
The GObject is declared with `G_DEFINE_TYPE`. Getters expose checksum, boot checksum, osname, deploy serial, boot serial, bootconfig, origin, and index. Setters mutate index, boot serial, bootconfig, origin, and internal boot checksum/overlay initrds. `ostree_deployment_new()` validates required fields and initializes identity. `ostree_deployment_clone()` deep-copies bootconfig, origin keyfile data, overlay initrds, and cached dev/inode. `ostree_deployment_hash()` and `ostree_deployment_equal()` use osname, commit checksum, and deploy serial. `ostree_deployment_origin_remove_transient_state()` removes the transient group plus legacy transient keys. `_ostree_deployment_get_kargs()` parses bootconfig `options` into `OstreeKernelArgs`.

## Control Flow, State, And Persistence
The object owns string fields, bootconfig object references, and a refcounted `GKeyFile` origin. Cloning serializes and reloads the origin to avoid shared mutable keyfile state. `ostree_deployment_get_origin_relpath()` derives the persistent `.origin` path from osname, checksum, and deploy serial. Finalization frees all owned state.

## Dependencies And Integration Points
It depends on bootconfig parsing, kernel args parsing, GLib/GObject, and otutil helpers. Sysroot code constructs deployments from on-disk state, compares them for bootloader writes, and uses transient-origin cleanup during upgrades.

## Risks And Test Signals
Equality ignores boot checksum, boot serial, origin, staged flags, and overlay initrds; code needing full boot equivalence must compare additional fields. `ostree_deployment_set_bootserial()` is public but documented as historical API not to use. Tests should cover clone independence, origin transient removal, origin relpath formatting, hash/equality consistency, overlay initrd ID behavior, and lifecycle cleanup under valgrind/asan.
