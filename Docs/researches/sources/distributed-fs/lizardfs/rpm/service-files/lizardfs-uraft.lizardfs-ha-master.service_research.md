<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.lizardfs-ha-master.service -->
# sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.lizardfs-ha-master.service

## Purpose
Alternate or templated packaging copy of the HA master systemd unit used with the uRaft high-availability service.

## Important APIs, Types, and Functions
Its contents match `lizardfs-ha-master.service`: `Type=forking`, `TimeoutSec=0`, `PartOf=lizardfs-uraft.service`, and `mfsmaster -o ha-cluster-managed -o initial-personality=shadow` for start/stop/reload.

## Control Flow, State, and Persistence
Lifecycle follows systemd and uRaft coupling; master metadata persistence is owned by `mfsmaster`, while the unit only controls initial HA personality and cluster-managed mode.

## Dependencies and Integration Points
Integrates with `lizardfs-uraft.service`; the filename suggests packaging/install logic may use it as a service-specific override or renamed companion.

## Risks and Test Signals
Risks are the same as the primary HA master unit plus drift between duplicate service files. Test signals should compare installed units, start/stop under uRaft, verify initial shadow personality, and check packaging chooses the intended filename.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/rpm/service-files/lizardfs-uraft.lizardfs-ha-master.service -->
