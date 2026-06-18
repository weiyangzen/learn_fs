# sources/cloud-native/ostree/man/ostree-admin-stateroot-init.xml

Purpose: documents `ostree admin stateroot-init`, which initializes empty state for a named OS/stateroot.

Important APIs/types: required `STATEROOT`; description defines stateroot as an OS name with shared `var` and deployments.

Control flow: creates core `/var` subdirectories and initializes `ostree/deploy/STATEROOT`.

State and persistence: creates persistent stateroot directories, shared var, and deployment roots.

Dependencies and integration: prerequisite for deploying a new OS name and replacement for deprecated `os-init`.

Risks and test signals: risks include inconsistent stateroot naming and var layout. Signals are directory layout tests and deploy into new stateroot.
