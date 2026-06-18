<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.h -->
# sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.h

## Purpose
Declares the chunkserver listing command and its reusable static fetch helper.

## Important APIs, Types, and Functions
`ListChunkserversCommand` overrides `name`, `supportedOptions`, `usage`, and `run`, and declares `static std::vector<ChunkserverListEntry> getChunkserversList(...)`.

## Control Flow, State, and Persistence
The header has no state. The helper declaration makes chunkserver discovery a shared integration point for other admin commands.

## Dependencies and Integration Points
Includes `common/network_address.h`, serialization macros, `protocol/chunkserver_list_entry.h`, and the base command header.

## Risks and Test Signals
Risks include broad coupling through the static helper and includes that expose protocol details to users. Build coverage of all callers and CLI tests around disconnected servers are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_chunkservers_command.h -->
