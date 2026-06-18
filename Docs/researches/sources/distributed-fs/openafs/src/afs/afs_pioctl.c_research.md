# sources/distributed-fs/openafs/src/afs/afs_pioctl.c

## Purpose

`afs_pioctl.c` implements the Unix/OpenAFS cache manager's path ioctl and vnode ioctl control plane. It is the kernel-facing backend for many `fs` command operations: ACL fetch/store, token set/get/unlog, cache and callback flushes, cell and alias management, volume status changes, server preference tuning, RX statistics toggles, disconnected-mode transitions, callback address changes, NFS translator credential handling, and FID/status inspection. It also provides small buffer-cursor helpers (`struct afs_pdata`) that make the varied pioctl payload formats less fragile than open-coded pointer arithmetic.

## Important APIs, types, and functions

- `struct afs_pdata` tracks a moving pointer and remaining byte count for pioctl input/output buffers. Helpers include `afs_pd_alloc`, `afs_pd_free`, `afs_pd_getBytes`, `afs_pd_getInt`, `afs_pd_getStringPtr`, `afs_pd_putBytes`, `afs_pd_putString`, `afs_pd_inline`, and XDR wrappers `afs_pd_xdrStart`/`afs_pd_xdrEnd`.
- `DECL_PIOCTL(name)` defines the common internal pioctl handler signature: `(struct vcache *avc, int afun, struct vrequest *areq, struct afs_pdata *ain, struct afs_pdata *aout, afs_ucred_t **acred)`.
- `VpioctlSw`, `CpioctlSw`, and `OpioctlSw` map pioctl device/function numbers to handlers. Device `'V'` carries original Venus pioctls, `'C'` newer coordinated/common operations, and `'O'` OpenAFS/private operations.
- `HandleIoctl` handles vnode ioctl commands on an already-open AFS vnode. It is much smaller than the pioctl path and supports safe-store, file-cell lookup, and cache-manager init parameter retrieval.
- `afs_xioctl` has multiple platform-specific implementations for AIX, SGI, Solaris, Linux, Darwin/BSD, and UKERNEL. Each detects AFS vnodes, copies in `struct afs_ioctl`, enters the AFS global lock where needed, and routes to `HandleIoctl`; non-AFS calls are passed through or rejected.
- `afs_syscall_pioctl` is the main syscall entry: it copies in the `afs_ioctl` descriptor, optionally applies NFS translator client context, handles the prefetch special case, resolves the path to a vnode, and dispatches to `afs_HandlePioctl`.
- `afs_HandlePioctl` creates a `vrequest`, evaluates fakestat, validates device/function and buffer sizes, copies user input into kernel memory, allocates output space, calls the selected handler, copies output to user space, and finalizes request/error handling.

## Control flow

The vnode ioctl family starts with platform-specific `afs_xioctl` or AIX `afs_ioctl` wrappers. These inspect the file descriptor/vnode, confirm it is an AFS vnode, copy the small `struct afs_ioctl` descriptor from userspace, then call `HandleIoctl`. `HandleIoctl` switches on the low command byte and performs a few legacy ioctl operations without the full path-lookup/pioctl machinery.

The path pioctl family enters through `afs_syscall_pioctl` (or `afs_syscall64_pioctl` on modern Darwin). The function normalizes `follow`, copies in the user `struct afs_ioctl`, and checks for `PSetClientContext`, which allows an NFS translator process to supply remote client credentials. It special-cases VIOC prefetch so the whole pathname evaluation can run in a background helper. Otherwise it resolves `path` to a vnode with platform lookup helpers, optionally unwraps Solaris real vnodes, and only proceeds when the target is absent or an AFS vnode. It then calls `afs_HandlePioctl` with the vnode, command, descriptor, follow flag, and active credentials.

`afs_HandlePioctl` performs common dispatch: create `vrequest`, evaluate fakestat, choose the `V`/`C`/`O` switch table, validate lengths, copy input into an `afs_pdata`, allocate output, call the selected handler, compute output length from pointer movement, copy output back, zero/free buffers, release fakestat state, map errors through `afs_CheckCode`, and destroy the request.

## State and persistence behavior

This file mutates extensive cache-manager runtime state: pioctl globals, message gag flags, disconnected-mode state, default store-behind asynchrony, NFS exporter policy, RX encryption/tunable state, probe interval, cache size counters, callback interface addresses/UUID, sysname generation, server rankings, and token/user structures.

Token state is stored in `struct unixuser` entries keyed by PAG/uid and cell. Legacy and XDR token setters replace token jars; token getters export them; unlog/nuke paths clear tokens and reset user connections. Cache state changes include single-vcache resets, volume/all-volume flushes, cache-size changes, DNLC purges, and disconnected-mode resync/discard behavior. Server-persistent changes are made through RXAFS ACL, volume status, remove-file, and residency/command RPCs.

## Dependencies and integration points

`afs_pioctl.c` integrates with vcache/fakestat, dcache, cell, volume, user/token, server/ranking, RX/RXAFS, directory, DNLC, background daemon, OS vnode/credential, PAG, NFS exporter, sysname, disconnected-mode, and cache-bypass subsystems. Its public entry points are declared in `afs_prototypes.h`, while the user ABI is defined by `struct afs_ioctl`, command numbers, token XDR types, and `fs` command payload structures.

## Risks and edge cases

- This is a security-sensitive syscall surface with many root-only and credential-substitution paths.
- Several handlers depend on variable-length struct layouts and array-overrun ABI conventions.
- String extraction uses `strlen` on the current cursor; the allocation guard NUL helps, but malformed field layouts remain worth fuzzing.
- `afs_pd_free` zeroes only the current remaining span, so consumed sensitive token bytes may not be scrubbed by that helper.
- The switch-table bounds calculation divides by `sizeof(char *)` instead of function-pointer size.
- `PCheckServers` peeks at an `afs_int32` directly from the buffer, which can be alignment-sensitive.
- Disconnected-mode numeric ABI values must stay synchronized with userland `fs.c`.

## Test signals

Run pioctl ABI tests for all populated `V`, `C`, and `O` entries; malformed size/string/XDR fuzzing; token set/get/unlog round trips; authorization checks; NFS translator context tests; ACL/volume RPC tests; cache flush and cache-size tests with dirty/reference chunks; server preference pagination; sysname validation; disconnected offline/online/force flows; and platform wrapper tests for AFS vs non-AFS ioctls. Kernel instrumentation should watch buffer bounds, credential references, token memory scrubbing, and vnode/dentry lock ordering.
