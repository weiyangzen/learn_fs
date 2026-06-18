# sources/distributed-fs/lizardfs/src/data/mfshdd.cfg

Purpose: sample chunkserver disk mount-point list.

Important syntax: one storage path per line; prefixing a path with `*` marks that mount point for removal.

Control flow: chunkserver reads the configured HDD file to discover storage directories and removal intent. The shipped file contains only commented examples.

State and persistence: administrator-managed persistent disk list; actual chunk state lives under the referenced mount points.

Dependencies and integration: installed as a chunkserver example and referenced by `HDD_CONF_FILENAME` in `mfschunkserver.cfg.in`.

Risks: mistaken active paths or removal markers can affect chunk availability and deletion/migration behavior.

Test signals: no direct tests in this subset.
