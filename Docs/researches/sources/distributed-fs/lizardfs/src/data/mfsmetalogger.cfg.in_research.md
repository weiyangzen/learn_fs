# sources/distributed-fs/lizardfs/src/data/mfsmetalogger.cfg.in

Purpose: configured sample metalogger daemon configuration.

Important settings: working user/group, syslog identity, memory lock/nice level, metadata data path, changelog backlog retention, previous metadata retention, metadata download frequency, master reconnection delay, master host/port, and connection timeout.

Control flow: CMake substitutes defaults; metalogger reads active settings to connect to the master and persist metadata/changelog backups.

State and persistence: persistent daemon config; controls where replicated metadata files are stored and how often snapshots are downloaded.

Dependencies and integration: installed as a metalogger example; coordinates with master `MATOML` port and changelog retention.

Risks: too few backlogs or infrequent metadata downloads can reduce recovery coverage; incorrect master host/port leaves the metalogger stale.

Test signals: no direct tests in this subset.
