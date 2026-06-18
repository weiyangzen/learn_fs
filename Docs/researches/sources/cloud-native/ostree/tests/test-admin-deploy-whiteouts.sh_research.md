# sources/cloud-native/ostree/tests/test-admin-deploy-whiteouts.sh

Purpose: validates deployment of OCI-style whiteout device nodes and preservation of their permissions.

Important APIs/functions: `skip_without_whiteouts_devices`, `setup_os_repository`, `pull-local`, `ostree admin deploy`, `admin --print-current-dir`, `assert_is_whiteout_device`, and mode/file absence assertions.

Control flow: deploys the runtime tree containing container layer whiteouts, resolves current deployment, asserts a whiteout device exists, confirms `.ostree-wh.whiteout` marker files are not materialized, and verifies modes for multiple whiteout entries.

State/persistence: reads deployment `/usr/container/layers/...` content from the committed fixture and writes boot deployment state. Dependencies include device-node support/privileges.

Integration/risk/test signals: protects container image whiteout translation in admin deployments. Risks are privilege and filesystem capability requirements. Three TAP cases cover device, marker absence, and permissions.
