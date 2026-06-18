# sources/distributed-fs/ceph-client/drivers/net/ethernet/netronome/nfp/nfp_net_debugfs.c

## Purpose

`nfp_net_debugfs.c` creates the NFP netdev debugfs hierarchy and exposes live RX, TX, and XDP ring descriptor state for each vNIC. It is a diagnostic-only interface used to inspect host pointers, queue-controller pointers, descriptor contents, DMA addresses, fragments, and optional TX write-back state.

## Important APIs, Types, and Functions

Public helpers are `nfp_net_debugfs_vnic_add()`, `nfp_net_debugfs_device_add()`, `nfp_net_debugfs_dir_clean()`, `nfp_net_debugfs_create()`, and `nfp_net_debugfs_destroy()`. Show handlers are `nfp_rx_q_show()`, `nfp_tx_q_show()`, `nfp_xdp_q_show()`, and shared `__nfp_tx_q_show()`. `DEFINE_SHOW_ATTRIBUTE()` binds the handlers to debugfs file operations. The module-global `nfp_dir` is the root `nfp_net` dentry.

## Control Flow

Module/device setup creates `nfp_net/<pci-name>/vnicN/queue/{rx,tx,xdp}/` files. RX reads take `rtnl_lock()`, verify that the vector/ring exists and that the vNIC is running, read queue-controller freelist pointers, print ring metadata, then iterate descriptors and mark host/freelist pointer positions. TX/XDP reads similarly choose the normal or XDP ring, read device read/write pointers, print optional write-back, then delegate descriptor formatting to the active datapath ops via `nfp_net_debugfs_print_tx_descs()`.

## State and Persistence Behavior

The file owns debugfs dentries stored in `nn->debugfs_dir` and the global root pointer. It does not mutate datapath state except for transient register reads. It serializes inspection with RTNL to avoid racing netdev/ring teardown and checks `nfp_net_running()` before dereferencing active ring content.

## Dependencies and Integration Points

It depends on Linux debugfs, seq_file, RTNL, queue-controller pointer helpers, `struct nfp_net_r_vector`, `struct nfp_net_rx_ring`, `struct nfp_net_tx_ring`, AF_XDP ring storage, and datapath-specific descriptor printers from `struct nfp_dp_ops`.

## Risks and Edge Cases

Debugfs readers inspect live DMA rings, so pointer validity and RTNL coverage are important. XSK and normal RX rings use different software buffer arrays. Ring modulo annotations assume descriptor counts are nonzero and stable while running. Debugfs creation ignores failures, consistent with debugfs conventions, so diagnostics may be absent without affecting probe.

## Test Signals

Validation should mount debugfs, probe PF and VF vNICs, read RX/TX/XDP queue files while interfaces are down, up, under traffic, and after AF_XDP pool setup. Teardown tests should repeatedly add/remove devices while reading debugfs to catch stale pointers.
