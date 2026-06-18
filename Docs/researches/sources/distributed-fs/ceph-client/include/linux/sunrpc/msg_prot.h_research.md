# sources/distributed-fs/ceph-client/include/linux/sunrpc/msg_prot.h

Purpose: defines core ONC RPC protocol constants, auth flavors, reply status values, stream fragment header layout, header sizing, and rpcbind netid/universal-address limits.

Important APIs and types: `rpc_authflavor_t` is a `u32`. Auth flavors include AUTH_NULL, AUTH_UNIX, AUTH_GSS, AUTH_TLS, and GSS pseudoflavors for krb5/krb5i/krb5p and others. Enums cover call/reply types, accepted/denied replies, accept status, reject status, and auth status including RPCSEC_GSS credential/context problems. `rpc_fraghdr` and masks define record-marking for stream transports. Header size macros include `RPC_CALLHDRSIZE`, `RPC_MAX_HEADER_WITH_AUTH`, and reply equivalents. Netid constants cover UDP/TCP/RDMA/SCTP IPv4/IPv6/local.

Control flow: encode/decode code uses these constants to marshal RPC headers, interpret replies, size buffers, and format rpcbind registrations. Stream transports inspect the high fragment bit and 31-bit fragment length.

State and persistence: no state; constants define wire ABI and must remain stable.

Dependencies and integration points: depends on `linux/inet.h` for address length limits and is included by client, auth, transport, and XDR headers.

Risks and test signals: risks include wire incompatibility from numeric changes, fragment length mishandling, auth size underestimation, and rpcbind address truncation. Test with TCP/UDP/RDMA RPC, rpcbind registration, AUTH_GSS/TLS, and malformed fragment headers.
