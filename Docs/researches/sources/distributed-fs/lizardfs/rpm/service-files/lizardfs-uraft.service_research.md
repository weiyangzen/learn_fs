<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.service

## Purpose
Systemd unit for the LizardFS uRaft high-availability daemon.

## Important APIs, Types, and Functions
Declares `Requires=lizardfs-ha-master.service`, orders after `network.target` and `lizardfs-ha-master.service`, runs `/usr/sbin/lizardfs-uraft` as `User=lizardfs`, sets `PIDFile=/var/run/lizardfs-uraft.pid`, calls `/usr/sbin/lizardfs-uraft-helper demote` in `ExecStopPost`, and disables automatic restart.

## Control Flow, State, and Persistence
Systemd starts the HA master first, then starts the simple foreground uRaft service. On stop, the helper demotes the node. Persistent HA state is not defined in the unit but likely lives in uRaft configuration/state files and master personality metadata.

## Dependencies and Integration Points
Integrates tightly with `lizardfs-ha-master.service`, `lizardfs-uraft`, and `lizardfs-uraft-helper`. It controls HA promotion/demotion safety around the metadata server.

## Risks and Test Signals
Risks include reliance on `ExecStopPost` for demotion, no automatic restart for HA manager failure, PIDFile mismatch with `Type=simple`, ordering that starts master as shadow before HA quorum, and minimal systemd hardening. Test signals are quorum formation, master promotion/demotion, stop demotion behavior, failures of `lizardfs-uraft-helper`, and service state after uRaft exits unexpectedly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.service -->
