<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.h -->
# sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.h

## Purpose
Declares the authenticated admin connection type used by privileged `lizardfs-admin` commands.

## Important APIs, Types, and Functions
`RegisteredAdminConnection` derives from `KeptAliveServerConnection` and exposes static `create(host, port, timeout = kDefaultTimeout)`. The constructor is private so callers must authenticate through `create`.

## Control Flow, State, and Persistence
The object inherits all socket/keepalive state from `KeptAliveServerConnection`; the header only constrains construction.

## Dependencies and Integration Points
Includes `common/server_connection.h` and `<memory>`. Mutating command implementations receive `std::unique_ptr<RegisteredAdminConnection>`.

## Risks and Test Signals
Risks include inherited connection behavior being exposed without extra authorization checks after creation. Build tests and authenticated command integration cover it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/lizardfs/src/admin/registered_admin_connection.h -->
