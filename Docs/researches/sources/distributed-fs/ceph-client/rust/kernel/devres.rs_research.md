# sources/distributed-fs/ceph-client/rust/kernel/devres.rs

## Purpose
`devres.rs` wraps Linux device-managed resources for Rust. It provides `Devres<T>`, which couples a device-bound resource with `Revocable<T>` so access is revoked before device unbind completes, and a simpler `register` helper for drop-on-unbind resources.

## Important APIs, Types, and Functions
`Inner<T>` embeds a `devres_node` and `Revocable<T>`. `Devres<T>` stores an `ARef<Device>` and an `Arc<Inner<T>>`. Important methods include `Devres::new`, `device`, `access`, `try_access`, `try_access_with`, and `try_access_with_guard`. C callbacks are `devres_node_release` and `devres_node_free_node`. The `base` module provides non-inlined wrappers for devres C symbols. `register_foreign` and public `register` use `devm_add_action_or_reset`.

## Control Flow
`Devres::new` allocates and pins `Inner<T>`, initializes a devres node with release/free callbacks, registers it on a bound device, and leaks an extra `Arc` reference for devres ownership. On device unbind, the devres release callback revokes access, and the free callback drops the extra `Arc`. If the Rust `Devres` handle drops first, it revokes without waiting, removes the devres node if still present, and releases the devres-owned reference.

## State and Persistence
All state is transient kernel memory tied to the device lifetime. The device keeps a devres node; Rust keeps an `Arc` and a device reference. `Revocable<T>` is the access gate and ensures no new accesses after revocation.

## Dependencies and Integration Points
The module depends on `Device<Bound>`, `ARef`, `Arc`, `Revocable`, RCU guards, `ForeignOwnable`, and devres bindings. DMA, DRM registration, IRQ/class/subsystem wrappers, and bus resources can use it to bind cleanup to unbind.

## Risks
The subtle risks are double-free or leaked `Arc` ownership between Rust drop and devres callbacks, using `access` with a different device, and assuming `try_access` remains valid after unbind starts. The comments also note monomorphization/export concerns for direct C binding calls.

## Test Signals
Exercise drop-before-unbind and unbind-before-drop paths, concurrent `try_access` while unbinding, `access` with matching and mismatched devices, `devm_add_action_or_reset` failure cleanup, and leak checks over repeated probe/remove cycles.
