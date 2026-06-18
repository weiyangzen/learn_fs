# Research: subset-b-004281

## sources/distributed-fs/ceph-client/drivers/mmc/host/via-sdmmc.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/via-sdmmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/via-sdmmc.c

## Purpose
This file implements the `via_sdmmc` PCI MMC host driver for VIA SD/MMC card reader hardware, currently matched by `PCI_VENDOR_ID_VIA` and device id `0x9530`. It exposes the controller through the Linux MMC core with command, data, card-detect, write-protect, power, clock, interrupt, and suspend/resume handling.

## Important APIs, types, and functions
- `struct via_crdr_mmc_host` is the private host state. It stores the active `mmc_request`, command, data phase, MMIO bases for SDC/DDMA/PCI-control register windows, saved PM register images, card-detect and completion work, timeout timer, spinlock, power state, reject flag, and quirks.
- Register mirror structs `struct sdhcreg` and `struct pcictrlreg` support suspend/resume and reset restore.
- `via_sdc_ops` registers `.request`, `.set_ios`, and `.get_ro` with the MMC core.
- `via_sd_probe()` enables the PCI device, requests BAR regions, maps BAR0, derives controller sub-bases, resets/powers the controller, initializes the MMC host, requests the shared IRQ, enables controller interrupts, applies the Lenovo 300 ms power-delay quirk, and calls `mmc_add_host()`.
- `via_sd_remove()` rejects new requests, disables interrupts, aborts active DMA/request state, removes the MMC host, frees IRQ/timer/work, powers off pads, unmaps MMIO, and releases PCI resources.
- `via_sd_suspend()`/`via_sd_resume()` save and restore PCI-control and SDC register state around power/reset sequencing.

## Control flow
MMC requests enter `via_sdc_request()` under `host->lock`. The driver enables the SDC DMA clock, clears pending write-one-to-clear SDC status, stores `host->mrq`, rejects requests if no card or removal is in progress, and otherwise calls `via_sdc_send_command()`. Command setup selects controller response encoding from `mmc_resp_type()`, programs argument/control registers, arms a timeout timer, and calls `via_sdc_preparedata()` when the command has data. Data setup requires a single DMA segment (`mmc->max_segs = 1` and `BUG_ON(count != 1)`), configures DDMA, and writes block length/count and interrupt enable bits.

The IRQ path `via_sdc_isr()` first validates the PCI interrupt-status bit, filters SDC status, handles card-detect interrupts by scheduling `carddet_work`, then dispatches command-status bits to `via_sdc_cmd_isr()` and data-status bits to `via_sdc_data_isr()`. Successful command completion reads response registers in `via_sdc_get_response()`. Successful or failed data completion unmaps DMA, sets `bytes_xfered`, and either sends a stop command or queues `finish_bh_work`. `via_sdc_finish_bh_work()` deletes the timer, clears active pointers, drops the spinlock, and calls `mmc_request_done()`.

## State and persistence
Runtime state is entirely in kernel memory and hardware registers. There is no on-disk persistence. The saved PM register images preserve controller state across suspend/resume. `host->power` tracks selected voltage for reset and resume. `host->reject` prevents new commands during remove. The timer is a per-request watchdog and the work items defer card detection and request completion out of IRQ context.

## Dependencies and integration points
The driver depends on PCI, MMIO accessors, DMA mapping, Linux MMC host APIs, workqueues, timers, IRQs, and PM helpers. Hardware integration is via PCI BAR0 with fixed register-window offsets. MMC integration is through `devm_mmc_alloc_host()`, `mmc_add_host()`, `mmc_detect_change()`, and `mmc_request_done()`.

## Risks and edge cases
- Data DMA only supports one scatter-gather entry; callers rely on `mmc->max_segs = 1`, but unexpected mapping results trigger `BUG_ON()`.
- DMA at 375 kHz is known broken; `via_set_ddma()` silently forces the controller to 8 MHz, which can surprise low-speed initialization paths.
- Timeout, removal, and IRQ completion share `host->cmd`/`host->data`/`host->mrq`; correctness depends on the spinlock and deferred completion ordering.
- `via_reset_pcictrl()` manipulates power/reset outside the lock after saving state, so races are mitigated by caller context but remain sensitive during card removal.
- Response packing is hardware-specific and should be regression-tested for R2 and short responses.

## Test signals
Useful validation signals include PCI probe/remove on matching hardware, card insertion/removal during idle and transfer, single- and multi-block read/write, timeout injection, write-protect reporting, suspend/resume with a card inserted, and DMA mapping behavior when requests exceed one segment. Kernel logs for "forcing card speed to 8MHz", timeout messages, and unexpected interrupts are important diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/via-sdmmc.c -->

