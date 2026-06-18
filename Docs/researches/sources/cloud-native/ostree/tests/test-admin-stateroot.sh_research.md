# sources/cloud-native/ostree/tests/test-admin-stateroot.sh

Purpose: validates stateroot initialization and `set-default` bootconfig swap decisions.

Important APIs/functions: `setup_os_repository`, `admin deploy`, `admin status`, `admin stateroot-init`, `admin set-default`, grep/sed ref extraction, and output assertions for `bootconfig swap`.

Control flow: deploys on `testos`, extracts the deployed ref, creates `testos2`, deploys the same ref there, sets default to the new stateroot and expects `bootconfig swap: yes`; then deploys identical entries again and expects `bootconfig swap: no`.

State/persistence: writes multiple stateroots under `sysroot/ostree/deploy` and bootloader ordering state. Dependencies include stable `admin status` text.

Integration/risk/test signals: protects bootloader update minimization across stateroots. Risks are parsing status output and index-based default selection. Two TAP cases cover changed vs equal deployments.
