
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/nk_qlease.py`

## Purpose
Tests netdev queue lease behavior with a netkit namespace and io_uring zero-copy receive (`iou-zcrx`). It validates queue lease metadata, traffic delivery through a leased RX queue, conflicts with XDP multi-buffer attachment, and lease cleanup after netkit device destruction.

## Important APIs, Types, And Functions
- `set_flow_rule(cfg)` installs an ethtool ntuple rule steering TCPv6 traffic on `cfg.port` to `cfg.src_queue`.
- `test_iou_zcrx()` configures TCP data split, RSS indirection, an ntuple rule, then runs `iou-zcrx` in the netns and a remote client.
- `test_attrs()` queries `NetdevFamily.queue_get()` and validates the `lease` object, leased queue ID/type, peer ifindex, and `netns-id`.
- `test_attach_xdp_with_mp()` verifies an active io_uring queue lease rejects XDP attachment with `xdp.frags`.
- `test_destroy()` deletes the netkit host link while `iou-zcrx` holds references, then verifies lease state disappears and direct physical queue receive still works.

## Control Flow
`main()` creates `NetDrvContEnv(__file__, rxqueues=2)`, deploys the `iou-zcrx` binary to the remote, selects the last combined channel as source queue, enters the netkit namespace, and creates a netdev queue lease from the guest RX queue to the physical RX queue. The tests run in order, with `test_destroy()` last because it removes netkit devices.

## State And Persistence
The test mutates ring settings (`tcp-data-split`, `hds-thresh`, `rx`), RSS indirection, ntuple rules, tc filters, and netkit devices. Most changes use `defer()`, while `test_destroy()` explicitly nulls `cfg._nk_host_ifname` and `cfg._nk_guest_ifname` after deleting the link so environment cleanup does not double-delete.

## Dependencies And Integration Points
Depends on `NetDrvContEnv`, `NetNSEnter`, `EthtoolFamily`, `NetdevFamily`, `iou-zcrx`, `nk_forward.bpf.o`, `xdp_dummy.bpf.o`, tc, ethtool ntuple support, netkit, and IPv6. It integrates netdev netlink queue lease API with ethtool ring/RSS state and io_uring.

## Risks
The test assumes at least two combined channels and a driver supporting TCP data split plus queue leases. Cleanup is timing-sensitive: `test_destroy()` uses a timer to terminate `iou-zcrx` while `ip link del` waits on references and later sleeps briefly for asynchronous io_uring cleanup.

## Test Signals
Pass signals include successful `iou-zcrx` transfer, expected queue lease netlink fields, `io-uring` presence while receive is active, XDP attach failure under active memory provider, and `io-uring` absence after teardown.
