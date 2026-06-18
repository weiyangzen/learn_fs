# sources/distributed-fs/openafs/src/sys/rmtsysc.c

## Purpose
`rmtsysc.c` is the client-side RMTSYS implementation. It lets user programs call `setpag` and `pioctl` against a remote AFS client host over RX, falling back to local syscalls when no remote host is configured/reachable.

## Important APIs, types, and functions
Exports include `setpag`, `pioctl`, `GetAfsServerAddr`, `rx_connection`, `afs_get_pag_from_groups`, and `afs_get_groups_from_pag`. Internal `SetClientCreds` captures uid and group state. Global state caches `afs_server`, `server_name`, `hostAddr`, and `hostAddrLookup`.

## Control flow
`GetAfsServerAddr` resolves the remote client from `AFSSERVER`, `$HOME/.AFSSERVER`, or `/.AFSSERVER` and caches the host address. `rx_connection` initializes RX and opens a null-security connection to `AFSCONF_RMTSYSPORT`. `setpag` tries the remote `RMTSYS_SetPag`, converts the returned PAG into two group slots, shifts existing groups if necessary, calls `setgroups`, and resets effective uid; if remote setup fails, it calls `lsetpag`. `pioctl` marshals input data, converts opcode-specific input to network order, expands relative paths, calls `RMTSYS_Pioctl`, converts output back to host order, and falls back to `lpioctl` when no remote connection is available.

## State and persistence behavior
It reads environment and `.AFSSERVER` files, caches remote host lookup, creates RX connections, mutates process groups/PAG via `setgroups`, and forwards pioctls that can mutate cache-manager state on the remote AFS client.

## Dependencies and integration points
It depends on RX, `rmtsys` generated stubs, pioctl conversion routines from `rmtsysnet.c`, local syscall wrappers, group/PAG encoding conventions, and Unix privilege behavior for `setgroups`.

## Risks
Remote calls use RX null security and trust client-supplied credentials encoded in the request. Path buffers are fixed at 256 bytes with `strcpy`/`strcat`. `rx_Init(0)` is called per connection path and global RX lifecycle is not managed here. `setpag` requires setuid-root behavior and can fail or alter group ordering unexpectedly.

## Test signals
Test `AFSSERVER`/home/root fallback resolution, DNS failure, local fallback, remote setpag group insertion when a PAG exists or not, `NGROUPS_MAX` overflow, relative and absolute remote pioctl paths, opcode conversion round trips, and remote errno propagation.
