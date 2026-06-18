<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.cc

## Purpose
Implements `lizardfs-admin list-tapeservers`, listing active tape servers known to the master.

## Important APIs, Types, and Functions
Defines command methods and consumes `TapeserverListEntry` records deserialized by `matocl::listTapeservers`.

## Control Flow, State, and Persistence
`run` validates host/port, sends `cltoma::listTapeservers::build`, receives `LIZ_MATOCL_LIST_TAPESERVERS`, and prints each tapeserver address, server name/id, version, and label in porcelain or human form. No state changes.

## Dependencies and Integration Points
Depends on `ServerConnection`, `protocol/cltoma.h`, `protocol/matocl.h`, `NetworkAddress` embedded in the entry, and version formatting.

## Risks and Test Signals
Risks include unescaped label/server fields in porcelain mode and command behavior when the feature is unsupported or no tapeservers exist. Test signals are empty and nonempty lists, labels with spaces, version formatting, and master protocol errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_tapeservers_command.cc -->
