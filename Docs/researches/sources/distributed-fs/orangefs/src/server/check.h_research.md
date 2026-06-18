# sources/distributed-fs/orangefs/src/server/check.h

## Purpose
Declares the server permission-checking API implemented by `check.c`.

## Important APIs, Types, And Functions
The header exports `PINT_perm_check(struct PINT_server_op *s_op)` for operation-level authorization and `PINT_get_capabilities(...)` for deriving a capability mask from ACL/mode/credential inputs. It includes `pvfs2-types.h`, `pvfs2-attr.h`, and `pvfs2-server.h` so callers see the required OrangeFS object, attribute, and server-op types.

## Control Flow
No control flow is implemented in the header. Server state-machine code includes it to call `PINT_perm_check`, while capability-producing code calls `PINT_get_capabilities` after fetching object attributes and optional ACL data.

## State And Persistence
The header declares no state. Its API surfaces transient request state, object attributes, ACL buffers, group arrays, and output capability masks.

## Dependencies And Integration Points
This is the public boundary between generated/manual server state machines and the permission helper module. It must remain consistent with `check.c` and with struct definitions in `pvfs2-server.h` and `pvfs2-attr.h`.

## Risks And Test Signals
Risks are declaration drift and accidental inclusion cycles because the header includes broad server definitions. Compile coverage of server state machines and permission unit/integration tests are the main signals.
