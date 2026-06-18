<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client.service -->
# sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client.service

## Purpose
Defines the systemd unit for the OpenAFS client. It delegates lifecycle operations to `openafs-client-systemd-helper.sh` and arranges ordering relative to network and remote filesystem targets.

## Important APIs, Types, And Functions
The unit uses `Wants=network-online.target`, `After=syslog.target network-online.target dkms.service`, `Before=remote-fs.target`, `Type=forking`, `RemainAfterExit=true`, helper-backed `ExecStart`, `ExecStop`, and `ExecStopPost`, plus `KillMode=process`, `GuessMainPID=no`, `SendSIGKILL=no`, and `KillSignal=SIGCONT`.

## Control Flow
On start, systemd invokes the helper's `ExecStart`; the helper loads the module and starts `afsd`. On stop, systemd invokes helper `ExecStop` to unmount `/afs`, then always runs `ExecStopPost` to shut down afsd and unload the module. Installation enables the unit for both `multi-user.target` and `remote-fs.target`.

## State And Persistence
The unit stores no state itself. It models OpenAFS as remaining active after the start command exits and relies on mount/module state maintained by the helper and kernel.

## Dependencies And Integration Points
It is packaged by the RPM spec for systemd-capable Fedora/RHEL/Amazon systems. It integrates with DKMS ordering, network availability, remote-fs ordering, and the legacy `/usr/vice/etc` helper path.

## Risks And Test Signals
Risks include forking-service modeling without a tracked main PID, unusual `KillSignal=SIGCONT`, and inactive unit state when `/afs` remains mounted after failed stop. Test signals are `systemctl start/stop/status`, correct ordering at boot/shutdown, no forced kill of cache-manager processes, and clear journal output from the helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/openafs/src/packaging/RedHat/openafs-client.service -->
