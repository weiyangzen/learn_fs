# sources/distributed-fs/ceph-client/include/linux/sunrpc/svcauth_gss.h

Purpose: declares server-side RPCSEC_GSS lifecycle and pseudoflavor registration helpers.

Important APIs and types: APIs include global `gss_svc_init()`/`gss_svc_shutdown()`, per-net `gss_svc_init_net()`/`gss_svc_shutdown_net()`, `svcauth_gss_register_pseudoflavor()`, and `svcauth_gss_flavor()`.

Control flow: SUNRPC server initialization registers GSS service support, per-net setup prepares namespace-local state, mechanisms register pseudoflavors as auth domains, and request authentication can recover the pseudoflavor from a domain.

State and persistence: GSS service and per-net state are runtime only; auth domains may be cached and refreshed by user-space GSS helpers.

Dependencies and integration points: depends on scheduler types, SUNRPC XDR, server auth, service sockets, and RPCSEC_GSS definitions. It bridges svcauth and GSS mechanism registration.

Risks and test signals: risks include per-net cleanup ordering, duplicate pseudoflavor registration, missing user-space helper state, and flavor/domain mismatch. Test with NFSd Kerberos exports, namespace creation/destruction, module init/shutdown, and GSS context expiry.
