<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.cc

## Purpose
Implements `lizardfs-admin list-chunkservers`, listing connected and recently known chunkservers with capacity, chunk count, error, label, and removal metrics.

## Important APIs, Types, and Functions
Defines `name`, `supportedOptions`, `usage`, `run`, and static `getChunkserversList(masterHost, masterPort)`. It prints `ChunkserverListEntry` records and checks `kDisconnectedChunkserverVersion`.

## Control Flow, State, and Persistence
`getChunkserversList` sends `cltoma::cservList::build(true)` to the master and deserializes `LIZ_MATOCL_CSERV_LIST`. `run` formats each entry, using a special disconnected line when the version sentinel is present. State is read-only and transient.

## Dependencies and Integration Points
Depends on `NetworkAddress`, `lizardfs_version`, `human_readable_format`, `ServerConnection`, and `protocol/chunkserver_list_entry.h`. Other commands reuse `getChunkserversList`, notably `list-disks` and `ready-chunkservers-count`.

## Risks and Test Signals
Risks include porcelain labels not escaped, disconnected output using fixed zero placeholders, downstream commands relying on the helper's inclusion of disconnected entries, and protocol changes to `ChunkserverListEntry`. Test signals are connected/disconnected entries, IPv4/port formatting, labels with spaces, large capacities/errors, and reuse by disk/ready-count commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.cc -->
