# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/Makefile

## Purpose
This Makefile assembles the monolithic `nfp.o` driver object from core NFP PCI/CPP libraries, datapath implementations, app modules, representor/devlink/netdev code, and optional feature object sets.

## Important entries
`obj-$(CONFIG_NFP) += nfp.o` emits the module or built-in object. `nfp-objs` includes `nfpcore` support, control channel, devlink params, NFD3/NFDK datapaths, app framework, netdev common/control/debugdump/ethtool/main, representors, SR-IOV, XSK, port/shared-buffer, and NIC app code. Conditional blocks add `crypto/tls.o` for `CONFIG_TLS_DEVICE=y`, flower app objects for `CONFIG_NFP_APP_FLOWER=y`, BPF offload objects for `CONFIG_BPF_SYSCALL=y`, ABM objects for `CONFIG_NFP_APP_ABM_NIC=y`, IPsec objects via `nfp-$(CONFIG_NFP_NET_IPSEC)`, debugfs via `nfp-$(CONFIG_NFP_DEBUG)`, and DCB support via `nfp-$(CONFIG_DCB)`.

## Control flow
kbuild expands `nfp-objs` and conditionals based on configuration, then links all selected objects into `nfp.o`. The conditional object layout mirrors runtime app registration: optional flower, BPF, ABM, TLS, IPsec, debug, and DCB features are compiled only when their symbols permit.

## State and persistence
The Makefile has build-time state only. It determines which translation units participate in the final driver and therefore which app types, offloads, and debug paths can exist at runtime.

## Dependencies and integration points
It integrates the NFP core, datapath variants, netdev management, app framework, flower/BPF/ABM/nic apps, crypto offloads, XSK support, debugfs, and DCB modules with kbuild and Kconfig.

## Risks and edge cases
The TLS block checks `CONFIG_TLS_DEVICE` directly rather than `CONFIG_NFP` because the whole file is already gated by `CONFIG_NFP`. Feature object lists must stay synchronized with Kconfig dependencies and source file renames. Objects that define app type symbols must be included whenever runtime firmware/app selection may reference them. Optional paths can bit-rot without config matrix builds.

## Test signals
Test with config matrices enabling/disabling flower, BPF syscall, ABM, IPsec, debug, TLS device, and DCB. Link tests should catch missing objects or unresolved references. Runtime smoke tests should verify expected app registration and absence of feature hooks when their objects are omitted.
