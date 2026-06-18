
# `sources/distributed-fs/ceph-client/tools/testing/selftests/drivers/net/hw/xsk_reconfig.py`

## Purpose
Reproduces AF_XDP/virtio-net reconfiguration races by binding a zero-copy XDP socket without filling the fill ring, then toggling XDP program attachment and RX ring size.

## Important APIs, Types, And Functions
- `_get_rx_ring_entries()` reads current RX ring size via `ethtool -g`.
- `setup_xsk()` probes and starts `xdp_helper <ifindex> <queue> -z` in background, skipping if AF_XDP or zero-copy bind is unsupported.
- `check_xdp_bind()` attaches and detaches `xdp_dummy.bpf.o` while XSK is bound.
- `check_rx_resize()` halves and restores RX ring size while XSK is bound.

## Control Flow
`main()` creates `NetDrvEnv(__file__, nsim_test=False)` and runs the two checks. Each check enters a `with setup_xsk(cfg)` block so the helper is alive while the potentially racy reconfiguration occurs.

## State And Persistence
Mutates XDP attachment and RX ring size. The XDP program is explicitly turned off; ring size is restored to the original value in the same test body.

## Dependencies And Integration Points
Intended for a virtio-net guest interface with zero-copy AF_XDP support. Depends on `xdp_helper`, `xdp_dummy.bpf.o`, ethtool ring configuration, and XDP attach support.

## Risks
The helper is deliberately started without fill ring setup to trigger delayed refill work, so failures can be hangs or deadlocks on buggy kernels. The format string in `setup_xsk()` is split such that `{xdp_queue_id}` is literal in the second string, which may be intentional shell text only if the helper accepts it; otherwise it is a likely bug because it will not substitute the queue ID.

## Test Signals
Success is completion of XDP attach/off and RX ring resize/restore while the zero-copy XSK helper is bound. Unsupported AF_XDP or failed zero-copy bind becomes a skip.
