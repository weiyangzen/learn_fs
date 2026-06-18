# sources/distributed-fs/ceph-client/drivers/mmc/core/sdio.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/core/sdio.c

### Purpose
`sdio.c` implements SDIO card attach, common register decoding, SDIO function discovery, SDIO/combo-card speed and bus-width negotiation, runtime/system PM, reset, and detection. It turns a responding SDIO card into one MMC card device plus one driver-model child per function.

### Important APIs, Types, And Functions
The entry point is `mmc_attach_sdio()`. Important helpers are `sdio_read_fbr()`, `sdio_init_func()`, `sdio_read_cccr()`, `sdio_enable_wide()`, `sdio_disable_cd()`, `sdio_disable_wide()`, `sdio_enable_4bit_bus()`, `sdio_enable_hs()`, `mmc_sdio_get_max_clock()`, `sdio_select_driver_type()`, `sdio_set_bus_speed_mode()`, `mmc_sdio_init_uhs_card()`, `mmc_sdio_pre_init()`, `mmc_sdio_init_card()`, `mmc_sdio_reinit_card()`, and the `mmc_sdio_ops` bus callbacks. `sdio_type` defines card-level sysfs attributes for SDIO-only devices.

### Control Flow
Attach probes CMD5 OCR, installs SDIO bus ops, selects voltage, initializes the card, enables runtime PM when supported, initializes each function from OCR function count, registers the card, then registers each SDIO function. Initialization optionally requests 1.8V, distinguishes SDIO-only from SD combo by memory-present and CID behavior, applies host and SDIO fixups, assigns RCA, reads combo CSD/CID when needed, selects the card, reads CCCR/CIS, swaps an old card back in on resume if vendor/device match, sets up combo memory via `mmc_sd_setup_card()`, disables CD pull-up if requested, and chooses UHS-I or legacy high-speed/4-bit operation.

### State, Persistence, And Dependencies
State lands in `host->card`, `card->cccr`, `card->cis`, `card->sdio_func[]`, `card->sdio_funcs`, `card->sw_caps`, `card->scr`, `card->type`, `host->pm_flags`, and runtime PM state on the card and functions. Sysfs exposes vendor/device/revision/info/OCR/RCA at the card level. Dependencies include SDIO ops, CIS parsing, SD memory helpers for combo cards, quirks, bus registration, PM runtime, and host capabilities for voltage, 4-bit, high speed, UHS, power-off-card, IRQ wake, and retuning.

### Integration Points
`mmc_attach_sdio()` is called from the MMC rescan path. It creates function devices via `sdio_alloc_func()` and `sdio_add_func()` from `sdio_bus.c`, reads tuple data through `sdio_cis.c`, and uses `sdio_irq.c` indirectly for IRQ restart after resume. Function drivers bind through the SDIO bus and use exported APIs from `sdio_io.c` and `sdio_irq.c`.

### Risks
Probe ordering is sensitive because function devices are initialized before they are registered, while runtime PM is held until after registration. Resume identity matching for SDIO-only devices relies on CIS vendor/device rather than CID. Voltage-switch fallback must reset/reprobe cleanly or UHS-capable cards can be left inaccessible. PM paths remove removable cards that lack function PM callbacks but keep non-removable cards despite missing ops. Multi-function hardware reset is asynchronous through rescan so all drivers see removal, while single-function reset is immediate. Keeping power with wake SDIO IRQ forces 1-bit mode and later retune-safe 4-bit restoration.

### Test Signals
Cover SDIO-only, SD combo, nonstandard SDIO quirks, multi-function cards, function registration failure cleanup, runtime PM power-off-card, missing suspend/resume callbacks, keep-power wake IRQ, UHS-I SDR/DDR, 1.8V fallback, software reset, hardware reset with one versus multiple probed functions, and card removal during function probe.
