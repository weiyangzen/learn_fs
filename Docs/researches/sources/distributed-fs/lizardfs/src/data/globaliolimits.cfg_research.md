# sources/distributed-fs/lizardfs/src/data/globaliolimits.cfg

Purpose: sample global I/O limiting configuration for master-controlled bandwidth groups.

Important syntax: commented `subsystem blkio` and `limit <group> <value>` examples, including `unclassified` and nested group paths like `/some_group/some_subgroup`.

Control flow: parsed at runtime by the global I/O limits subsystem when configured through `GLOBALIOLIMITS_FILENAME`; this file itself is an example with all directives commented.

State and persistence: persisted administrator configuration; no active limits until copied/edited and comments removed.

Dependencies and integration: installed as a master example by `src/data/CMakeLists.txt`; referenced by `mfsmaster.cfg.in`.

Risks: units and subsystem behavior are not explained in this file beyond the manpage reference, so operators must consult `globaliolimits.cfg(5)`.

Test signals: no direct tests; parser coverage would be in the I/O limits code, not this sample.
