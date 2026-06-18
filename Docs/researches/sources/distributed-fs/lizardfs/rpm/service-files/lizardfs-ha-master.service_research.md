<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-ha-master.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-ha-master.service

## Purpose
Systemd unit for a LizardFS master managed by high-availability tooling, started initially as a shadow under cluster control.

## Important APIs, Types, and Functions
Uses `Type=forking`, `TimeoutSec=0`, and runs `/usr/sbin/mfsmaster -o ha-cluster-managed -o initial-personality=shadow start|stop|reload`. It has `PartOf=lizardfs-uraft.service` and is ordered after `syslog.target` and `network.target`.

## Control Flow, State, and Persistence
Systemd starts/stops the master wrapper, while `PartOf` ties lifecycle to the uRaft HA daemon. Persistent metadata state remains in LizardFS metadata files; this unit influences startup personality and HA management flags.

## Dependencies and Integration Points
Integrates with `lizardfs-uraft.service`, `/usr/sbin/mfsmaster`, and HA cluster promotion/demotion flows.

## Risks and Test Signals
Risks include split-brain if uRaft and master lifecycle ordering is wrong, indefinite start/stop waits due to `TimeoutSec=0`, and manual starts outside uRaft changing personality expectations. Test signals are paired start/stop with `lizardfs-uraft.service`, initial shadow status, promotion through HA, reload propagation, and metadata server status queries after boot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-ha-master.service -->
