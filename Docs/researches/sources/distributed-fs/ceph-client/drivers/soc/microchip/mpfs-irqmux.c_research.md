# sources/distributed-fs/ceph-client/drivers/soc/microchip/mpfs-irqmux.c

## Purpose
Programs the PolarFire SoC GPIO interrupt mux register from device-tree `interrupt-map` data, selecting direct versus non-direct routing between GPIO controllers and the PLIC.

## Important APIs, Types, And Functions
Important functions are `mpfs_irqmux_is_direct_mode()` and `mpfs_irqmux_probe()`. It uses `of_imap_parser`, `of_imap_item`, bitmap duplicate detection, parent syscon regmap lookup with `device_node_to_regmap()`, and `regmap_read()/regmap_write()`.

## Control Flow
Probe validates `#interrupt-cells = <1>` and `#address-cells = <0>`, initializes an interrupt-map parser, and iterates every map item. It validates parent interrupt ranges, child controller indexes, duplicate child lines, and duplicate direct parent lines. It builds a 32-bit mux value: direct-mode entries leave bits cleared, non-direct GPIO0 entries set bits 0-13, and non-direct GPIO1 entries set bits 14-31. GPIO2 entries are skipped because their counterpart entries determine the shared bit. Finally it writes `MPFS_IRQMUX_CR` and logs if firmware state was overwritten.

## State And Persistence
Runtime state is transient except the hardware mux register at offset `0x54`. Bitmaps track duplicate validation only during probe.

## Dependencies And Integration Points
Depends on parent syscon regmap, OF interrupt-map bindings, platform bus, and the PolarFire GPIO/PLIC interrupt topology. Kconfig selects regmap support.

## Risks
Strict binding validation returns `-EINVAL` on malformed maps, so DT errors disable mux setup. Firmware mux settings are overwritten when DT differs. The logic encodes PolarFire-specific assumptions about 70 GPIO interrupts, 41 PLIC lines, 38 direct lines, and the special GPIO1 lines 18-23.

## Test Signals
Boot logs should show no duplicate or invalid interrupt-map errors. A one-time info message indicates the driver corrected a firmware mux value. GPIO interrupts from all three controllers should route according to the DT map.
