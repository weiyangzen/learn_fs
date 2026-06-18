# sources/cloud-native/ostree/tests/test-admin-deploy-switch.sh

Purpose: validates `ostree admin switch` between refs and remotes, including expected error when switching to the same ref.

Important APIs/functions: `setup_os_repository`, `remote add`, `pull`, `admin deploy`, `admin switch`, `rev-parse`, and filesystem assertions under deployment `/usr/include`.

Control flow: deploys runtime, confirms devel header absent, attempts a same-ref switch and expects failure, switches to the devel ref and checks header presence, then adds another remote and exercises switching remote/ref origins.

State/persistence: updates remote config, origin files, deployment directories, and bootloader entries. Dependencies include runtime and devel refs created by the OS repository harness.

Integration/risk/test signals: protects branch/rebase-like admin switch behavior. Risks include assumptions about fixture refs and header content. Four TAP entries describe switch outcomes.
