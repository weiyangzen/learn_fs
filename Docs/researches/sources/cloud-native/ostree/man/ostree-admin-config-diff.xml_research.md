# sources/cloud-native/ostree/man/ostree-admin-config-diff.xml

Purpose: documents `ostree admin config-diff`, which compares current `/etc` with default `/usr/etc`.

Important APIs/types: synopsis `ostree admin config-diff [OPTIONS]`, option `--os="STATEROOT"`, and output prefixes `A`, `M`, and `D`.

Control flow: command walks configuration differences and prints added, modified, and deleted paths; optional stateroot selects another OS root.

State and persistence: read-only reporting over deployment configuration state.

Dependencies and integration: relates to OSTree's three-way `/etc` merge model and admin stateroot selection.

Risks and test signals: risks are docs drifting from diff prefix semantics or stateroot option naming. Signals are CLI tests for `/etc` add/modify/delete cases and successful man generation.
