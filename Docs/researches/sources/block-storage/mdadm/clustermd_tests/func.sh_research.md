# File Research: sources/block-storage/mdadm/clustermd_tests/func.sh

## Purpose
`func.sh` is the shared harness for clustered mdadm tests.

## Main Flow
It validates the two-node environment, discovers test devices, ensures cluster/DLM services are available, manages cleanup, saves logs, stops arrays locally or remotely, controls RAID sync speed limits, and provides common assertions over `/proc/mdstat`, `mdadm`, and `dmesg`.

## Key Behavior
- `check_ssh()` reads `NODE1`/`NODE2` from `$CLUSTER_CONF` and requires passwordless root SSH.
- `fetch_devlist()` supports either configured device lists or iSCSI target discovery, removes SBD devices, exports `dev0`, `dev1`, etc., and requires at least six disks.
- `check_dlm()` creates Pacemaker DLM resources if absent and verifies `dlm_controld`.
- `check_env()` requires root, built mdadm, required commands, required kernel modules, and no pre-existing RAID arrays.
- `stop_md()` stops all arrays or a specific md device on one or both nodes.
- `save_log()` copies test logs, clears/saves dmesg, captures `/proc/mdstat`, `mdadm -D`, bitmap examination, and superblock examination.
- `check()` implements assertions for spares, RAID level strings, recovery/resync/reshape/PENDING, wait completion, bitmap/nobitmap, chunk size, member state, no sync, readonly state, and dmesg errors.

## Integration Notes
The test scripts source this file and rely on global variables for nodes, devices, mdadm path, log paths, and speed-limit settings. The harness assumes Pacemaker/crm, DLM, md-cluster, ssh, and shared block devices.

## Risks
The harness is environment-sensitive and destructive: it stops md arrays and zeroes devices. Some checks parse human-readable `/proc/mdstat` and may be brittle across kernel output changes.
