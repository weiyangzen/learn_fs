# sources/cloud-native/ostree/tests/test-admin-pull-deploy-commit.sh

Purpose: regression test for deploying a directly pulled commit checksum rather than a ref.

Important APIs/functions: `setup_os_repository`, `remote add`, `pull`, `rev-parse`, `ostree admin deploy`, and parent commit resolution through `${rev}^`.

Control flow: creates a sysroot, adds a remote, pulls the runtime ref, resolves its parent commit, explicitly pulls that parent checksum, then deploys the parent by checksum with kernel arguments.

State/persistence: imports commit objects and writes one deployment. Dependencies include a repository history with at least one parent commit.

Integration/risk/test signals: protects issue-era behavior where pulled commits without ref names must remain deployable. Risk is limited to parent commit fixture shape. One TAP case reports `deploy pulled commit`.
