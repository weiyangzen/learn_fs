# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/ima_setup.sh

Purpose: helper script for IMA-related BPF selftests to create a loopback ext2 filesystem, install an IMA measurement policy, run/modify/restore a copied test binary, and clean up.

Important APIs and functions: actions `setup`, `cleanup`, `run`, `modify-bin`, `restore-bin`, and `load-policy`; `ensure_mount_securityfs()` mounts securityfs if needed; setup uses `dd`, `losetup`, `mkfs.ext2`, `mount`, `blkid`, and writes `/sys/kernel/security/ima/policy`.

Control flow: validates two arguments, routes by action, captures logs to a temp file unless verbose, and uses an EXIT trap to print logs only on failure.

State and persistence: creates a loop image, loop device, mount directory, copied `/bin/true`, policy file, and possibly active IMA policy entries. Cleanup detaches loop devices, unmounts, and removes tmpdir.

Dependencies and integration points: requires root privileges, loop device support, ext2 tools, securityfs, IMA enabled, and writable IMA policy.

Risks: cleanup order detaches loop devices before unmounting, which can fail depending on kernel behavior; loop device discovery by grepping image path can match multiple stale devices; appending/truncating binary assumes `modify-bin` appends exactly four bytes.

Test signals: run action executes copied binary to trigger IMA; load-policy failures are intentionally suppressible; errors print captured command logs when not verbose.
