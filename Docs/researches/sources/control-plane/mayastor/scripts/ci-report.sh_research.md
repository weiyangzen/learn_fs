# sources/control-plane/mayastor/scripts/ci-report.sh

Purpose: gathers system diagnostics into a compressed CI report bundle.

Important APIs/types/functions: sets `ROOT_DIR`, chooses `nix-sudo` or `sudo`, uses `CI_REPORT_START_DATE`, writes `journalctl.txt`, `dmesg.txt`, `lsblk.txt`, `nvme.txt`, `meminfo.txt`, masks GitHub tokens matching `ghs_...`, and creates `ci-report.tar.gz`.

Control flow: creates `ci-report` directory, collects logs and hardware state, then tars `.txt` and `.xml` files found in that directory.

State/persistence: writes/overwrites files under `ci-report`.

Dependencies/integration: used by CI for post-failure artifacts; integrates journalctl, lsblk, nvme-cli, sudo/nix-sudo, and tar.

Risks: token masking is narrow and may not catch all secrets. It appends `nvme list-subsys` output to the same file and assumes sudo access.

Test signals: generated tarball should contain recent logs and NVMe/block-device state.
