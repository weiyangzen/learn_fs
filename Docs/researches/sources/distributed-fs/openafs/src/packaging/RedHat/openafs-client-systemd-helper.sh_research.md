<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client-systemd-helper.sh -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client-systemd-helper.sh

## Purpose
Implements the operational logic behind `openafs-client.service`. It starts the OpenAFS client, stops `/afs`, and performs post-stop cleanup in a way systemd can model while dealing with kernel-module and mount-state edge cases.

## Important APIs, Types, And Functions
The bash script accepts `ExecStart`, `ExecStop`, or `ExecStopPost`. It sources `/etc/sysconfig/openafs`, uses `fs sysname`, `sed`, `chmod`, `lsmod`, `rmmod`, `modprobe`, `/usr/vice/etc/afsd`, `umount`, `mountpoint`, `systemctl is-system-running`, and `sleep`. `UMOUNT_TIMEOUT` controls shutdown retry behavior.

## Control Flow
`ExecStart` first detects an already-running client via `fs sysname` and exits successfully to let systemd regain control. Otherwise it concatenates `CellServDB.local` and `.dist`, ensures permissions, removes a partially initialized loaded `openafs` module, loads the module, and execs `afsd` with configured args. `ExecStop` attempts to unmount `/afs`; during system shutdown it retries for up to 30 seconds if `/afs` remains a mountpoint. `ExecStopPost` runs `afsd -shutdown`, tries to unload the module, and emits explicit remediation instructions if the module remains loaded.

## State And Persistence
The helper rewrites `/usr/vice/etc/CellServDB`, loads/unloads the kernel module, starts/stops `afsd`, and changes the `/afs` mount state. It does not store separate state; it derives state from commands and systemd.

## Dependencies And Integration Points
It is installed by `openafs.spec.in` and referenced by `openafs-client.service`. It depends on OpenAFS client tools in legacy `/usr/vice/etc`, kernel module tooling, systemd state, and `/etc/sysconfig/openafs` for `AFSD_ARGS`.

## Risks And Test Signals
Risks include assuming `fs` is available in PATH, service activation when an old client is running, unmount races with active `/afs` users, and systemd considering the service inactive when module unload fails. Test signals include clean start from unloaded state, idempotent start when already running, stop during active `/afs` use, shutdown retry behavior, and accurate failure messaging when `rmmod` cannot unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client-systemd-helper.sh -->
