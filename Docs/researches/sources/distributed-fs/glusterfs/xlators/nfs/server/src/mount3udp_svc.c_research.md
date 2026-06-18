<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3udp_svc.c -->
# sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3udp_svc.c

## Purpose

`mount3udp_svc.c` implements the ONC RPC UDP transport entry point for MOUNT v3. It decodes UDP MNT and UMNT requests, delegates filehandle lookup and mount-list mutation to `mount3.c`, sends XDR replies with libc/TIRPC svc APIs, and runs the UDP service thread when `nfs.mount-udp` is enabled. Source read: complete 237-line file.

## Important APIs, Types, and Functions

The external entry point is `mount3udp_thread`. Request handlers are `mountudpproc3_mnt_3_svc` and `mountudpproc3_umnt_3_svc`. The dispatcher is `mountudp_program_3`. It relies on external functions `nfs3_rootfh`, `mnt3svc_set_mountres3`, `mount3udp_add_mountlist`, `mount3udp_delete_mountlist`, and `mnt3svc_errno_to_mnterr`. The global `mnthost` stores the IPv4 caller address for the single UDP service path.

## Control Flow

`mount3udp_thread` sets `THIS`, creates a UDP transport with `svcudp_create`, registers MOUNT program version 3 with `svc_register`, and starts the NFS RPC poller. `mountudp_program_3` obtains the caller IPv4 address with `svc_getcaller`, stores it in `mnthost`, selects XDR routines and local handlers for `NULLPROC`, `MOUNT3_MNT`, or `MOUNT3_UMNT`, decodes arguments, invokes the local handler, sends the reply, frees arguments, and releases allocated result data.

For MNT, `mountudpproc3_mnt_3_svc` strips leading slashes, allocates a `mountres3` and one AUTH_UNIX flavor, calls `nfs3_rootfh`, maps errno to a MOUNT status on failure, and on success adds the client/export to the mount list. UMNT allocates a `mountstat3`, returns `MNT3_OK`, and deletes the mount-list entry.

## State and Persistence Behavior

This file has minimal local state: the global `mnthost` buffer and per-request allocations for replies and auth flavor arrays. Persistent and shared state is delegated to `mount3udp_add_mountlist` and `mount3udp_delete_mountlist`, which update `mount3_state` and rmtab in `mount3.c`.

## Dependencies and Integration Points

It depends on generated NFS XDR types, Gluster logging/memory APIs, `mount3.h`, libc/TIRPC svc APIs, portmap registration, and the NFS RPC poller. Its filehandle path is entirely integrated through `nfs3_rootfh` in `mount3.c`.

## Risks and Edge Cases

The code asserts IPv4 caller family and does not implement IPv6 UDP MOUNT. `mnthost` is global and documented as safe because only this thread uses it; that assumption matters if UDP serving changes. Failure paths must free `fh`, `res`, and auth arrays consistently. UDP mount list insertion delegates to a path that does not suppress duplicates as strictly as TCP.

## Test Signals

Enable `nfs.mount-udp` and run UDP MOUNT/UMNT interoperability tests, including bad export paths, auth rejection, stopped subvolumes, and allocation-failure simulation. Packet-level tests should confirm NULLPROC, MNT, UMNT, XDR decode errors, and unsupported procedure handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/glusterfs/xlators/nfs/server/src/mount3udp_svc.c -->