## sources/distributed-fs/ceph-client/drivers/mmc/host/vub300.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/vub300.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/vub300.c

## Purpose
This file implements the `vub300` USB-to-SD/MMC/SDIO adapter driver. It is both a USB client driver and an MMC host driver: a card inserted into the external VUB300 device is surfaced to the Linux MMC/SDIO stack as a local host controller.

## Important APIs, types, and functions
- USB matching is through `vub300_table` for Elan and SMSC/VUB300 vendor IDs with product id `0x012c`.
- Packed protocol structs (`sd_command_header`, `sd_irqpoll_header`, `sd_status_header`, `sd_error_header`, offload/piggyback structs, and `union sd_command`/`union sd_response`) define the private USB firmware command/response ABI.
- `struct vub300_mmc_host` owns USB device/interface refs, endpoint addresses, MMC state, URBs, completions, timers, SG requests, firmware/offload caches, SDIO IRQ state, and work items.
- `vub300_mmc_ops` implements `.request`, `.set_ios`, `.get_ro`, and `.enable_sdio_irq`.
- Workqueues `cmndworkqueue`, `pollworkqueue`, and `deadworkqueue` serialize command execution, SDIO IRQ polling, and inactivity/port-status checks.
- Module parameters tune speed, packet padding, offload use, bus width, SDIO IRQ polling, firmware polling timeout, max request size, and ROM wait states.

## Control flow
`vub300_probe()` allocates URBs and an MMC host, configures capabilities and limits, discovers two bulk-in and two bulk-out endpoints, queries firmware/controller status with vendor control messages, initializes timers/work, sets interface data, and calls `mmc_add_host()`. Runtime MMC requests enter `vub300_mmc_request()`, which rejects missing interface/card/power/transport-failure states, then locks `cmd_mutex`. CMD52 reads may be satisfied immediately from offloaded register data via `satisfy_request_from_offloaded_data()`. Other requests are stored in `vub300->req/cmd/data`, `datasize` is computed, and command work is queued.

`vub300_cmndwork_thread()` serializes the command transaction. It may download SDIO offload pseudocode firmware based on card/vendor/function IDs, constructs a firmware command in `send_command()`, starts the command response URB chain, performs bulk data movement using USB SG or padded temporary buffers, waits for command response completion, translates firmware errors, builds MMC response words, clears active pointers, and calls `mmc_request_done()`.

SDIO IRQ support is polling based. `vub300_enable_sdio_irq()` updates `irq_enabled`, delivers queued IRQs, or queues poll work. `vub300_pollwork_thread()` sends an IRQ-poll command and interprets response types including normal interrupt, IRQ-enabled/disabled with offloaded register payloads, no interrupt, status updates, and device errors. Inactivity timer work periodically checks port status when idle.

## State and persistence
State is volatile kernel and device firmware state. `vub_name` doubles as a firmware file name and "already attempted/downloaded" marker. Dynamic SDIO offload state is stored in `sdio_register[]` and per-function cyclic FIFOs `fn[8]`. `card_present`, `read_only`, `card_powered`, `irq_enabled`, `irq_disabled`, `irqs_queued`, `usb_transport_fail`, and `usb_timed_out` gate future operations. Krefs protect the host across queued work and disconnect.

## Dependencies and integration points
The driver integrates with USB core, MMC/SDIO core, firmware loading (`request_firmware()`), workqueues, timers, completions, krefs, mutexes, and scatter-gather helpers. Its external firmware names are generated as `vub_<card vendor/device>_<func vendor/device>...bin`, falling back to `vub_default.bin`.

## Risks and edge cases
- Disconnect does not explicitly kill every queued work item before dropping interface visibility; correctness relies on interface NULL checks and krefs.
- The offload cache can return stale CMD52 values if firmware/register invalidation is wrong; writes to dynamic registers clear prepared state, but cyclic FIFO matching is protocol-dependent.
- USB timeout recovery may reset the USB device from command response handling.
- Padding workarounds and packet-size branches can hide short-transfer bugs.
- Probe contains an unusual `for` loop that increments `i` both in the loop and in `vub300->sdio_register[i++].activate = 0`, leaving alternating entries initialized by that statement only.

