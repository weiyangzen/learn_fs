<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-metalogger.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-metalogger.service

## Purpose
Systemd unit for the LizardFS metalogger daemon, which tails/replicates metadata changelog data from the master.

## Important APIs, Types, and Functions
Uses `Type=forking` and `/usr/sbin/mfsmetalogger start|stop|reload`, restarts on abort, and is ordered after `network.target`.

## Control Flow, State, and Persistence
The unit starts the daemonized metalogger and delegates state management to `mfsmetalogger`. Persistent state includes downloaded metadata/changelog data and daemon lock/PID files outside the unit definition.

## Dependencies and Integration Points
Integrates with master network availability and metalogger configuration. It is operationally related to disaster recovery and metadata backup workflows.

## Risks and Test Signals
Risks include no explicit dependency on the master being reachable, no filesystem mount dependency for backup storage, and restart-on-abort only handling abort-class failures. Test signals are successful master connection, metadata/changelog replication, reload of configuration, clean stop, and behavior during master outage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-metalogger.service -->
