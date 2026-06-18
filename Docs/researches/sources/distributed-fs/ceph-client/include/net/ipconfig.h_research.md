# sources/distributed-fs/ceph-client/include/net/ipconfig.h

Purpose: Exposes early boot automatic IP configuration state for kernel components that need boot-time network identity and root-server information.

Important APIs/types/functions: External initdata-style variables include `ic_proto_enabled`, `ic_set_manually`, `ic_myaddr`, `ic_gateway`, `ic_servaddr`, `root_server_addr`, and `root_server_path`. Protocol bits include `IC_PROTO`, `IC_BOOTP`, `IC_RARP`, and `IC_USE_DHCP`.

Control flow: Boot-time IP configuration code sets the global variables based on kernel command line, BOOTP/DHCP, or RARP. Consumers can inspect whether protocols were enabled and whether addresses were manually supplied.

State and persistence: State is global early-boot configuration, not a per-net runtime table. Comments mark it as initdata-like, so lifetime is tied to early initialization decisions and boot root setup.

Dependencies/integration: Depends only on Linux fixed-width/network-endian types. Integrates with NFS-root boot paths and low-level IP autoconfiguration.

Risks: The header exposes globals without locking because intended use is early boot; late consumers must not assume these remain mutable runtime netns state. DHCP is represented as a bit layered on BOOTP protocol selection. Test signals include command-line IP configuration, BOOTP/DHCP/RARP selection, NFS-root server/path propagation, and manual-address precedence.
