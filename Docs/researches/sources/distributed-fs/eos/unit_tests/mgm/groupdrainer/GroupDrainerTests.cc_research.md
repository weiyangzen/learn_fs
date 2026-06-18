# sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/GroupDrainerTests.cc

## sources/distributed-fs/eos/unit_tests/mgm/groupdrainer/GroupDrainerTests.cc

Purpose: tests static status-reduction helpers in `GroupDrainer`.

Important APIs and types: `GroupDrainer::checkGroupDrainStatus`, `GroupDrainer::isDrainFSMapEmpty`, `GroupStatus`, `FsidStatus`, `fs_status_map_t`, `drain_fs_map_t`, `ActiveStatus`, and `DrainStatus`.

Control flow: status tests build maps of filesystem active/drain states and assert group-level results. All online drained filesystems yield `DRAINCOMPLETE`. Any offline filesystem yields `OFF` and takes precedence. Failed drain states yield `DRAINFAILED` unless unknown/expired online states push the result to the catchall `ON`. `isDrainFSMapEmpty` checks empty maps and groups with empty vectors.

State and persistence: no persistent state. Tests reduce local maps into derived status.

Dependencies and integration: these helpers are central to group-drainer state aggregation from filesystem-level MGM status.

Risks and test signals: precedence ordering is the main risk. Offline dominates failed, while certain unknown states return `ON`; callers must understand that this is not a pure severity ordering.
