# sources/distributed-fs/ceph-client/fs/smb/client/smb1debug.c

## Purpose
`smb1debug.c` provides SMB1-specific debug dumping for CIFS packets when deeper debug support is compiled in.

## Important APIs, types, and functions
The single exported function is `cifs_dump_detail(void *buf, size_t buf_len, struct TCP_Server_Info *server)`. Under `CONFIG_CIFS_DEBUG2` it reads `struct smb_hdr` fields and optionally prints the calculated SMB size after running the dialect `check_message` callback.

## Control flow
In debug builds, the function logs command, CIFS error, flags, flags2, MID, PID, and word count. If the server operation's `check_message` accepts the buffer, it logs the buffer pointer and calculated SMB size. In non-debug builds the function is effectively empty.

## State and persistence
There is no state. Output is diagnostic logging only.

## Dependencies and integration points
It depends on `smb1proto.h`, `cifsproto.h`, `cifs_debug.h`, and the server operation callbacks `check_message` and `calc_smb_size`. `smb1ops.c` wires this into `smb1_operations.dump_detail`.

## Risks and test signals
Risks are low but include debug dereference of malformed or too-short buffers and confusion if `server->ops` is incomplete. Test signals are debug builds receiving valid SMB1 PDUs, malformed PDUs, and verifying that non-debug builds compile without runtime behavior.
