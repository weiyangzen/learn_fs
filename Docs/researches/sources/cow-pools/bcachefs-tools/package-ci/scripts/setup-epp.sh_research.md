# File Research: sources/cow-pools/bcachefs-tools/package-ci/scripts/setup-epp.sh

## Purpose
One-time setup script for package CI on `evilpiepirate.org`.

## Workflow
- Requires root.
- Installs podman, sbuild, mmdebstrap, aptly, gnupg, devscripts, git-buildpackage, qemu-user-static, and uidmap.
- Configures subuid/subgid ranges for `aptbcachefsorg`.
- Creates CI directories and cache directories.
- Installs the git post-receive hook if absent.
- Installs and enables the systemd service.
- Prints manual follow-up deployment and GPG setup steps.

## Notes
The script does not build or deploy the Rust orchestrator binary itself; it documents those as next steps.
