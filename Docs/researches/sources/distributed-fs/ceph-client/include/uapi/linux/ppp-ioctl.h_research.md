<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp-ioctl.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/ppp-ioctl.h

Purpose: defines the PPP character-device and socket ioctl ABI for configuring PPP units/channels, compression, filters, multilink, L2TP stats, and link flags.

Important APIs and types: `SC_*` flags control protocol/address compression, VJ TCP compression, CCP state, IP enablement, multilink, logging/debug, sync mode, and decompression errors. `struct npioctl`, `struct ppp_option_data`, and `struct pppol2tp_ioc_stats` carry network-protocol mode, compression option data, and L2TP counters. `PPPIOC*` ioctls cover flags, async maps, MRU/MRRU, units, channels, filters, compression, idle stats, bridge/unbridge, and L2TP stats; `SIOCGPPP*` commands expose device stats/version.

Control flow: pppd and related tools open PPP devices, create/attach units and channels, set flags/maps/MRU, install filters, enable compression, connect channels, then query stats or detach. The kernel PPP layer maps ioctls to per-unit and per-channel state changes.

State and persistence: state is per PPP unit/channel and link lifetime: flags, maps, filters, compression state, network protocol mode, channel bindings, idle counters, and L2TP statistics. No durable state is defined.

Dependencies and integration points: depends on `linux/ppp_defs.h`, compiler `__user`, BPF socket filter structs, and ioctl/socket command numbers. Integrates with PPP generic, ppp_async/sync, pppoe, pptp/l2tp, pppd, and network device stats.

Risks and test signals: risks include ioctl numbering compatibility, 32/64-bit idle time variants, user pointer validation for compression options, filter privilege checks, and channel/unit lifetime races. Test pppd bring-up/teardown, compression negotiation, filter install, multilink, L2TP stats, bridge/unbridge, and compat ioctl paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/ppp-ioctl.h -->
