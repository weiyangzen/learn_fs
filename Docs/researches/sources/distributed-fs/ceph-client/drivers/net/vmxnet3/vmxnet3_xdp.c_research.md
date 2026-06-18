# sources/distributed-fs/ceph-client/drivers/net/vmxnet3/vmxnet3_xdp.c

## Purpose
`vmxnet3_xdp.c` implements vmxnet3's XDP integration: installing/removing BPF programs, choosing TX queues for XDP TX/redirect transmit, mapping `xdp_frame`s into vmxnet3 TX descriptors, running programs on RX buffers, building SKBs for `XDP_PASS`, recycling page_pool pages for drop/error paths, and supporting `ndo_xdp_xmit`.

## Important APIs, Types, And Functions
Key functions are `vmxnet3_xdp()`, `vmxnet3_xdp_set()`, `vmxnet3_xdp_xmit()`, `vmxnet3_process_xdp()`, `vmxnet3_process_xdp_small()`, `vmxnet3_run_xdp()`, `vmxnet3_xdp_xmit_frame()`, and `vmxnet3_xdp_xmit_back()`.

## Control Flow
Program setup rejects too-large MTUs, disables LRO, swaps the RCU-protected program pointer, releases the old program, and if XDP mode changed while running, quiesces, resets, recreates RX queues with XDP-compatible buffers, adjusts redirect-target features, and reactivates. `ndo_xdp_xmit` rejects quiesced/resetting devices, selects a CPU-based TX queue, locks it, maps frames, and returns the accepted count. RX processing syncs page_pool DMA for CPU, prepares an `xdp_buff`, runs BPF actions, builds SKBs for PASS, recycles pages for DROP/ABORTED/redirect failure, transmits frames for XDP_TX, and refills RX descriptors.

## State And Persistence
The BPF program lives in `adapter->xdp_bpf_prog` under RCU. XDP mode changes RX buffers to page_pool-backed `VMXNET3_RX_BUF_XDP`. TX descriptors mark XDP ownership with `VMXNET3_MAP_XDP`, optionally combined with `VMXNET3_MAP_SINGLE` for externally supplied frames. XDP counters persist in RX/TX queue stats.

## Dependencies And Integration Points
Depends on BPF/XDP core APIs, page_pool, netdev XDP features, and vmxnet3 lifecycle/ring helpers. Called from the main RX loop and netdev ops in `vmxnet3_drv.c`; constants come from `vmxnet3_xdp.h`.

## Risks
Risks include page ownership leaks after PASS/TX/REDIRECT/DROP, missing RX descriptor refill, wrong DMA sync direction, program-swap races during queue reconfiguration, LRO/MTU mismatch, and TX queue locking interactions with normal SKB transmit.

## Test Signals
Attach programs returning PASS, DROP, ABORTED, TX, and REDIRECT; test `ndo_xdp_xmit`, redirect flushes, data-ring packet copies, MTU limit rejection, LRO forced off, enable/disable while up, TX ring full errors, and XDP stats.
