<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.cc -->
# sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.cc

## Purpose
Implements `lizardfs-admin list-metadataservers`, listing the active master and shadow metadata servers with status, hostname, personality, metadata version, and software version.

## Important APIs, Types, and Functions
Defines command methods and overloaded variadic `printInfo` helpers. It consumes `MetadataserverListEntry` and calls `MetadataserverStatusCommand::getStatus`.

## Control Flow, State, and Persistence
`run` resolves the supplied master host/port to numeric address, requests `cltoma::metadataserversList::build`, deserializes master version and shadow list, inserts the connected master entry at the beginning by appending then reversing, and for each server with known port opens a direct connection to query status and hostname. It prints a block per server or a porcelain sequence of values. No state is changed.

## Dependencies and Integration Points
Depends on socket resolution (`tcpresolve`), `ServerConnection`, metadata server list/status/hostname protocols, `lizardfs_version`, and `MetadataserverStatusCommand`.

## Risks and Test Signals
Risks include sequential direct queries causing the whole command to fail if one shadow is unreachable, port-zero entries yielding unknowns, porcelain output spanning multiple lines per server without explicit record separators beyond `printInfo`, and the master insertion/reverse hack. Test signals are master-only clusters, shadow connected/disconnected/port-zero entries, hostname failures, status mapping, porcelain parsing, and DNS/port resolution errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/list_metadataservers_command.cc -->
