# sources/distributed-fs/ceph-client/drivers/net/vmxnet3/vmxnet3_xdp.h

## Purpose
`vmxnet3_xdp.h` is the internal XDP interface for vmxnet3. It defines RX buffer layout limits for page_pool-backed XDP buffers and declares the XDP setup, transmit, RX processing, and page_pool allocation helpers used by the main driver.

## Important APIs, Types, And Functions
The header defines `VMXNET3_XDP_HEADROOM`, `VMXNET3_XDP_RX_TAILROOM`, `VMXNET3_XDP_RX_OFFSET`, `VMXNET3_XDP_MAX_FRSIZE`, and `VMXNET3_XDP_MAX_MTU`; declares `vmxnet3_xdp()`, `vmxnet3_xdp_xmit()`, `vmxnet3_process_xdp()`, `vmxnet3_process_xdp_small()`, and `vmxnet3_pp_get_buff()`; and provides `vmxnet3_xdp_enabled()`.

## Control Flow
No standalone flow. The constants gate XDP MTU validation and page_pool offset setup. The inline enabled check gates RX allocation mode, LRO feature validation, and RX completion paths.

## State And Persistence
No state is stored here, but it defines how `adapter->xdp_bpf_prog` is observed and how XDP receive pages are laid out. The maximum MTU/frame-size formulas are persistent driver constraints for XDP mode.

## Dependencies And Integration Points
Includes Linux filter, BPF trace, netlink, and `vmxnet3_int.h`. Used by `vmxnet3_drv.c`, `vmxnet3_ethtool.c`, and `vmxnet3_xdp.c`.

## Risks
Incorrect headroom/tailroom formulas can cause XDP data overruns or invalid SKB construction. Callers using `vmxnet3_xdp_enabled()` must still use proper RCU dereference when they need the program pointer itself.

## Test Signals
Compile XDP configurations, attach/detach programs, test MTUs at and above `VMXNET3_XDP_MAX_MTU`, verify PASS SKB data/headroom, and run ethtool feature toggles affected by XDP state.