## Test signals
Test with VUB300 hardware across SD memory and SDIO cards, card insertion/removal, power transitions, 1-bit/4-bit modes, high-speed limit parameter, padded and unpadded transfers, CMD52 offload hits/misses, SDIO IRQ delivery, USB reset/disconnect during active transfer, and missing/corrupt offload firmware. Logs around endpoint discovery, operating mode, firmware download, USB transport errors, and port status are high-value.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/vub300.c -->

## sources/distributed-fs/ceph-client/drivers/mmc/host/wbsd.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/wbsd.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/wbsd.c

## Purpose
This file implements the Winbond W83L51xD SD/MMC host driver. It supports both PnP-discovered and manually configured platform instances, exposes the chip through the MMC core, and handles legacy I/O-port, IRQ, and optional ISA DMA resources.

## Important APIs, types, and functions
- `wbsd_ops` provides MMC `.request`, `.set_ios`, and `.get_ro`.
- Low-level helpers `wbsd_unlock_config()`, `wbsd_write_config()`, `wbsd_read_config()`, `wbsd_write_index()`, and `wbsd_read_index()` access Super I/O config and indexed SD registers.
- `wbsd_init_device()` resets the SD function/FIFO, sets card-detect mode, powers down the port, configures max timeout and interrupts, and records card-present state.
- `wbsd_prepare_data()`, `wbsd_finish_data()`, `wbsd_empty_fifo()`, and `wbsd_fill_fifo()` implement data transfer through ISA DMA or programmed FIFO.
- `wbsd_irq()` accumulates interrupt status and schedules bottom-half work for card, FIFO, CRC, timeout, and transfer-complete events.
- Resource setup is split across `wbsd_scan()`, `wbsd_request_resources()`, `wbsd_chip_config()`, `wbsd_chip_validate()`, `wbsd_init()`, and `wbsd_shutdown()`.

## Control flow
Requests enter `wbsd_request()` under `spin_lock_bh()`. The driver rejects missing-card requests, validates data commands against the controller-supported command set, prepares data when present, sends the command, and either finishes immediately or leaves completion to IRQ/work handling. `wbsd_send_command()` writes opcode and argument bytes to the command register, waits until card traffic clears, then checks accumulated ISR bits for card removal, timeout, and CRC errors before reading short or long responses.

For data transfers, `wbsd_prepare_data()` programs timeout registers, block size including CRC bytes, bus width, and resets the FIFO. If DMA is available, it copies write data into a 64 KiB DMA buffer, programs the ISA DMA controller, and enables host DMA. Without DMA, it initializes scatter-gather traversal, configures FIFO thresholds, and pre-fills FIFO for writes. IRQ bottom halves drain/fill FIFO, mark CRC/timeout errors, or call `wbsd_finish_data()`. Finish logic optionally sends a stop command, waits until block read/write state clears, disables DMA, computes `bytes_xfered`, copies read DMA data back to SG, adjusts bytes on error, and completes the MMC request.

Card detection is interrupt and timer mediated. `wbsd_card_bh_work()` updates `WBSD_FCARD_PRESENT`, aborts active transfers on removal, and calls `mmc_detect_change()`. DAT3 chip-select initialization temporarily sets `WBSD_FIGNORE_DETECT`; `ignore_timer` later re-enables detection and schedules a card check.

## State and persistence
Driver state resides in `struct wbsd_host`: current request, accumulated ISR, SG cursor, DMA buffer/address, clock, bus width, config port/unlock code, chip ID, base/IRQ/DMA resources, flags, work items, and ignore timer. There is no persistent storage. Module parameters `nopnp`, `io`, `irq`, and `dma` configure non-PnP probing.

## Dependencies and integration points
The driver depends on legacy port I/O, ISA DMA APIs, PnP, platform devices, MMC core, workqueues, timers, and scatterlist helpers. It uses `devm_mmc_alloc_host()` but manually manages I/O regions, IRQ, DMA buffer, and PnP/platform registration.

## Risks and edge cases
- The source comments document broken FIFO size and threshold behavior; FIFO mode uses proactive workqueue polling to compensate.
- ISA DMA requires a 64 KiB-aligned buffer below 16 MB; failures fall back to FIFO, while unexpected alignment bugs call `BUG_ON(1)`.
- Several paths busy-wait on hardware status under lock.
- Data command support is explicitly limited; unsupported commands with data return `-EINVAL`.
- Request completion unlocks around `mmc_request_done()` and then relocks, so caller assumptions around `host->lock` must remain consistent.

