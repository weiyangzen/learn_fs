# sources/distributed-fs/ceph-client/net/atm/ioctl.c

## Purpose
`ioctl.c` implements the common ATM socket ioctl dispatcher. It handles generic VCC queries, privileged signaling-daemon attachment, backend autoloading, registered backend/module ioctls, per-device ATM ioctls, and 32-bit compat translations.

## Important APIs and Functions
- `register_atm_ioctl` / `deregister_atm_ioctl`: exported registration API for backend modules such as PPPoATM and BR2684. Entries live in `ioctl_list` under `ioctl_mutex`.
- `do_vcc_ioctl`: primary dispatcher used by native and compat entry points.
- `vcc_ioctl`: native socket `proto_ops.ioctl` callback.
- `vcc_compat_ioctl`: compat callback when `CONFIG_COMPAT` is enabled.
- Compat helpers `do_atm_iobuf`, `do_atmif_sioc`, and `do_atm_ioctl` translate legacy 32-bit ioctl command numbers and pointer layouts.

## Control Flow
The dispatcher first handles socket-local commands (`SIOCOUTQ`, `SIOCINQ`, obsolete `ATM_SETSC`, and `ATMSIGD_CTRL`). `ATMSIGD_CTRL` requires both `CAP_NET_ADMIN` and `CAP_SYS_RAWIO`, rejects compat callers, then calls `sigd_attach` and marks the socket connected. Backend-setting commands request-load `pppoatm` or `br2684` based on the user-provided backend id, then fall through to registered ioctl handlers. Registered handlers are invoked under `ioctl_mutex` with `try_module_get`/`module_put`; the first response other than `-ENOIOCTLCMD` wins. If no backend handles the command, `ATM_GETNAMES` is routed to `atm_getnames`, while interface-specific commands are unpacked into `(buf, len, number)` and forwarded to `atm_dev_ioctl`.

## State and Persistence
Persistent state is the global registered ioctl handler list. User-visible effects include socket state changes for `ATMSIGD_CTRL`, possible module autoload requests, device metadata/stat changes through `atm_dev_ioctl`, and backend binding via registered handlers.

## Dependencies and Integration
Integrates with `resources.c` for device ioctls, `signaling.c` for `sigd_attach`, `pppoatm.c` through the exported registration API, module autoloading via `request_module`, Linux capability checks, and compat pointer helpers from `net/compat.h`.

## Risks and Test Signals
Main risks are user pointer handling, compat divergence, locking/module lifetime for registered handlers, and the intentionally dangerous signaling daemon pointer protocol. Test signals include native and 32-bit ioctl coverage for `ATM_GETNAMES` and `ATM_GETTYPE`, backend autoload/bind tests, permission tests for `ATMSIGD_CTRL` and admin-only device commands, and races where a backend unregisters while ioctls are in flight.
