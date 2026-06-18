# sources/distributed-fs/ceph-client/drivers/net/ethernet/hisilicon/hns/hns_dsaf_rcb.c

## Purpose

`hns_dsaf_rcb.c` implements the HNS RCB ring-control block used by the netdev data path. It maps DSAF modes to queue/ring topology, allocates and initializes per-ring hardware descriptors, configures interrupt coalescing, resets rings, polls ring emptiness during reset, controls ring interrupts, exposes hardware/software stats, and supplies register dump support.

## Important APIs, Types, And Functions

The exported API includes ring wait/reset/control functions (`hns_rcb_wait_fbd_clean`, `hns_rcb_wait_tx_ring_clean`, `hns_rcb_reset_ring_hw`, `hns_rcb_ring_enable_hw`, interrupt clear/mask variants for v1/v2), common setup (`hns_rcb_common_get_cfg`, `hns_rcb_common_free_cfg`, `hns_rcb_common_init_hw`, `hns_rcb_common_init_commit_hw`, `hns_rcb_get_cfg`, `hns_rcb_get_queue_mode`), coalescing getters/setters, buffer-size programming, stats accessors, and register-dump helpers.

Internally it uses `struct rcb_common_cb`, `struct ring_pair_cb`, `struct hnae_queue`, and `struct hnae_ring`. It relies on RCB register offsets and bit fields from `hns_dsaf_reg.h`.

## Control Flow

Configuration starts with `hns_rcb_common_get_cfg`, which determines ring count from `dsaf_dev->dsaf_mode`, allocates a flexible-array `rcb_common_cb`, stores descriptor count, queue mode limits, virtual/physical common MMIO bases, and attaches it to `dsaf_dev->rcb_common[]`. `hns_rcb_get_cfg` iterates each ring, calculates ring MMIO base and physical base, derives the port inside the common block, obtains TX/RX IRQs from the platform device using different v1/v2 layouts, and initializes TX/RX ring software fields.

Hardware initialization in `hns_rcb_common_init_hw` clears/masks common exception interrupts, verifies the hardware init flag, writes per-port descriptor counts, default coalescing frames/timeouts, endian mode, and v1/v2 FNA/FA/TSO mode bits. `hns_rcb_common_init_commit_hw` uses write memory barriers around the system-finish register write.

At runtime, ring reset waits for TX fetched descriptors to drain, disables prefetch, toggles reset, and polls whether the ring can be reset. Interrupt helpers write per-ring mask/status registers. Coalescing setters validate ranges and hardware limits before writing common registers. Stats routines combine RCB packet records, PPE queue counters, and software ring stats.

## State And Persistence

Persistent driver state lives in `rcb_common_cb` and each `ring_pair_cb`. Hardware state lives in descriptor base registers, descriptor count/length registers, ring head/tail/fbd counters, prefetch enable, interrupt masks/status, common endian and TSO bits, and coalescing registers. Software stats in `hns_ring_hw_stats` are cumulative until control-block teardown.

## Dependencies And Integration Points

RCB is initialized through PPE setup and consumed by `hns_enet.c` for TX/RX DMA rings, IRQ handling, and NAPI. It also feeds ethtool stats and register dumps through AE operations. It integrates with platform IRQ resources, DSAF mode/version helpers, and `hnae` queue/ring abstractions.

## Risks And Test Signals

Risks include invalid IRQ indexing between v1 and v2, bad DSAF mode topology resulting in incorrect port/ring mapping, coalescing values outside hardware ranges, reset loops that leave prefetch disabled or rings uncleared, and stats races with live traffic. Test signals include successful probe with expected queue count, no `wait fbd clean fail`, `head not equal to tail`, or `reset ring fail` logs, functioning TX/RX after reset, correct interrupt moderation from `ethtool -c/-C`, and coherent ring register dumps.
