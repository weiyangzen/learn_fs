# sources/distributed-fs/lizardfs/src/data/mfsmaster.cfg.in

Purpose: configured sample master/shadow metadata-server configuration.

Important settings: master personality, admin password, user/group, exports/topology/goals paths, data path, metadata recovery/backlog retention, chunk operation delay/limits, listen hosts/ports for metaloggers/chunkservers/clients/tapeservers, chunk loop pacing/CPU budget, deletion/replication limits, endangered chunk priority, balancing thresholds, inode/session options, global I/O limits, shadow-master connection, metadata checksum behavior, Berkeley DB name storage, same-IP avoidance, load factor penalty, redundancy level, snapshot batch sizing, and file-test loop timing.

Control flow: CMake fills default paths; `main.cc` loads the config at daemon startup and module reload callbacks consume individual keys. `chunks.cc` specifically reads chunk loop, deletion, replication, endangered, balancing, same-IP, and redundancy settings.

State and persistence: persistent master configuration controlling metadata storage and cluster behavior; does not itself contain metadata.

Dependencies and integration: references `mfsexports.cfg`, `mfstopology.cfg`, `mfsgoals.cfg`, `globaliolimits.cfg`, `mfsmetarestore`, shadow/master ports, and chunk maintenance modules.

Risks: settings directly affect safety and availability. `AUTO_RECOVERY`, checksum verification, deletion/replication limits, and redundancy controls are especially sensitive. Several deprecated names remain for compatibility.

Test signals: no direct tests for the sample; runtime parsers enforce some min/max constraints in modules such as `chunks.cc` and `changelog.cc`.
