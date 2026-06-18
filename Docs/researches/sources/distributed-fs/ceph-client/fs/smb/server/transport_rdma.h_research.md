## sources/distributed-fs/ceph-client/fs/smb/server/transport_rdma.h

Purpose: declares ksmbd SMB Direct/RDMA transport lifecycle and capability APIs, with stubs when SMBDirect server support is disabled.

Important APIs and types: defines default/min/max SMBDirect I/O sizes (`8 MiB`, `512 KiB`, `16 MiB`) and declares `ksmbd_rdma_init`, `ksmbd_rdma_stop_listening`, `ksmbd_rdma_capable_netdev`, `init_smbd_max_io_size`, and `get_smbd_max_read_write_size`. Disabled builds return success/no-op/false/zero as appropriate.

Control flow: server startup can call RDMA init unconditionally because the header supplies disabled stubs. Runtime sizing and network-interface info call the capability helpers without depending on the configuration.

State and persistence behavior: this header owns no state. Enabled implementation stores listener and negotiated transport state in `transport_rdma.c`.

Dependencies and integration points: includes `linux/smbdirect.h` and is used by IPC startup config, server transport initialization/shutdown, and network-interface enumeration.

Risks: disabled stubs make RDMA absence look like a successful no-op, so startup tests must distinguish "feature unavailable" from "listener started." Consumers must include this header with `struct net_device` and `struct ksmbd_transport` visible or forward-declared by surrounding includes.

Test signals: compile with `CONFIG_SMB_SERVER_SMBDIRECT=y/m/n`, startup behavior when disabled, I/O size clamp tests when enabled, and interface capability output for RDMA and non-RDMA netdevices.
