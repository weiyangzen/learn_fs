<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/staged-deploy.sh -->
## sources/cloud-native/ostree/tests/kolainst/destructive/staged-deploy.sh

Purpose: comprehensive staged deployment behavior test, including finalization, cleanup, locking, upgrade staging, staged/non-staged interactions, ignored `/etc` special files, and boot-complete failure reporting.

Important APIs/functions: uses `ostree admin deploy --stage`, `--lock-finalization`, `lock-finalization`, `undeploy`, `upgrade --stage`, `pin`, `rpm-ostree cleanup`, journal grep/counts, and JSON status checks.

Control flow/state: first phase disables GPG verification, creates socket/FIFO to ignore during `/etc` merge, creates a synthetic commit, stages it, verifies service/ref/state, rejects pinning, and reboots. Second phase verifies finalization logs and syncfs counts, tests cleanup/restaging/locking/upgrade/unstage/overwriting/retaining behavior, then intentionally makes `/boot` immutable and stages kargs to force previous-boot finalization failure. Third phase verifies `ostree-boot-complete` captured that failure.

Dependencies/integration: requires writable sysroot, systemd, SELinux toggle, rpm-ostree, jq, journalctl, chattr, and reboot harness.

Risks/test signals: large destructive surface; can leave immutable `/boot` or staged deployments on interruption. Signals are status text/JSON, `/run/ostree/staged-deployment*`, journal messages, syncfs counts, and captured boot-complete status.
<!-- END_FILE_RESEARCH: sources/cloud-native/ostree/tests/kolainst/destructive/staged-deploy.sh -->
