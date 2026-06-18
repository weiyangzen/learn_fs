# sources/cloud-native/ostree/rust-bindings/src/auto/deployment.rs

Purpose: Generated wrapper for `OstreeDeployment`, representing a bootable deployed tree in a sysroot.

Important APIs: `new`, `clone`, `equal`, getters for bootconfig, boot checksum/serial, commit checksum, deploy serial, index, origin, origin relpath, OS name, unlocked state, pinned/staged/finalization-lock/soft-reboot status by feature, setters for bootconfig, bootserial, index, and origin, plus static helpers `origin_remove_transient_state` and `unlocked_state_to_string`.

Control flow and state: Deployment objects hold sysroot deployment metadata. Some setters mutate object state in memory; sysroot APIs persist deployment lists and bootloader entries. Origin is a `glib::KeyFile`, connecting deployments back to remote/ref configuration.

Dependencies and integration points: Depends on `BootconfigParser`, `DeploymentUnlockedState`, GLib keyfiles, feature-gated libostree deployment APIs, and sysroot write/deploy flows. It is central to upgrade/downgrade behavior such as the manual `upgrade-loop.js`.

Risks: Deployment identity includes index, checksum, serials, and origin; changing setters without writing sysroot state has no persistent effect. Feature-gated status methods depend on runtime libostree support. Origin keyfiles can contain transient state that should be stripped where appropriate.

Test signals: Equality/hash behavior via libostree, clone/getter/setter round trips, origin keyfile persistence through sysroot writes, and feature-gated deployment state tests.
