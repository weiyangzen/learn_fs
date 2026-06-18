# sources/cloud-native/composefs-rs/examples/unified/Containerfile

Purpose: Fedora multi-stage Containerfile for unified composefs UKI images without Secure Boot signing.

Important APIs/types/functions: base/kernel/bootable stages; installs composefs, kernel, systemd-boot, ukify, SELinux tools, SSH; computes fs-verity digest from bound base via `cfsctl`; writes kernel cmdline; runs `kernel-install add-all`.

Control flow: base root is prepared, kernel stage computes digest over base and generates `/boot`, bootable stage combines base with generated boot files.

State/persistence: resulting image includes `/boot` UKIs, command line with composefs digest, SELinux workaround module, and `/sysroot`.

Dependencies/integration: cfsctl, kernel-install, ukify, dracut module files, and VM tests.

Risks/test signals: digest must match base content exactly; removing random seed improves reproducibility. Example tests validate boot and persistence.