## Test signals
Key tests include PnP and non-PnP probe, configured I/O/IRQ/DMA combinations, FIFO fallback, read/write single and multi-block transfers, card removal during transfer, CRC and timeout interrupt handling, write-protect reporting, suspend/resume for both platform and PnP modes, and DAT3/MMC chip-select detection blackout behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/wbsd.c -->

## sources/distributed-fs/ceph-client/drivers/mmc/host/wbsd.h
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/wbsd.h -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/wbsd.h

## Purpose
This header defines the Winbond W83L51xD SD/MMC controller register map, bit definitions, DMA sizing, and the private `struct wbsd_host` used by `wbsd.c`.

## Important APIs, types, and definitions
- Super I/O configuration constants include `LOCK_CODE`, `WBSD_CONF_*` register offsets, `DEVICE_SD`, and card-detect pin configuration values.
- Runtime I/O register offsets include `WBSD_CMDR`, `WBSD_DFR`, `WBSD_EIR`, `WBSD_ISR`, `WBSD_FSR`, `WBSD_IDXR`, `WBSD_DATAR`, and `WBSD_CSR`.
- Interrupt enable/status masks define card detect, FIFO threshold, CRC, timeout, program/busy end, and transfer-complete events.
- FIFO and CSR masks describe FIFO empty/full threshold state, memory-stick LED/write-protect/card-present bits, and power control.
- Indexed SD register offsets describe clock, block size, timeouts, setup, DMA, FIFO enable, status, response bytes, CRC status, and ISR mirror registers.
- `struct wbsd_host` is the central private state shared by the implementation.

## Control flow relevance
The header has no executable flow, but its constants directly drive every hardware access path in `wbsd.c`. Request submission uses `WBSD_CMDR`; response parsing uses `WBSD_IDX_RESP*` and `WBSD_IDX_RSPLEN`; data setup uses block-size, timeout, setup, FIFO, and DMA indices; IRQ handling uses `WBSD_ISR` masks; card-detect and write-protect checks use `WBSD_CSR` masks.

## State and persistence
`struct wbsd_host` holds all volatile driver state: MMC host pointer, spinlock, flags (`WBSD_FCARD_PRESENT`, `WBSD_FIGNORE_DETECT`), active request, accumulated ISR, current SG entry/count/offset/remain, DMA buffer and bus address, first-error flag, clock, bus width, config/unlock data, chip ID, I/O base, IRQ, DMA channel, work structs, and ignore timer. There is no persistent state.

## Dependencies and integration points
The struct embeds Linux kernel types from the implementation context: `struct mmc_host`, `spinlock_t`, `struct mmc_request`, `struct scatterlist`, `dma_addr_t`, `struct work_struct`, and `struct timer_list`. It is private to the Winbond host driver rather than a public subsystem ABI.

## Risks and edge cases
- Hardware semantics are encoded as raw numeric constants; mistakes in bit use can affect power, card detect, FIFO, or DMA behavior.
- `WBSD_DMA_SIZE` fixes the DMA bounce buffer at 64 KiB and matches request-size limits in `wbsd.c`.
- `WBSD_IDX_RESP*` ordering is critical for correct short and long response assembly.
- The header uses older C style pointer spacing but is otherwise isolated.

## Test signals
Validation is indirect through `wbsd.c`: register access correctness can be observed through successful probe/config, card-detect state changes, command responses, FIFO transfer progress, DMA completion counts, write-protect state, and interrupt classification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/wbsd.h -->

## sources/distributed-fs/ceph-client/drivers/mmc/host/wmt-sdmmc.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/wmt-sdmmc.c -->
# sources/distributed-fs/ceph-client/drivers/mmc/host/wmt-sdmmc.c

## Purpose
This file implements the WonderMedia WM8505/WM8650 SD/MMC host controller driver (`wmt-sdhc`) as an OF/platform MMC host with a separate DMA engine.

## Important APIs, types, and functions
- `struct wmt_mci_priv` stores MMIO base, regular and DMA IRQs, coherent DMA descriptor buffer, command/data completions, active request/command, clock, device pointer, and polarity flags.
- `struct wmt_mci_caps` describes controller limits supplied through OF match data.
- `wmt_mci_ops` provides MMC `.request`, `.set_ios`, `.get_ro`, and `.get_cd`.
- `wmt_mci_probe()` reads OF match/device data, maps registers, requests regular and DMA IRQs, allocates coherent descriptors, obtains/enables the SDMMC clock, resets hardware, and registers the MMC host.
- `wmt_mci_regular_isr()` and `wmt_mci_dma_isr()` jointly complete command and data phases.
- DMA helpers initialize descriptors, configure direction, enable interrupts, and start the DMA controller.

