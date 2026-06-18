# sources/distributed-fs/lizardfs/src/master/masterconn.h

## Purpose

`masterconn.h` is the small public interface for the master-to-master/metalogger connection module implemented in `masterconn.cc`. It exposes initialization and a connection-status query to other master components while hiding the singleton connection internals.

## Important APIs

- `int masterconn_init(void)`: starts the module when applicable. In non-metalogger builds it is a no-op unless the metadata server personality is shadow. In active mode it reads config, opens the master connection, and registers event-loop hooks.
- `bool masterconn_is_connected()`: returns whether the shadow/metalogger connection is registered and usable, not merely whether the socket exists.

The header includes `common/platform.h`, `<inttypes.h>`, and `<stdio.h>`. The latter two are not needed by the declarations themselves but are consistent with older C-style headers in this codebase.

## Control Flow And Integration

Other master modules call `masterconn_init()` during startup to attach the replication/metalogger client to the event loop. `matoclserv.cc` calls `masterconn_is_connected()` when answering metadata-server status requests so clients/admin tools can distinguish shadow-connected from shadow-disconnected states.

## State And Persistence Behavior

The header declares no state. All connection, packet, metadata-download, and changelog cursor state is private to `masterconn.cc`.

## Dependencies And Risks

The interface is intentionally narrow. The main risk is semantic: callers must understand that `masterconn_is_connected()` reports successful protocol registration, not just TCP connectivity. Tests that mock or drive status reporting should account for this distinction.

## Test Signals

Compile-level tests should ensure both `METALOGGER` and normal master builds include this header cleanly. Integration tests should verify that status consumers report disconnected before registration and connected only after the master version is known.
