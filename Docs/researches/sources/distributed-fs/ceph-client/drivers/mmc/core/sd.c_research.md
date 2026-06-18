# sources/distributed-fs/ceph-client/drivers/mmc/core/sd.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sd.c

### Purpose
`sd.c` is the core SD memory-card attach, identification, capability decoding, speed negotiation, cache/power-extension, detection, suspend/resume, and bus-operation implementation for the MMC subsystem. It translates raw SD registers and SD application commands into `struct mmc_card` state, then registers the card with the MMC bus.

### Important APIs, Types, And Functions
The public/internal entry points are `mmc_attach_sd()`, `mmc_sd_get_cid()`, `mmc_sd_get_csd()`, `mmc_sd_setup_card()`, `mmc_sd_get_ro()`, `mmc_sd_get_max_clock()`, `mmc_sd_switch_hs()`, `mmc_decode_cid()`, `mmc_decode_scr()`, and exported `sd_type`. `mmc_sd_ops` implements the bus callbacks for remove, detect, runtime/system PM, alive, shutdown, hardware reset, cache status, and cache flush. Decoders and setup helpers populate `card->cid`, `card->csd`, `card->scr`, `card->ssr`, `card->sw_caps`, `card->ext_power`, `card->ext_perf`, `card->erase_size`, and read-only flags. UHS-I helpers include `mmc_sd_init_uhs_card()`, `sd_update_bus_speed_mode()`, `sd_select_driver_type()`, `sd_set_current_limit()`, `sd_set_bus_speed_mode()`, and `mmc_sd_use_tuning()`.

### Control Flow
Attach probes OCR with ACMD41, attaches `mmc_sd_ops`, narrows host voltage, and calls `mmc_sd_init_card()`. Initialization gets CID, allocates or reuses a card, invokes host quirks, assigns RCA, reads CSD/CID, selects the card, applies SD fixups, reads SCR/SSR/switch status, enables SPI CRC when needed, checks write-protect, then selects UHS-I or legacy high-speed timing. UHS-I setup switches to 4-bit mode, selects driver strength/current limit/bus speed, sets host timing/clock, and runs tuning for SDR50/SDR104 and optionally DDR50. Legacy setup switches high speed, sets clock, performs optional host tuning hooks, and enables 4-bit mode. New cards then read extension registers, enable cache when supported, optionally enable CQE/host software queue, and reject unresolved 3.3V operation when `MMC_CAP2_AVOID_3_3V` is set.

### State, Persistence, And Dependencies
Persistent kernel state is held on `host->card` and the card substructures decoded from raw SD registers. User-visible state appears through `sd_std_groups` sysfs attributes for raw CID/CSD/SCR/SSR, identity fields, OCR/RCA, erase sizes, DSR, and combo-card CIS metadata. Extension register writes persist on the card for cache enable, cache flush, and power-off notification until power/reset semantics clear them. Dependencies include `core.h`, `card.h`, `host.h`, `bus.h`, `mmc_ops.h`, `sd_ops.h`, SD/MMC public headers, PM runtime, sysfs, scatterlist, quirks, and host callbacks such as voltage switch, tuning, CQE, and `get_ro`.

### Integration Points
`sd.c` is reached from the MMC rescan path through `mmc_attach_sd()`. It uses command helpers from `sd_ops.c` and generic MMC operations, installs `mmc_sd_ops` into the bus layer, publishes `sd_type` for `mmc_alloc_card()`, and cooperates with block/card layers through erase/cache/CQE fields. PM callbacks coordinate with runtime PM and card power state, while cache callbacks integrate with block-layer flush handling.

### Risks
The initialization sequence is highly order-sensitive: changing when SCR/SSR/switch data is read can break UHS mode negotiation, erase geometry, or combo-card sysfs. Voltage-switch retry handling must preserve card identity and avoid leaving a card in 1.8V while the host believes it is at 3.3V. Cache and power-off-notify use CMD48/CMD49 extension registers plus busy polling; failures can lose data or hang suspend if not surfaced. The file as read contains a duplicated `__be32 *raw_ssr;` declaration in `mmc_read_ssr()` and a duplicated `mmc_sd_setup_card()` call in `mmc_sd_init_card()`, both strong build/review signals. Lifetime around `mmc_sd_remove()` keeps a temporary device reference while powering off after removal.

### Test Signals
Build this file with representative SD configs to catch duplicate declarations and signature drift. Runtime signals include SD, SDHC, SDXC, SDUC, SPI SD, UHS-I SDR12/25/50/104 and DDR50 attach, voltage-switch retry and fallback, read-only GPIO/switch behavior, sysfs attribute correctness, cache enable/flush, CQE enablement, card removal detection, runtime/system suspend/resume, hardware reset, and power-off-notify timeout paths.
