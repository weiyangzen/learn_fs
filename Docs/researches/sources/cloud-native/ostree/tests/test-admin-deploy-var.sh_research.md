# sources/cloud-native/ostree/tests/test-admin-deploy-var.sh

Purpose: validates initial `/var` population from a commit when the `initial-var` feature is enabled.

Important APIs/functions: `has_ostree_feature initial-var`, `setup_os_repository`, direct `osdata/var/lib` creation, `ostree commit`, `pull-local`, `admin deploy`, and file assertions under `sysroot/ostree/deploy/testos/var`.

Control flow: checks feature availability, creates `var/lib/somefile` in the OS tree, commits and pulls it, deploys, then confirms the stateroot var contains the file. It later creates tmpfiles-style data and verifies expected var behavior across additional commits.

State/persistence: writes stateroot shared var, deployment usr trees, and commits. Dependencies include feature support and syslinux setup.

Integration/risk/test signals: protects one-time initial var seeding without confusing deployment-local usr data. Risks include feature-gated behavior and broad `ls -R` diagnostics. Assertions on var content are the main signal.
