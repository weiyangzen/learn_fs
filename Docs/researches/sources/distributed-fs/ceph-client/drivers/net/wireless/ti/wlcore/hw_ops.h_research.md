# sources/distributed-fs/ceph-client/drivers/net/wireless/ti/wlcore/hw_ops.h

## Purpose
`hw_ops.h` is the common inline dispatch layer from wlcore core code to chip-specific operations stored in `wl->ops`. It hides wl12xx/wl18xx differences for TX/RX descriptors, firmware status, rate masks, keys, debugfs, address conversion, priority decisions, smart config, DFS/CAC, and AP sleep.

## Important APIs and wrappers
Mandatory wrappers call `BUG_ON(1)` when missing: TX block calculation, TX descriptor block/data length setup, RX buffer alignment, RX packet length, firmware status conversion, STA AP rate mask, TX checksum setup, spare block calculation, key setup, firmware address conversion, and link priority decisions.

Optional wrappers return success/defaults or `-EINVAL`: read preparation, delayed/immediate TX completion, vif init, firmware identify, RX checksum setup, AP MIMO/wide rate mask, chip debugfs init, static data handling, pre-packet-send adjustment, STA rate-control update, interrupt notify, RX BA filter, AP sleep, peer capability setup, smart config, CAC, and DFS master restart.

## Control flow and integration
Core files call these wrappers instead of branching on chip type. The wrappers either delegate to `wl->ops` or provide a conservative default. This keeps common code in `cmd.c`, `event.c`, `debugfs.c`, `init.c`, TX, and RX independent of hardware family details.

## State and persistence behavior
The header mutates no state directly, but delegated operations can update descriptors, firmware status structures, per-vif chip-private data, keys, debugfs trees, and DFS/smart-config firmware state.

## Dependencies and risks
It depends on `wlcore.h`, `rx.h`, and the completeness of each chip family's operations table. The main risk is a missing mandatory callback causing a kernel BUG instead of a recoverable failure. Optional default returns can also hide unsupported hardware features if callers assume the operation took effect.

## Test signals
Build coverage across wl12xx and wl18xx, probe-time operations table validation, TX/RX descriptor correctness, key installation, firmware status decoding, debugfs chip extensions, AP rate masks, DFS/CAC calls, and smart-config unsupported-path errors exercise this layer.
