# sources/cloud-native/ostree/man/ostree-admin-init-fs.xml

Purpose: documents `ostree admin init-fs`, which initializes an empty physical root filesystem for OSTree deployments.

Important APIs/types: required `PATH`; options `--modern` and `--epoch`. Epoch text describes skipping API filesystem toplevels and hardened `ostree` directory permissions.

Control flow: creates expected toplevels and permissions under a target root. `--modern` maps to epoch behavior.

State and persistence: creates persistent root filesystem directories such as boot/sysroot/ostree layout and permission policy.

Dependencies and integration: used by OS installers and pairs with later stateroot/deploy operations.

Risks and test signals: docs contain a range note `[0-1]` but also describe epoch 2, a drift risk. Signals are installer tests for initialized layout and permission checks for epoch modes.
