# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/crypto/ipsec.c

## Purpose
This file implements NFP IPsec/XFRM crypto offload support. It translates Linux `xfrm_state` objects into firmware SA configuration messages, registers `xfrmdev_ops`, tracks offloaded SAs in an xarray, and attaches offload metadata to TX/RX packets.

## Important APIs, types, and functions
- Firmware command/reply enums describe add/invalidate SA requests and response codes.
- `struct nfp_ipsec_cfg_add_sa` and `struct nfp_ipsec_cfg_mssg` are the 64-word mailbox ABI used for SA configuration.
- `nfp_net_ipsec_cfg()` writes the full message to the simple mailbox, runs `NFP_NET_CFG_MBOX_CMD_IPSEC`, reads the reply back, and maps firmware response codes to Linux errors.
- `nfp_net_xfrm_add_state()` validates XFRM mode/protocol/offload type/algorithms, fills keys, salt, SPI, address family, direction, PMTU, and SA index, sends the add command, and stores `xso.offload_handle = saidx + 1`.
- `nfp_net_xfrm_del_state()` invalidates an SA and erases its xarray entry.
- `nfp_net_ipsec_tx_prep()` exports sequence and handle metadata for TX; `nfp_net_ipsec_rx()` maps firmware SA index metadata back to an `xfrm_state` in the skb secpath.

## Control flow
Initialization checks `NFP_NET_CFG_CTRL_IPSEC`, initializes `nn->xa_ipsec`, and assigns `netdev->xfrmdev_ops`. XFRM add allocates a bounded SA index, then schedules a mailbox async-message work item with `nfp_net_sched_mbox_amsg_work()`. On command failure it erases the index. Delete sends invalidate and erases regardless after warning on firmware failure. RX subtracts one from firmware SA index, validates range, creates/extends `sec_path`, looks up and holds the xfrm state, and marks `xfrm_offload` as crypto done/success.

## State and persistence
The xarray `nn->xa_ipsec` is the live SA table mapping hardware SA indices to kernel `xfrm_state` pointers. The kernel-visible offload handle is one-based because zero is invalid to XFRM. There is no persistent state across driver reload. Cleanup warns if the xarray is not empty, then destroys it.

## Dependencies and integration points
The file integrates with Linux XFRM (`xfrmdev_ops`, `secpath_set`, `xfrm_offload`), the NFP mailbox scheduler, PCI device IDs for feature differences, and NFP RX metadata (`meta->ipsec_saidx`). It uses unaligned big-endian key loads and Netlink extack messages for user-visible offload rejection reasons.

## Risks
Algorithm support is hardware-specific and easy to regress: NFP3800 disallows MD5/3DES but allows CHACHA20-POLY1305, while other devices reject CHACHA20. Key length and ICV checks must match XFRM conventions where AEAD key length includes salt. Bitfield layout in the firmware message is ABI-sensitive. RX depends on firmware providing a valid one-based SA index; stale or missing xarray entries lead to packet failure.

## Test signals
Exercise XFRM add/delete for tunnel and transport ESP/AH, AES-CBC, AES-GCM/GMAC, null auth/encryption, CHACHA20-POLY1305 on NFP3800, unsupported ESN, bad key lengths, and RX packets with valid/invalid SA indices. Cleanup should not warn after all states are deleted.
