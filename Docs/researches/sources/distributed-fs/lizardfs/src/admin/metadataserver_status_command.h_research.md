<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.h -->
# sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.h

## Purpose
Declares metadata-server status reporting types and command.

## Important APIs, Types, and Functions
Defines `struct MetadataserverStatus { std::string personality; std::string serverStatus; uint64_t metadataVersion; }` and `MetadataserverStatusCommand` with overrides plus static `getStatus(ServerConnection&)`.

## Control Flow, State, and Persistence
No state is stored; the struct is a value return from protocol decoding.

## Dependencies and Integration Points
Includes `common/server_connection.h` and the base command header. The static helper is shared by `list-metadataservers`.

## Risks and Test Signals
Risks include stringly typed status/personality and helper coupling to live network connections. Build and protocol mapping tests are signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/metadataserver_status_command.h -->
