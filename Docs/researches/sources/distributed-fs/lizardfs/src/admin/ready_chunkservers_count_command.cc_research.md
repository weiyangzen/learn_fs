<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.cc

## Purpose
Implements `lizardfs-admin ready-chunkservers-count`, printing a simple count of chunkservers considered writable.

## Important APIs, Types, and Functions
Defines command methods and reuses `ListChunkserversCommand::getChunkserversList`.

## Control Flow, State, and Persistence
`run` requires master host/port, fetches chunkservers, counts entries whose `totalspace > 0`, and prints the count. It is read-only and has no options.

## Dependencies and Integration Points
Depends on the chunkserver listing helper and the semantics of `ChunkserverListEntry::totalspace`.

## Risks and Test Signals
Risks include treating any nonzero total space as ready even if the server is disconnected, damaged, full, labeled out, or otherwise unwritable; it also ignores available space. Test signals are connected/disconnected entries, zero/positive total space, full disks, and consistency with actual master write placement decisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/ready_chunkservers_count_command.cc -->