## Control flow
`wmt_mci_request()` stores the active request and command, converts MMC response type values into controller encodings, and chooses a non-data or data path. Non-data commands are programmed by `wmt_mci_send_command()` and started; completion occurs in `wmt_mci_regular_isr()`. Data requests initialize a command completion, reset/enable DMA, program block length/count, map the SG list, create one descriptor per block-sized chunk, mark the last descriptor with `DMA_RBR_END`, configure DMA direction, send the command, initialize data completion, start DMA, and then start the command.

The regular ISR handles card insertion/removal/device-insertion status first, aborting active command/DMA completions when needed. For non-data and stop commands, it handles command-done and timeout bits, reads responses, clears active command, and calls `mmc_request_done()`. For data commands, it completes `comp_cmd` on command response or timeout and, if DMA has already completed, calls `wmt_complete_data_request()`. The DMA ISR checks the DMA completion event code, marks data timeout on non-success, disables DMA, completes `comp_dma`, and finishes the request when command completion is already done. `wmt_complete_data_request()` unmaps DMA, sets bytes transferred, reads the original command response, and sends a stop command when required.

## State and persistence
The driver keeps only volatile kernel/hardware state. `priv->req`, `priv->cmd`, `priv->comp_cmd`, and `priv->comp_dma` represent the active transaction. OF booleans `sdon-inverted` and `cd-inverted` configure polarity behavior. Suspend/resume reset selected hardware bits and gate the clock; there is no saved register image beyond reset-time defaults.

## Dependencies and integration points
The driver depends on platform/OF APIs, IRQ mapping, MMIO accessors, coherent DMA allocation, DMA mapping, Linux clock framework, and MMC core. Device-tree compatible `"wm,wm8505-sdhc"` selects `wm8505_caps`.

## Risks and edge cases
- Descriptor generation assumes block-sized chunks and enough coherent descriptor space for `mmc->max_blk_count`; malformed SG/block combinations could underdescribe data if lengths are not multiples of block size.
- Request state is global per host and not explicitly locked; MMC core serialization and interrupt ordering are assumed.
- `wmt_dma_init()` returns `1` on failure, but callers do not check it.
- Error handling maps any non-success DMA event to `-ETIMEDOUT`, losing event specificity.
- `wmt_mci_remove()` resets and frees DMA before `mmc_remove_host()`, which is a teardown ordering detail worth reviewing against active requests.

