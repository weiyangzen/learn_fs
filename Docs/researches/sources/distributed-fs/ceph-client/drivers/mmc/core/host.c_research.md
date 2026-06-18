# sources/distributed-fs/ceph-client/drivers/mmc/core/host.c

## Purpose
MMC host class lifecycle, OF/property parsing, retuning management, wakeup resources, debugfs integration, and capability validation.

## Important APIs, Types, And Functions
- `mmc_register_host_class()` and `mmc_unregister_host_class()` manage the class.
- Retuning APIs manage enable/pause/hold/release/timer and `mmc_retune()`.
- `mmc_of_parse()` maps firmware properties to caps, GPIOs, PM caps, DSR, delays, and pwrseq.
- `mmc_of_parse_voltage()` converts `voltage-ranges` to OCR masks.
- `mmc_alloc_host()`, `devm_mmc_alloc_host()`, `mmc_add_host()`, `mmc_remove_host()`, and `mmc_free_host()` implement lifecycle.

## Control Flow
Host drivers allocate and initialize a host, parse firmware, set ops/caps, then call `mmc_add_host()`. The core validates caps, adds the class device, registers LED/debugfs, and starts detection. Removal stops card activity, removes debugfs/class device, and unregisters LEDs. Free cancels detect work and releases pwrseq/device references.

## State And Persistence
State includes host index, class device, wakeup source, retune timer/flags, detect work, GPIO descriptors, pwrseq handle, caps, IOS defaults, and error/work structures.

## Dependencies And Integration Points
Uses driver core classes, IDA, OF/fwnode properties, GPIO slot helpers, pwrseq, SDIO IRQ work, LEDs, wakeup sources, debugfs, and public MMC APIs.

## Risks And Edge Cases
Retune holds must balance. Firmware parsing can drop capabilities when bus width is insufficient. OF aliases determine `mmcN` names. Detect work/debugfs must be removed before freeing memory.

## Test Signals
`/sys/class/mmc_host/mmcN`, debugfs nodes, LED triggers, DT parsing cases, card detect, retune on CRC/timer, HS400 transitions, and pause/unpause around RPMB.
