# sources/cloud-native/ostree/tests/test-admin-upgrade-unconfigured.sh

Purpose: validates user-facing failure when a deployment origin is marked unconfigured and confirms switching can move to a configured remote.

Important APIs/functions: `setup_os_repository`, `pull-local`, `admin deploy`, manual edit of `.origin`, `remote add`, `admin upgrade`, and `admin switch`.

Control flow: deploys a runtime, appends `unconfigured-state=...` to the deployment origin, adds the remote, attempts upgrade and expects the subscription-style message, then adds another remote and switches to it successfully.

State/persistence: mutates the active deployment origin file and remote config. Dependencies include origin parsing and unconfigured-state validation.

Integration/risk/test signals: protects subscription/unconfigured remote UX and switch escape path. Risks are exact error message regexes. Two TAP cases report error and switch success.
