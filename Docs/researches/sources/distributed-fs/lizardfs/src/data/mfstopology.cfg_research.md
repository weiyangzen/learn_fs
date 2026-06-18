# sources/distributed-fs/lizardfs/src/data/mfstopology.cfg

Purpose: sample topology grouping file for master distance decisions.

Important syntax: maps IP ranges/networks/single addresses to rack/group IDs. Supports CIDR bit counts, explicit ranges, dotted netmasks, and individual addresses.

Control flow: master topology parser reads entries and assigns connecting chunkservers/mounts to groups; unspecified hosts default to group 0. Distance values feed client read-location sorting and placement/rebalancing decisions.

State and persistence: persistent topology policy; no active entries in the shipped sample.

Dependencies and integration: installed as a master example and referenced by `TOPOLOGY_FILENAME`; consumed by `topology_distance`, including calls from `chunks.cc`.

Risks: stale or overly broad ranges can bias reads/replication incorrectly. Overlapping definitions add information rather than replacing it, per the comments.

Test signals: no direct tests in this subset.
