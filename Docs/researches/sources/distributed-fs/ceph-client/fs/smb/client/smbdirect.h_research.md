# sources/distributed-fs/ceph-client/fs/smb/client/smbdirect.h

## Purpose
`smbdirect.h` declares the CIFS client wrapper interface for SMBDirect/RDMA support and provides no-op stubs when `CONFIG_CIFS_SMB_DIRECT` is disabled.

## Important APIs, Types, And Functions
When enabled, it defines `cifs_rdma_enabled(server)`, exposes RDMA tunables, declares `struct smbd_connection { struct smbdirect_socket *socket; }`, and prototypes connection, send/recv, MR registration, buffer descriptor fill, MR deregistration, and debug display functions. When disabled, it defines `cifs_rdma_enabled(server)` as `0`, an empty `struct smbd_connection`, and inline stubs returning `NULL` or `-1`.

## Control Flow
There is no runtime control flow in the header. Compile-time configuration selects real SMBDirect declarations or stubs, allowing the rest of the SMB client to compile with minimal feature-condition checks.

## State And Persistence Behavior
The enabled struct stores the SMBDirect socket pointer. No additional state is maintained here. Disabled stubs intentionally prevent RDMA state from existing.

## Dependencies And Integration Points
The enabled branch includes CIFS globals and `linux/smbdirect.h`. `smb2pdu.c`, transport setup, debug proc code, and connection management use this header to conditionally integrate RDMA behavior.

## Risks
The disabled stubs return generic `-1` rather than a specific errno, so callers should generally be protected by `cifs_rdma_enabled` or compile-time guards. Any new enabled API must receive a matching stub or non-RDMA builds will fail.

## Test Signals
Build both `CONFIG_CIFS_SMB_DIRECT=y/m` and disabled configurations. Runtime tests should verify non-RDMA mounts never enter stub send/recv paths and RDMA builds expose the expected wrapper functions.
