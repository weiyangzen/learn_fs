# sources/distributed-fs/lustre-release/include/uapi/linux/lnet/lnet-dlc.h

Purpose: Dynamic LNet Configuration UAPI for ioctl and generic netlink management of networks, NIs, routes, peers, buffers, health, UDSP, and fault controls.

Important APIs/types: defines generic netlink name/version and `enum lnet_commands` for configure, nets, peers, routes, conns, ping, CPT-of-NID, peer distance, UDSP, peer fail, debug recovery, fault, routing, buffers, and NUMA. Structures cover common and LND-specific tunables (`o2ib`, `sock`, `kfi`, `efa`, `gni`), NI/net config, router buffer pools, ping data, route/net/buffer config union, communication and message stats, local/peer health stats, NI config with CPT/interface/bulk, peer config and credit info, health reset, connection-per-peer reset, recovery lists, LNet stats, UDSP expression descriptors, UDSP rule/action payloads, and constructed UDSP info.

Control flow: user tools marshal these structs into ioctl or netlink requests; kernel code validates headers/version/counts, copies bulk arrays, and mutates/query LNet dynamic state.

State and persistence: structures represent runtime LNet state and configuration; persistence is external to user tooling, not in the ABI.

Dependencies/integration: includes `libcfs_ioctl.h` and `lnet-types.h`. Several comments require append-only structure evolution for backward compatibility with old `lnetctl`.

Risks and test signals: ABI layout, flexible arrays, user pointers, bitfields, fixed array limits, and append-only versioning are high-risk. Test signals are old/new lnetctl compatibility, per-LND tunable round trips, bulk length validation, UDSP marshal/unmarshal symmetry, peer/route/list pagination limits, and 32/64-bit userspace compatibility.
