# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/idpf/xsk.c

## Purpose
Implements AF_XDP zero-copy support for the Intel IDPF driver. It binds XSK pools to IDPF RX, split RX buffer, XDP TX, and TX completion queues, drives XSK RX polling and TX wakeup, and translates between IDPF descriptors and libeth XDP/XSK helper APIs.

## Important APIs, Types, And Functions
Key entry points are `idpf_xsk_setup_queue`, `idpf_xsk_clear_queue`, `idpf_xskfq_init`, `idpf_xskfq_rel`, `idpf_xskrq_poll`, `idpf_xsk_xmit`, `idpf_xsk_pool_setup`, and `idpf_xsk_wakeup`. Internal setup helpers attach `struct xsk_buff_pool` to queue objects and mark queue flags with `idpf_queue_set(XSK, ...)`. TX cleanup uses `idpf_xsksq_complete`, `idpf_xsksq_clean`, `xsk_tx_completed`, and `libeth_xdp_complete_tx`. RX uses `struct idpf_xskfq_refill_set` to batch buffer-queue refill accounting.

## Control Flow
Queue setup is conditional on `idpf_xdp_enabled(vport)` and on a usable XSK pool for the queue id. TX queues are initialized with a libeth XDP SQ timer and a `NOIRQ` flag when need-wakeup is active. RX polling loops over descriptors while generation bits match, extracts buffer queue and buffer ids, processes XSK buffers through the XDP program, finalizes any redirected TX work, advances queue indices, and then refills touched buffer queues. Pool setup validates frame-size alignment, optionally disables the queue pair, calls `libeth_xsk_setup_pool`, and restarts the pair.

## State And Persistence
Persistent runtime state is in queue fields: `pool`, `next_to_clean`, `next_to_use`, `pending`, `thresh`, `xsk`, buffer DMA descriptors, and queue flag bits such as `XSK`, `XDP`, `NOIRQ`, `GEN_CHK`, and `HSPLIT_EN`. There is no disk persistence. Hardware-visible state changes happen through descriptor rings and tail writes, plus queue-pair disable/enable during pool reconfiguration.

## Dependencies And Integration
Depends on Linux AF_XDP APIs, `net/libeth/xsk.h`, IDPF XDP helpers, Virtchnl2 queue types, NAPI wakeup via `libeth_xsk_init_wakeup`, and IDPF queue-pair switching. It integrates with netdev BPF `XSK_POOL_SETUP` and ndo XSK wakeup paths through functions declared in `xsk.h`.

## Risks
Queue-id mapping is sensitive for split buffer queues and XDP TX queue offsets. Incorrect `pending` accounting can starve refills or overrun rings. Need-wakeup handling must set/clear wake flags only when failures or no progress require userspace notification. Pool reconfiguration errors must leave queue-pair and pool state consistent.

## Test Signals
Useful signals include AF_XDP zero-copy bind/unbind on aligned and misaligned frame sizes, traffic through XDP_PASS/TX/REDIRECT/drop paths, need-wakeup sockets, queue restart failure injection, RX descriptor wrap/generation-bit transitions, and TX completion accounting matching userspace completions.
