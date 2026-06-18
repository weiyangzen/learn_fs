<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-master.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-master.service

## Purpose
Systemd unit for a standalone LizardFS master server.

## Important APIs, Types, and Functions
Defines `Type=forking`, `TimeoutSec=0`, `/usr/sbin/mfsmaster start|stop|reload`, `Restart=no`, documentation `man:mfsmaster`, and ordering after `network.target`.

## Control Flow, State, and Persistence
Systemd invokes the legacy master control interface and does not restart it automatically. Persistent behavior is owned by `mfsmaster`: metadata files, changelogs, lock/PID files, and configured networking.

## Dependencies and Integration Points
Integrates with LizardFS metadata service configuration, metaloggers, chunkservers, clients, and admin commands that connect to the master port.

## Risks and Test Signals
Risks include no automatic restart for crashes, no explicit filesystem dependency for metadata storage, `TimeoutSec=0` hiding hung control operations, and limited hardening. Test signals are start/stop/reload, client/chunkserver registration, metadata save/load on restart, and systemd state matching the daemonized master process.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-master.service -->
