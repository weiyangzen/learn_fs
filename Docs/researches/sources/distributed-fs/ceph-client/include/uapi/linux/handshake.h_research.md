<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/handshake.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/handshake.h

## Purpose
`handshake.h` is an auto-generated YNL generic-netlink UAPI for the kernel handshake service. It lets kernel consumers delegate transport handshakes, currently TLS via `tlshd`, to userspace.

## Important APIs, types, and functions
The family is `HANDSHAKE_FAMILY_NAME` with version `HANDSHAKE_FAMILY_VERSION`. Enums define handler classes (`HANDSHAKE_HANDLER_CLASS_TLSHD`), message types (`CLIENTHELLO`, `SERVERHELLO`), auth modes (`UNAUTH`, `PSK`, `X509`), X.509 certificate/private-key attributes, accept attributes such as socket fd, handler class, message type, timeout, auth mode, peer identity, certificate, peer name, and keyring, done attributes such as status, socket fd, and remote auth, commands `HANDSHAKE_CMD_READY`, `HANDSHAKE_CMD_ACCEPT`, `HANDSHAKE_CMD_DONE`, and multicast groups `none` and `tlshd`.

## Control flow
Userspace announces readiness, receives or issues accept work for a socket and requested handler class, performs the negotiated handshake outside the kernel, then reports completion status and remote authentication details with `DONE`.

## State and persistence behavior
Handshake work is transient per socket. Certificate, keyring, timeout, peer identity, and remote-auth results are carried in netlink messages; durable TLS or transport state is associated with the socket by kernel and daemon code.

## Dependencies and integration points
The file is generated from `Documentation/netlink/specs/handshake.yaml` and integrates with YNL tooling, generic netlink, `tlshd`, kernel TLS/RPC consumers, sockets, keyrings, and X.509 credential handling.

## Risks and test signals
Risks include generated header/spec drift, fd lifetime mistakes, missing timeout handling, wrong auth-mode interpretation, certificate/keyring lookup failures, and daemon/kernel version mismatch. Test signals include YNL schema validation, `tlshd` accept/done round trips, timeout and daemon-crash recovery, X.509/PSK cases, and multicast readiness tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/handshake.h -->
