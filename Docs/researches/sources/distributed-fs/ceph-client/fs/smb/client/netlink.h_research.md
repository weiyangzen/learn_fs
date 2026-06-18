# sources/distributed-fs/ceph-client/fs/smb/client/netlink.h

## Purpose
`netlink.h` is the small internal declaration header for CIFS generic netlink support. It exposes the registered family and lifecycle functions to the rest of the SMB client module.

## Important APIs, types, and functions
The header declares `extern struct genl_family cifs_genl_family`, `int cifs_genl_init(void)`, and `void cifs_genl_exit(void)`. It uses a normal `_CIFS_NETLINK_H` include guard.

## Control flow
There is no runtime control flow in the header. It enables other compilation units to call the registration and unregistration functions implemented in `netlink.c` and to refer to the family object when needed.

## State and persistence behavior
No state is stored here. The declared family is defined in `netlink.c` and registered with generic netlink at module lifecycle boundaries.

## Dependencies and integration points
The header assumes `struct genl_family` is visible where included or through prior includes. It is integrated with CIFS module initialization and witness notification code.

## Risks
Risks are limited to declaration drift: if the family object or lifecycle signatures change in `netlink.c`, this header must change in lockstep. Include-order assumptions around `struct genl_family` should be watched if new users include it without generic netlink headers.

## Test signals
Build coverage is the main signal: compile all configurations that enable CIFS netlink/SWN support and ensure module init/exit users link against these declarations.
