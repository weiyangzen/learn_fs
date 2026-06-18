# sources/cloud-native/ostree/tests/test-admin-deploy-composefs.sh

Purpose: verifies admin deployment behavior when composefs support is available, including runtime disablement and artifact generation.

Important APIs/functions: `skip_without_ostree_feature composefs`, `setup_os_repository`, `ostree commit`, `pull-local`, `ostree admin deploy`, config file `usr/lib/ostree/prepare-root.conf`, and `.ostree.cfs` checks.

Control flow: writes a tree config disabling composefs at runtime, commits and deploys it, asserts a composefs blob is still generated, then mutates config/commits for additional deploy cases covering enabled behavior and metadata expectations.

State/persistence: creates commits with `version=*.composefs`, writes deployment directories and `.ostree.cfs` files. Dependencies include composefs-enabled OSTree and syslinux admin setup.

Integration/risk/test signals: validates composefs deployment artifacts independent from runtime mount policy. Risks include feature gating, exact artifact names, and external composefs capability changes. TAP output and file counts signal success.
