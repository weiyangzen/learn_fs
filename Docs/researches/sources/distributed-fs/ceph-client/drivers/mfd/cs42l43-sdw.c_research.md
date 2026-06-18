# sources/distributed-fs/ceph-client/drivers/mfd/cs42l43-sdw.c

## Purpose
This is the SoundWire bus front-end for CS42L43/CS42L43B. It describes SoundWire ports, configures a little-endian SoundWire regmap, tracks attach/detach status, clears SoundWire-specific interrupt state, constrains PLL-related bus clock changes, and delegates device initialization to the common MFD core.

## Important APIs, types, and functions
`cs42l43_sdw_regmap` mirrors the I2C regmap constraints and cache callbacks but uses little-endian register/value formatting for SoundWire. `CS42L43_SDW_PORT()` defines source/sink `sdw_dpn_prop` entries. `cs42l43_read_prop()` sets wake, paging, domain IRQ, parity quirk, SCP interrupt masks, and source/sink port bitmaps/properties. `cs42l43_sdw_update_status()` updates `cs42l43->attached` and completes either `device_attach` or `device_detach`. `cs42l43_sdw_interrupt()` clears Cirrus GEN interrupt status outside the generic regmap IRQ handling. `cs42l43_sdw_bus_config()` records `sdw_freq` as half the current data rate and rejects frequency changes while `sdw_pll_active` is true. `cs42l43_sdw_probe()` allocates state, stores `sdw`, variant ID from the SDW ID table, initializes regmap, and calls `cs42l43_dev_probe()`.

## Control flow
SoundWire framework first calls property and probe paths, then reports attachment via `update_status()`. The core starts with regcache cache-only and its boot work calls `cs42l43_wait_for_attach()`, which blocks until this wrapper completes `device_attach`. During soft resets, the core waits for `device_detach`, again completed by this file. SoundWire interrupts are first represented through regmap IRQs and then have the SoundWire GEN status cleaned in the callback.

## State and persistence behavior
This file maintains attachment state, detach/attach completion signaling, and SoundWire bus frequency state in `struct cs42l43`. It does not persist register settings itself, but its attach/detach events determine when the core may leave cache-only mode and synchronize register cache. PLL lock state is protected by `pll_lock` shared with child/core users.

## Dependencies and integration points
It depends on the Linux SoundWire slave framework, SoundWire register definitions, regmap SoundWire transport, PM, and the CS42L43 core. It exposes source ports 1-4 and sink ports 5-7, sets `use_domain_irq`, and uses SDW slave IDs for CS42L43 and CS42L43B.

## Risks and edge cases
Attach timeouts in the core depend on this file receiving status callbacks. The SoundWire interrupt cleanup ignores return values from no-PM reads/writes, so bus errors may be hidden after IRQ handling. `bus_config()` rejects frequency changes only while `sdw_pll_active` is true; users must correctly set that flag. Endian differs from I2C, so regressions in regmap format are bus-specific.

## Test signals
Useful tests include SoundWire property enumeration, source/sink port masks, attach and detach completion timing, soft-reset detach wait behavior, interrupt clearing, bus clock change rejection while PLL is active, and runtime suspend/resume through regcache cache-only transitions.