## Test signals
Test OF probe with both IRQs and clock present, card-detect polarity variants, read/write single and multi-block DMA transfers, stop-command handling, response parsing, card insertion/removal IRQs, DMA error event injection, suspend/resume, and clock-rate changes through `.set_ios()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/wmt-sdmmc.c -->

## sources/distributed-fs/ceph-client/drivers/most/Kconfig
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/most/Kconfig

## Purpose
This Kconfig file defines build-time configuration entries for the MOST (Media Oriented Systems Transport) Linux driver stack and its selectable components.

## Important configuration symbols
- `MOST` is a tristate menuconfig for core MOST support. It depends on `HAS_DMA` and `CONFIGFS_FS`, defaults to `n`, and builds module `most_core` when selected as a module.
- `MOST_USB_HDM` enables the USB hardware-dependent module and depends on `USB`; it builds `most_usb`.
- `MOST_CDEV` enables the character-device component and builds `most_cdev`.
- `MOST_SND` enables the ALSA/sound component, depends on `SND`, selects `SND_PCM`, and builds `most_sound`.

## Control flow and integration behavior
Kconfig has no runtime control flow, but it controls which pieces of the MOST stack can be compiled. The core requires configfs support because `core.o` includes `configfs.o`, and components use configfs registration to expose link creation/configuration. The help text describes the expected stack composition: at least one userspace-facing component such as cdev and one hardware interface such as USB are needed for practical use.

## State and persistence
The state is kernel build configuration only. Choices persist through the kernel `.config` mechanism, not through runtime driver state.

## Dependencies and integration points
The entries connect the MOST sources to the kernel build system and subsystem dependencies: DMA availability, configfs, USB, ALSA, and PCM support. They pair with `drivers/most/Makefile`, which maps these symbols to object files.

## Risks and edge cases
- `MOST` depends on `CONFIGFS_FS`, so systems without configfs cannot build even the core.
- Component symbols are only visible inside `if MOST`; users must enable the core before cdev/sound/USB choices appear.
- The cdev and sound help text contains a typo ("commumicate"), but it does not affect build behavior.

## Test signals
Build matrix checks should cover `MOST=y/m`, individual components as built-in/modules, dependency rejection when `CONFIGFS_FS`, `USB`, or `SND` are absent, and module names matching the help text and Makefile.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/Kconfig -->

## sources/distributed-fs/ceph-client/drivers/most/Makefile
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/Makefile -->
# sources/distributed-fs/ceph-client/drivers/most/Makefile

## Purpose
This Makefile wires the MOST subsystem Kconfig symbols to kernel build targets.

## Important build rules
- `obj-$(CONFIG_MOST) += most_core.o` builds the core when `MOST` is enabled.
- `most_core-y := core.o configfs.o` links `core.c` and `configfs.c` into the core module/object.
- `obj-$(CONFIG_MOST_USB_HDM) += most_usb.o` builds the USB hardware-dependent module.
- `obj-$(CONFIG_MOST_CDEV) += most_cdev.o` builds the cdev userspace component.
- `obj-$(CONFIG_MOST_SND) += most_snd.o` builds the sound component.

## Control flow and integration behavior
There is no runtime control flow. Build flow is controlled by Kbuild expansion of `obj-*` and composite object rules. Because `configfs.o` is part of `most_core-y`, configfs support is compiled into the core object rather than as a separate module.

## State and persistence
The file has no runtime state. Its effects are build artifacts determined by kernel configuration.

## Dependencies and integration points
This Makefile integrates with the Kbuild system and the symbols defined by the adjacent Kconfig. The source files referenced here provide the core bus/buffer manager, configfs interface, USB HDM, character device component, and sound component.

## Risks and edge cases
- Renaming source files or Kconfig symbols without updating this Makefile breaks builds.
- `most_core-y` means `configfs.c` initialization is expected from core initialization; any change to that coupling must adjust both files.
- Component modules depend at runtime on symbols exported from the core, so build configurations should ensure module dependencies are generated.

## Test signals
Useful checks are `make M=drivers/most` for all enabled combinations, module dependency inspection for `most_cdev` and `most_sound`, and confirming `most_core.o` contains both core and configfs objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/Makefile -->

## sources/distributed-fs/ceph-client/drivers/most/configfs.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/configfs.c -->
# sources/distributed-fs/ceph-client/drivers/most/configfs.c

## Purpose
This file implements the configfs control plane for the MOST stack. It lets users create named links between MOST interface channels and components, set channel configuration values, and create sound-card groupings before asking the component to complete configuration.

## Important APIs, types, and functions
- `struct mdev_link` represents one configfs item/link. It stores link lifecycle flags, channel config values, device/channel/component names, component parameters, and a list node for deferred reapplication.
- `set_config_and_add_link()` pushes all stored configuration values into MOST core setters and then calls `most_add_link()`.
- Attribute store/show functions implement configfs fields: `device`, `channel`, `comp`, `comp_params`, `num_buffers`, `buffer_size`, `subbuffer_size`, `packets_per_xact`, `datatype`, `direction`, `dbr_size`, `create_link`, and `destroy_link`.
- `struct most_common` and static instances `most_cdev`, `most_net`, and `most_video` create component-specific configfs subsystems whose new items default `comp` to the subsystem component.
- `struct most_sound`, `struct most_snd_grp`, and related operations model sound-card groups and gate creation of a new sound group until the previous one is complete.
- Exported functions `most_register_configfs_subsys()`, `most_deregister_configfs_subsys()`, and `most_interface_register_notify()` are used by MOST core/components.

## Control flow
Component registration calls `most_register_configfs_subsys()`, which selects a static subsystem by component name and registers it with configfs. Creating an item under `most_cdev`, `most_net`, or `most_video` allocates `mdev_link`, takes a module reference for the component, initializes the config item, defaults the component name, and records the link name. User writes validate and store attributes. Writing true to `create_link` invokes `set_config_and_add_link()`, adds the link to `mdev_link_list`, and marks the link created. Writing true to `destroy_link` removes the link through `most_remove_link()` and deletes it from the list.

On config item release, a link that was not explicitly destroyed is removed from MOST core before the item is freed. For sound, configfs creates nested groups; writing true to `create_card` calls `most_cfg_complete("sound")`. `most_interface_register_notify()` iterates stored links when a matching interface appears, reapplies config/link creation, and triggers sound config completion if needed.

## State and persistence
Runtime state is in static configfs subsystem objects, `mdev_link_list`, and `most_sound_subsys.soundcard_list`. Configfs items persist only while mounted/configured in memory; there is no disk persistence. Module references keep component modules loaded while configfs items exist.

## Dependencies and integration points
The file depends on configfs, module refcounting, and MOST core exported configuration/link APIs. It integrates with cdev/net/video/sound components by name and with interface registration notifications from `core.c`.

## Risks and edge cases
- `mdev_link_list` is global and not visibly protected by a dedicated lock; configfs serialization may be relied upon.
- `destroy_link_store()` calls `list_del()` when the global list is non-empty, not when this item is known linked; double delete or wrong-list assumptions are risk points.
- Direction/datatype stores use `strcpy()` after validation against short literals, while other string stores use `strscpy()`.
- `set_config_and_add_link()` ignores `-ENODEV` from individual setters but still attempts link creation, supporting deferred interface appearance but making error interpretation nuanced.

## Test signals
Exercise configfs item creation/removal for cdev/net/video/sound, each attribute parser, invalid direction/datatype values, create/destroy link sequencing, module unload with live configfs items, deferred link reapplication when interfaces register after configfs setup, and sound group `create_card` ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/configfs.c -->

## sources/distributed-fs/ceph-client/drivers/most/core.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/core.c -->
# sources/distributed-fs/ceph-client/drivers/most/core.c

## Purpose
This file implements the MOST core bus, interface/channel registration, component linking, channel configuration, buffer-object allocation, enqueueing, completion routing, and exported APIs consumed by MOST components and hardware-dependent modules.

## Important APIs, types, and functions
- `struct most_channel` wraps a Linux `struct device` plus per-channel config, linked components (`pipe0`/`pipe1`), buffer FIFOs, trash/halt queues, starvation state, enqueue thread, locks, completion, and counters.
- `struct interface_private` stores the generated device id, name, channel array, and channel list for each `struct most_interface`.
- Exported configuration/link APIs include `most_set_cfg_*()`, `most_add_link()`, `most_remove_link()`, and `most_cfg_complete()`.
- Exported buffer/channel APIs include `most_start_channel()`, `most_stop_channel()`, `channel_has_mbo()`, `most_get_mbo()`, `most_put_mbo()`, `most_submit_mbo()`, `most_register_component()`, `most_deregister_component()`, `most_register_interface()`, `most_deregister_interface()`, `most_stop_enqueue()`, and `most_resume_enqueue()`.
- `mostbus` is a custom bus with interface and channel devices plus sysfs/driver attributes for links, components, channel capabilities, and selected settings.

## Control flow
`most_init()` initializes the component list and ID allocator, registers the `most` bus and core driver, then initializes configfs static groups. Hardware modules call `most_register_interface()` with an initialized `struct most_interface`. The core validates callbacks, allocates an interface-private object and ID, adds the parent interface device to the MOST bus, creates one child channel device per advertised channel, initializes locks/FIFOs/config, and calls `most_interface_register_notify()` so configfs-created links can bind to newly available interfaces.

Components register through `most_register_component()` and are later linked to channels by `most_add_link()`, which locates the channel and component, assigns an empty pipe slot, and calls the component's `probe_channel()`. Starting a channel via `most_start_channel()` acquires the HDM module, calls the interface `configure()` callback with current channel config, allocates MBOs and coherent buffers, starts an enqueue kthread, partitions buffers between two component pipes, and increments the calling component's ref count.

For TX, components take buffers from `most_get_mbo()`, fill them, and submit through `most_submit_mbo()`, which queues to `halt_fifo` for the HDM enqueue thread. TX completion recycles buffers through `arm_mbo()`. For RX, buffers are initially queued to the HDM; `most_read_completion()` routes received MBOs to linked component `rx_completion()` callbacks or requeues them. Stopping a channel stops the enqueue thread, module-puts the HDM, poisons the channel, calls `poison_channel()`, flushes FIFOs/trash, waits for MBO cleanup, and decrements pipe refs.

## State and persistence
State is in memory only: bus devices, channel config, component links, buffer pools, FIFO lists, IDA IDs, kthreads, and module references. There is no disk persistence. Sysfs exposes current capabilities/settings but does not store them.

## Dependencies and integration points
The file depends on Linux device/bus/sysfs APIs, kthreads, wait queues, lists, spinlocks, mutexes, completions, atomic counters, DMA helpers, IDA, and MOST public types from `<linux/most.h>`. It integrates with configfs through `configfs_init()` and `most_interface_register_notify()`.

## Risks and edge cases
- Component list and link operations are not guarded by an obvious global mutex; runtime safety depends on higher-level registration/link sequencing.
- Two components may share one channel through `pipe0` and `pipe1`; buffer partitioning and ref counting need careful testing.
- `most_stop_channel()` decrements refs after teardown decisions; incorrect caller pairing can underflow pipe refs.
- MBO cleanup waits on `mbo_ref`; leaks or missing completion callbacks can hang stop.
- `most_register_interface()` error cleanup must unwind partially registered channel devices correctly.

## Test signals
Test component registration/deregistration, interface registration with 0/1/many channels, configfs link creation before and after interface registration, start/stop with one and two components, RX/TX completion routing, starvation reporting, `most_stop_enqueue()`/`most_resume_enqueue()`, HDM enqueue failure, poison cleanup, sysfs `links`/`components`, and module unload ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/core.c -->

## sources/distributed-fs/ceph-client/drivers/most/most_cdev.c
<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/most_cdev.c -->
# sources/distributed-fs/ceph-client/drivers/most/most_cdev.c

## Purpose
This file implements the MOST character-device component. It creates `/dev` nodes for linked MOST channels and exposes blocking/nonblocking read, write, poll, open, and close operations backed by MOST buffer objects.

## Important APIs, types, and functions
- `struct cdev_component comp` stores the allocated character-device region, minor ID allocator, major number, and embedded `struct most_component` callbacks.
- `struct comp_channel` represents one cdev-linked MOST channel, including wait queue, unlink spinlock, cdev/device, I/O mutex, MOST interface/config pointers, channel id, MBO offset, FIFO of MBO pointers, access flag, and global list node.
- File operations are `comp_open()`, `comp_close()`, `comp_read()`, `comp_write()`, and `comp_poll()`.
- MOST component callbacks are `comp_probe()`, `comp_disconnect_channel()`, `comp_rx_completion()`, and `comp_tx_completion()`.
- Module init/exit registers the cdev class, chrdev region, MOST component, and configfs subsystem.

## Control flow
When configfs links a cdev component to a MOST channel, MOST core calls `comp_probe()`. It allocates a minor, creates `comp_channel`, initializes the cdev and FIFO sized to `cfg->num_buffers`, adds the channel to `channel_list`, creates the device node using the link name, and emits a uevent.

Opening the node checks access mode against channel direction (`O_RDONLY` for RX, `O_WRONLY` for TX), rejects concurrent opens with `access_ref`, starts the MOST channel through `most_start_channel()`, and records the open. Closing clears `access_ref`, stops the channel if still connected, and destroys the channel object if it was disconnected while open.

For TX, `comp_write()` waits for an available MBO from the core, copies user data into the current MBO at `mbo_offs`, and submits the MBO when full or when the datatype is control/async. For RX, `comp_rx_completion()` receives completed MBOs from core, enqueues them into the per-cdev FIFO, and wakes readers. `comp_read()` waits for FIFO data, copies from the current MBO to userspace, and returns the MBO to core when fully consumed. `comp_poll()` reports readability or writability based on FIFO/core-buffer state and disconnect status.

## State and persistence
All state is volatile. The global `channel_list` tracks live cdev channel objects. `comp.minor_id` and the allocated chrdev region manage device numbers. Per-open state is only `filp->private_data` and per-channel `access_ref`/`mbo_offs`. There is no disk persistence beyond device nodes managed by devtmpfs/udev.

## Dependencies and integration points
The component depends on cdev, device class, IDA, kfifo, wait queues, user-copy helpers, poll, and MOST core exported APIs. It registers with MOST core as component name `"cdev"` and with configfs through `most_register_configfs_subsys()`.

## Risks and edge cases
- Only one opener is allowed per channel; clients must handle `-EBUSY`.
- Disconnect while open is handled by setting `c->dev = NULL`, waking waiters, stopping the channel, and deferring object free until close; races rely on `io_mutex` plus `unlink` spinlock.
- `comp_write()` may return a partial count after a partial user copy and only submits the MBO once the configured boundary is reached.
- `kfifo_alloc()` uses `cfg->num_buffers`; invalid or zero configuration from configfs can affect behavior.
- Exit iterates remaining channels after deregistering component/configfs, so active users must be quiesced by disconnect handling.

## Test signals
Test cdev link creation and node naming, open access-mode enforcement, single-open behavior, blocking and nonblocking reads/writes, partial read/write offsets, poll readiness, RX completion wakeups, TX completion wakeups, disconnect during blocked I/O, module unload with open and closed channels, and configfs create/destroy link cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/most_cdev.c -->
