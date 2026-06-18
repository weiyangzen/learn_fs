# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nic/main.h

Purpose: Declares NIC app private data and, when DCB is enabled, the per-vNIC DCB state layout and init/clean hooks.

Important APIs/types/functions: Defines DCB sizes (`NFP_NET_MAX_DSCP`, `NFP_NET_MAX_TC`, `NFP_NET_MAX_PRIO`, `NFP_DCB_CFG_STRIDE`), `struct nfp_dcb`, `nfp_nic_dcb_init()`, `nfp_nic_dcb_clean()`, and `struct nfp_app_nic_private`.

Control flow/state: Header-only declarations. With `CONFIG_DCB`, each NIC private object embeds `struct nfp_dcb`; otherwise DCB init/clean are inline no-ops and the private structure is empty.

Dependencies/integration: Included by NIC main and DCB implementation. Depends on Linux netdevice/DCB constants and NFP CPP area forward declarations through included implementation context.

Risks: Empty `struct nfp_app_nic_private` under no DCB interacts with allocation logic that checks `sizeof(*app_pri)`. DCB field layout must match `dcb.c` expectations.

Test signals: Build with `CONFIG_DCB=y` and disabled, verify vNIC private allocation behavior, DCB init/clean symbol availability, and no-op behavior when DCB is off.
