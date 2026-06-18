# Research: subset-b-004295

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_legacy.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_legacy.c

Purpose: this file preserves the raw NAND legacy-controller path used when a controller does not implement `exec_op`. It supplies default byte/buffer I/O callbacks, legacy command sequencing for small and large page devices, ready/busy polling, and default hook validation.

Important APIs, types, and functions: `nand_legacy_set_defaults()`, `nand_legacy_adjust_cmdfunc()`, and `nand_legacy_check_hooks()` are the exported setup helpers for legacy drivers. `nand_wait_ready()` and the internal `nand_wait()` implement ready/status polling. `nand_command()` and `nand_command_lp()` translate generic NAND commands into CLE/ALE cycles through `chip->legacy.cmd_ctrl`. The default 8-bit and 16-bit read/write callbacks use `readb/readw`, `iowrite*_rep`, and `ioread*_rep`.

Control flow: controller setup calls the defaults unless `nand_has_exec_op()` is true. Command flow latches commands, emits column and row address cycles, handles bus-width column adjustment, and then either returns immediately for commands with explicit busy handling or waits using `dev_ready`, status reads, fixed command delays, and tWB/tCCS delays. Large-page handling emulates OOB reads as `READ0` with an OOB column and issues `READSTART` or `RNDOUTSTART` where required.

State and persistence: the file mutates only `struct nand_chip` callback pointers and options-derived behavior. Runtime state is hardware line state behind the controller callbacks plus the MTD `oops_panic_write` flag, which switches waits to polling loops that touch the watchdog instead of scheduling.

Dependencies and integration points: this code depends on `internals.h`, legacy `struct nand_chip.legacy` hooks, MTD geometry, jiffies/delay helpers, soft-lockup watchdog handling, and raw NAND operation helpers such as `nand_status_op()` and `nand_read_data_op()`.

Risks: legacy callbacks require `cmd_ctrl` and correct IO addresses; a missing hook fails attach. Timing fallback paths assume `chip_delay` and `dev_ready` reflect board behavior. 16-bit byte writes intentionally zero/ignore upper bus bits, which can expose controller-specific assumptions. Command/address sequences are compatibility-sensitive because many old board drivers depend on this path.

Test signals: exercise a legacy-only controller through ID read, reset, page/OOB read, page program, erase, random column read/write, 8-bit and 16-bit bus modes, no-R/B polling fallback, panic/oops write waits, and large-page command adjustment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_legacy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_macronix.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_macronix.c

Purpose: this manufacturer extension configures Macronix raw NAND quirks and features: bad-block marker policy, read retry, randomizer OTP enablement, block protection, deep power-down suspend/resume, and OTP user-protection-region access for selected AC devices.

Important APIs, types, and functions: `macronix_nand_manuf_ops` exposes `.init`. `macronix_nand_onfi_init()` parses the Macronix ONFI vendor table. `macronix_nand_setup_read_retry()` writes `ONFI_FEATURE_ADDR_READ_RETRY`. `macronix_nand_randomizer_check_enable()` programs randomizer OTP bits. `mxic_nand_lock()` and `mxic_nand_unlock()` become `chip->ops.lock_area/unlock_area`. `macronix_30lfxg18ac_*_otp()` functions implement MTD user OTP callbacks.

Control flow: init marks SLC devices with first/second-page BBM, clears broken timing-mode feature bits for known AC model strings, enables ONFI-derived read retry and optional randomizer, probes block-protection support by reading the protection feature, adds deep-power-down hooks for selected AD parts, and registers OTP callbacks for supported 30LFxG18AC models.

State and persistence: state is mostly feature-register state on target 0. Randomizer OTP programming is persistent in flash. Block protection is volatile/configurable through feature address `0xA0`. Deep power-down suspend sends `0xB9`; resume toggles chip select by issuing the same low-level operation and waits for tRDP.

Dependencies and integration points: the file uses ONFI SET/GET FEATURES, device-tree property `mxic,enable-randomizer-otp`, raw page read/program helpers, target selection, MTD OTP callback slots, and manufacturer model strings.

Risks: randomizer enablement performs an OTP-affecting page program and is gated by DT but still permanent. Block-protection support assumes power-on all-lock state when probing. OTP support reports unlocked because lock state cannot be read, and locking is not supported. Deep power-down is model-list driven and only targets chip select 0.

Test signals: verify feature-list bits after init, read-retry mode changes, randomizer logs and persistence, lock/unlock behavior after probe, suspend/resume recovery after `0xB9`, OTP read/write bounds across 30 pages, and no timing-mode SET/GET attempts for broken AC models.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_macronix.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_micron.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_micron.c

Purpose: this file implements Micron-specific raw NAND setup, especially ONFI vendor read-retry support and optional Micron on-die ECC integration for SLC parts with 4-bit or 8-bit correction per 512-byte step.

Important APIs, types, and functions: `micron_nand_manuf_ops` supplies `.init`, `.cleanup`, and `.fixup_onfi_param_page`. `struct micron_nand` stores on-die ECC state and a raw comparison buffer. `micron_nand_on_die_ecc_setup()`, `micron_nand_read_page_on_die_ecc()`, and `micron_nand_write_page_on_die_ecc()` become ECC engine callbacks. OOB layouts are split between 4-bit and 8-bit on-die ECC.

Control flow: init allocates manufacturer data, parses ONFI vendor read-retry count, sets SET/GET feature support bits, marks Micron BBM locations, detects on-die ECC by enabling/disabling the feature and checking READID bit 7, rejects mandatory on-die ECC unless the user selected `NAND_ECC_ENGINE_TYPE_ON_DIE`, and then wires ECC callbacks, OOB layout, ECC geometry, and raw-page restrictions.

State and persistence: `micron->ecc.enabled` tracks the current volatile ONFI on-die ECC feature state, and `forced` records parts where firmware/hardware cannot disable ECC. For 4-bit ECC, `rawbuf` temporarily stores raw page+OOB data so corrected and raw data can be compared to estimate bitflips.

Dependencies and integration points: this code depends on ONFI parameter/vendor pages, `nand_set_features()`/`nand_get_features()`, READID behavior, generic raw page helpers, MTD ECC statistics, OOB layout APIs, and selected ECC engine type from the NAND core.

Risks: mandatory on-die ECC is rejected for normal raw operation because raw access cannot be honored. 4-bit ECC bitflip accounting rereads the page with ECC disabled and compares buffers, so ordering and OOB availability matter. Status-based 8-bit accounting reports approximate correction counts. Detection has side effects because it toggles ECC during init.

Test signals: test ONFI revision fixup for zero revision, read-retry feature programming, on-die ECC selection/rejection, corrected/failed ECC stats for 4-bit and 8-bit status patterns, raw read/write behavior on mandatory ECC parts, OOB layout offsets, and cleanup of allocated raw buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_micron.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_onfi.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_onfi.c

Purpose: this file detects and parses ONFI-compliant NAND devices. It validates parameter pages, recovers damaged parameter data by bitwise majority, fills memory-organization and ECC requirements, records optional command/timing capabilities, and parses the extended parameter page when needed.

Important APIs, types, and functions: `nand_onfi_detect()` is the main entry point, `onfi_crc16()` computes ONFI CRCs, `nand_flash_detect_ext_param_page()` extracts extended ECC requirements, and `nand_bit_wise_majority()` reconstructs a parameter page from three reads.

Control flow: detection reads ID address `0x20` and requires the `ONFI` signature. It reads up to three parameter pages, accepts the first valid CRC, or performs bitwise-majority recovery and revalidates CRC. Manufacturer fixups may patch the page before parsing. The code selects the highest supported ONFI version, sanitizes strings, fills MTD and NAND memory geometry, handles 16-bit bus flags, sets ECC requirements from either the base or extended parameter page, records SET/GET FEATURES timing support and read-cache support, and stores selected timing values in `chip->parameters.onfi`.

State and persistence: parsed model string and `struct onfi_params` are allocated and stored in `chip->parameters`. Geometry and ECC requirements are copied into `nand_memory_organization`, `mtd_info`, and `nand_device` state; there is no persistent flash mutation.

Dependencies and integration points: this code uses raw NAND read-id/read-param/change-column/data helpers, manufacturer fixup hooks, `nand_legacy_adjust_cmdfunc()` for extended parameter reads on legacy controllers, string sanitization, and ONFI structures from the raw NAND internals.

Risks: non-power-of-two page/block counts are truncated to match MTD expectations. Extended parameter parsing depends on Change Read Column support and may only warn if it fails. Model string allocation can fail after some state has been partially parsed. Majority recovery can accept only data that still passes CRC.

Test signals: test ONFI and non-ONFI ID paths, valid and invalid CRC handling, majority recovery, unsupported revision rejection, extended ECC section parsing, 16-bit bus detection, SET/GET timing feature bits, read-cache capability, manufacturer fixup invocation, and cleanup on allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_onfi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_samsung.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_samsung.c

Purpose: this manufacturer file decodes Samsung raw NAND IDs and applies Samsung-specific initialization options for page/OOB/block geometry, ECC requirements, subpage-write restrictions, and bad-block marker placement.

Important APIs, types, and functions: `samsung_nand_manuf_ops` provides `.detect` and `.init`. `samsung_nand_decode_id()` handles both newer 6-byte MLC Samsung IDs and the generic extended-ID path. `samsung_nand_init()` applies large-page and BBM options.

Control flow: detect chooses the Samsung 6-byte MLC decode when ID length is 6 and the sixth byte is nonzero; it extracts page size, OOB size, eraseblock size, and ECC strength from extended ID bytes. Other devices use `nand_decode_ext_id()`, with special SLC cases for K9F4G08U0D ECC and K9F1G08U0E 21 nm no-subpage-write detection. Init then sets Samsung large-page options and chooses last-page BBM for MLC or first/second-page BBM for SLC.

State and persistence: no private state is allocated. The file updates memory geometry, MTD sizes, ECC requirements, and `chip->options`.

Dependencies and integration points: it relies on raw NAND ID bytes, `nand_is_slc()`, generic extended-ID decoding, `nanddev_set_ecc_requirements()`, and MTD geometry fields consumed later by core attach and controller ECC setup.

Risks: invalid or future Samsung extended-ID encodings trigger warnings and may leave incomplete OOB/ECC interpretation. The MLC ECC mapping includes high strengths at 1024-byte steps, which controller support must later satisfy. Subpage-write suppression is narrow to a specific ID pattern.

Test signals: verify decoding for 6-byte Samsung MLC IDs, SLC fallback IDs, ECC requirement propagation, OOB and eraseblock sizes, BBM option selection, large-page options, and no-subpage-write behavior for K9F1G08U0E 21 nm devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_samsung.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_sandisk.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_sandisk.c

Purpose: this small manufacturer file applies a SanDisk timing quirk for SDTNQGAMA devices whose interface timing negotiation must be limited to ONFI SDR mode 0 as the starting point.

Important APIs, types, and functions: `sandisk_nand_manuf_ops` exposes `.init`. `sdtnqgama_choose_interface_config()` fills an SDR mode-0 ONFI interface config and delegates final selection to `nand_choose_best_sdr_timings()`.

Control flow: manufacturer init checks whether `chip->parameters.model` starts with `SDTNQGAMA`; matching devices get `chip->ops.choose_interface_config` replaced with the custom chooser.

State and persistence: the only state change is the function pointer in `chip->ops`; no flash or private memory state is modified.

Dependencies and integration points: it depends on the model string populated during detection, `onfi_fill_interface_config()`, and the NAND core timing negotiation path.

Risks: the model-prefix match is intentionally narrow. If related SanDisk parts need the same limit but use different names, they will negotiate through the generic path. The code assumes `parameters.model` is valid when manufacturer init runs.

Test signals: verify SDTNQGAMA model matching, selected timing mode constraints, successful controller timing setup via `nand_choose_best_sdr_timings()`, and no behavior changes for nonmatching SanDisk devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_sandisk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_timings.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_timings.c

Purpose: this file is the raw NAND timing database and conversion helper for ONFI SDR and NVDDR interface modes. It provides reset defaults, closest-mode matching, and interface-config filling with dynamic timing values from the detected ONFI parameter page.

Important APIs, types, and functions: `nand_get_reset_interface_config()`, `onfi_find_closest_sdr_mode()`, `onfi_find_closest_nvddr_mode()`, and `onfi_fill_interface_config()` are the exported helpers. Static arrays `onfi_sdr_timings[]` and `onfi_nvddr_timings[]` define modes 0-5 in picoseconds.

Control flow: callers request a reset config, find the fastest ONFI mode satisfying a timing structure, or fill a config for a specific SDR/NVDDR mode. Fill helpers copy the static table entry and then override dynamic values such as tPROG, tBERS, tR, tCCS, and NVDDR tCAD from `chip->parameters.onfi` when available.

State and persistence: timing tables are immutable. Filled `struct nand_interface_config` values are caller-owned and transient. The only input state is `chip->parameters.onfi`.

Dependencies and integration points: this code integrates with detection results from `nand_onfi.c`, manufacturer timing quirks, controller `setup_interface` support, and core timing negotiation routines.

Risks: closest-mode helpers compare only minimum constraints, so callers must handle max timing and controller-side limits separately. Non-ONFI chips use intentionally conservative dynamic maxima. Invalid timing-mode indexes only warn and leave the caller's config unchanged.

Test signals: validate mode table values, closest-mode selection for SDR and NVDDR boundary timings, ONFI dynamic tPROG/tBERS/tR/tCCS override behavior, fast-tCAD behavior, reset mode 0 selection, and invalid mode handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_timings.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_toshiba.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_toshiba.c

Purpose: this manufacturer file decodes Toshiba raw NAND IDs, configures Toshiba SLC ECC requirements, supports BENAND on-die ECC reads, and applies model-specific timing/scrambling/pairing quirks.

Important APIs, types, and functions: `toshiba_nand_manuf_ops` exposes `.detect` and `.init`. BENAND support is implemented by `toshiba_nand_benand_init()`, `toshiba_nand_read_page_benand()`, `toshiba_nand_read_subpage_benand()`, and `toshiba_nand_benand_eccstatus()`. Model-specific interface choosers cover `TC58TEG5DCLTA00`, `TC58NVG0S3E`, and `TH58NVG2S3HBAI4` families.

Control flow: detect runs generic extended-ID decode, adjusts 24 nm raw SLC OOB size, and derives SLC ECC strength from the sixth ID byte. Init marks SLC BBM pages, enables BENAND on-die ECC callbacks when requested and detected, and then installs model-specific timing callbacks; the TC58TEG5DCLTA00 path also enables scrambling and a distance-3 pairing scheme.

State and persistence: no private allocation is used. The file changes ECC callback pointers, ECC geometry, OOB layout, MTD pairing scheme, and NAND options. BENAND ECC status updates MTD ECC stats after reads.

Dependencies and integration points: it uses raw NAND exec_op for BENAND ECC status command `0x7A`, generic raw read/page helpers, `nand_get_large_page_ooblayout()`, ONFI timing fill helpers, `nand_choose_best_sdr_timings()`, and the MTD pairing API.

Risks: BENAND detailed ECC status requires exec_op; otherwise it falls back to coarse status bits and threshold-based correction counts. Raw page operations are disabled for BENAND. Model string matches are exact or prefix based, so new revisions may miss quirks. Custom timing patches rely on manually maintained datasheet values.

Test signals: validate ID decoding for 43/32/24 nm SLC, BENAND on-die ECC read/subpage behavior, ECC stats for correctable and uncorrectable cases, OOB layout exposure, timing selection for listed models, scrambling and pairing setup, and fallback status handling when ECC status read is unsupported.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nand_toshiba.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nandsim.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nandsim.c

Purpose: `nandsim.c` is the kernel raw NAND simulator. It registers a synthetic NAND chip, emulates NAND command/address/data state transitions, stores flash contents in sparse memory or a cache file, injects bad/weak/read-disturbed behavior, supports optional software BCH ECC, partitions, BBT modes, and wear reporting through debugfs.

Important APIs, types, and functions: `struct nandsim` holds the simulated chip, controller, partitions, geometry, state machine, registers, storage backing, and debugfs node. `ops[]` describes accepted NAND operation state chains. `ns_exec_op()` bridges modern `nand_operation` instructions to the legacy state-machine callbacks. `ns_read_page()`, `ns_prog_page()`, and `ns_erase_sector()` implement storage behavior. `ns_init_module()` and `ns_cleanup_module()` own module lifetime.

Control flow: module parameters define ID bytes, timing delays, bus width, partitions, BBT behavior, weak blocks/pages, random bitflips, grave pages, override size, cache file, and BCH strength. Init allocates `struct nandsim`, performs a minimal ID-readable setup, parses fault-injection lists, initializes a NAND controller with `.exec_op`, runs `nand_scan()`, optionally overrides geometry, initializes simulator geometry/storage, creates BBT, marks configured bad blocks, registers MTD partitions, and creates debugfs wear output. Runtime operations advance through command, address, data input/output, and action states; actions copy data to the internal buffer, program pages by NAND-style bitwise AND, erase sectors, or adjust offsets.

State and persistence: simulator state includes current command/state, row/column/count/off registers, chip line levels, sparse allocated page contents or cache-file contents plus `pages_written` bits, weak/grave counters, wear counters, partitions, and optional random bitflip behavior. With `cache_file`, contents persist in the named file across module lifetimes; otherwise storage is memory-only.

Dependencies and integration points: this module integrates with the raw NAND core, MTD partition registration, software Hamming/BCH ECC, debugfs, kernel file I/O, page cache helpers, module parameters, and BBT creation. It rejects cached sequential read commands in `check_only` because the internal state model cannot distinguish those flows.

Risks: the state machine is strict and can enter failed-ready state on unexpected command/address/data ordering. Cache-file I/O is kernel-internal and uses pre-held page cache pages plus no-reclaim regions to avoid filesystem recursion. Fault injection and random bitflips make test results intentionally nondeterministic unless disabled. 16-bit mode is explicitly warned as not well tested.

Test signals: load with several ID geometries, 8/16-bit bus modes, memory and cache-file backing, partition lists, BBT modes, badblocks, weakblocks, weakpages, gravepages, bitflips, BCH strengths, page read/program/erase/OOB/random-read flows, unsupported cached-read check, debugfs wear report contents, and full cleanup without leaked list/storage allocations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nandsim.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ndfc.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ndfc.c

Purpose: this is the Open Firmware platform driver for IBM/AMCC NDFC NAND Flash Controller hardware integrated in EP440-era cores. It supports one NAND chip per controller instance, maps NDFC command/address/data registers, and uses the controller's simple hardware Hamming ECC.

Important APIs, types, and functions: `struct ndfc_controller` stores the platform device, MMIO base, embedded `nand_chip`, chip select, and `nand_controller`. Legacy hooks include `ndfc_select_chip()`, `ndfc_hwcontrol()`, `ndfc_ready()`, `ndfc_read_buf()`, and `ndfc_write_buf()`. ECC hooks are `ndfc_enable_hwecc()` and `ndfc_calculate_ecc()`.

Control flow: probe reads the `reg` property to select one of four static controller slots, maps MMIO, programs the controller configuration register and optional bank settings, then initializes the child flash node. Chip init wires legacy callbacks, ON_HOST Hamming ECC over 256-byte steps with three ECC bytes, sets the flash node and MTD name, runs `nand_scan(chip, 1)`, and registers the MTD device.

State and persistence: state lives in the static `ndfc_ctrl[]` array and hardware registers. Remove unregisters MTD, calls `nand_cleanup()`, and frees the allocated MTD name, but the MMIO mapping is manually established in probe.

Dependencies and integration points: the driver depends on OF address/property helpers, `linux/mtd/ndfc.h` register definitions, raw NAND legacy core hooks, big-endian register accessors, MTD registration, and software Hamming correction (`rawnand_sw_hamming_correct`).

Risks: the driver is legacy-callback based and only supports one chip despite hardware multichip capability. Static controller slots and manual `of_iomap()` cleanup increase lifecycle sensitivity. Buffer I/O assumes page-aligned multiples of four. ECC byte ordering is NDFC/SmartMedia-specific.

Test signals: validate DT `reg`, `ccr`, and `bank-settings`, chip-select switching, ready bit polling, command/address cycles, 32-bit buffer transfers, hardware ECC calculation and correction, MTD registration/removal, and behavior on each supported chip select.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ndfc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nuvoton-ma35d1-nand-controller.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nuvoton-ma35d1-nand-controller.c

Purpose: this is the Nuvoton MA35D1 NAND controller driver. It implements an `exec_op` raw NAND controller with DMA-backed full-page transfers, hardware BCH ECC for 2K/4K/8K pages, redundant-area management, IRQ completion, and Device Tree child-chip registration.

Important APIs, types, and functions: `struct ma35_nand_info` holds controller state, MMIO registers, clock, IRQ, completion, shared DMA buffer, and chip list. `struct ma35_nand_chip` embeds `nand_chip` and chip-select metadata. Key functions are `ma35_nand_attach_chip()`, `ma35_nfc_exec_op()`, `ma35_nand_do_read()`, `ma35_nand_do_write()`, `ma35_nfi_ecc_check()`, `ma35_nfi_correct()`, and the HWECC page/subpage/OOB callbacks.

Control flow: probe allocates the controller, maps registers, enables `nand_gate`, requests the IRQ, globally resets/enables NAND hardware, disables write protect, and scans child nodes. Each child validates `reg` chip selects, prevents duplicate CS assignment, sets the flash node and OOB layout, runs `nand_scan()`, and registers MTD. Attach rejects 16-bit bus, programs page-size bits, wires ON_HOST ECC callbacks when selected, configures BCH strength 8/12/24, parity byte counts, redundant-area size, and DMA/subpage options.

State and persistence: persistent driver state includes the child chip list, assigned chip-select bitmap, completion object, and shared page buffer. Hardware state includes NANDCTL page/ECC/DMA bits, redundant-area registers, DMA source address, interrupt status/enables, and ECC result/address/data registers. Remove unregisters all MTDs and cleans NAND chips; devm handles MMIO/clock/IRQ allocations.

Dependencies and integration points: the driver uses raw NAND controller ops, MTD OOB layout APIs, DMA mapping, platform IRQs, completions, common clocks, OF child nodes, and MA35 NFI registers. It integrates with NAND core page helpers for command sequencing and uses controller-specific redundant-area registers for OOB/ECC bytes.

Risks: full-page DMA is required for page-sized transfers, with one-second timeout handling. ECC correction mutates both data and redundant-area registers based on hardware error addresses; parity offset math must match BCH mode. Prefix-empty redundant-area detection treats pages as erased. The probe error path manually disables a devm-enabled clock, which is worth reviewing in lifecycle tests.

Test signals: validate 2K/4K/8K page setup, BCH8/12/24 parity totals, DMA read/write completions and timeouts, ECC corrected/uncorrectable paths, subpage write masks, OOB layout and redundant-area reads, empty-page detection, wait-ready polling via `INT_RB0`, duplicate/invalid chip selects, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/nuvoton-ma35d1-nand-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/omap2.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/omap2.c

Purpose: this is the TI OMAP2+ GPMC NAND glue driver. It connects raw NAND to the GPMC FIFO/register interface, supports polled/prefetch/DMA/IRQ transfer modes, implements Hamming and BCH ECC modes, integrates with the ELM BCH decoder, and registers an MTD device from Device Tree.

Important APIs, types, and functions: `struct omap_nand_info` stores the embedded `nand_chip`, GPMC chip select, transfer mode, ECC mode, ELM node/device, DMA channel, IRQs, FIFO/register pointers, ready GPIO, and ECC page grouping. Controller ops are `omap_nand_attach_chip()`, `omap_nand_detach_chip()`, and `omap_nand_exec_op()`. Major helpers cover prefetch setup/reset, DMA transfer, IRQ transfer, Hamming ECC, BCH ECC generation, ELM correction, BCH page read/write, and OOB layout.

Control flow: probe parses `reg`, `ti,elm-id`/`elm_id`, `ti,nand-ecc-opt`, and optional `ti,nand-xfer-type`, obtains GPMC NAND ops/registers, maps the FIFO resource, initializes a shared GPMC `nand_controller`, reads optional ready GPIO, assigns default data I/O callbacks, runs `nand_scan()`, and registers MTD. Attach selects data-transfer callbacks, requests DMA or IRQs when configured, validates ECC dependencies, then wires ECC geometry/callbacks and OOB layouts for software Hamming, hardware Hamming, BCH with software correction, or BCH with ELM correction.

State and persistence: state includes selected transfer and ECC modes, DMA channel, interrupt completions, ELM device reference, GPMC register programming, and ECC grouping fields (`neccpg`, `nsteps_per_eccpg`, `eccpg_size`, `eccpg_bytes`). Runtime flash persistence is normal NAND media; the driver itself maintains no on-disk state. Remove releases BCH resources, DMA, MTD registration, and NAND cleanup.

Dependencies and integration points: the file depends on GPMC NAND platform ops, raw NAND controller APIs, DMAengine, GPIO ready polling, ELM platform data, software BCH library, OMAP BCH Kconfig support, MTD OOB layout helpers, and OF match data from OMAP NAND platform headers.

Risks: many ECC modes have different OOB reservations and boot-ROM compatibility bytes; wrong DT choices can make existing media unreadable. Prefetch/DMA/IRQ paths have fallback behavior but depend on GPMC FIFO status and completion ordering. ELM availability is required for hardware BCH correction. Erased-page bitflip handling is custom and must stay aligned with NAND core behavior. The shared controller serializes access to the GPMC ECC engine across instances.

Test signals: cover all transfer modes, ready GPIO and soft wait paths, Hamming and BCH4/8/16 ECC modes, ELM missing/present cases, OOB layout size checks, erased-page bitflip correction, BCH page and subpage writes, DMA fallback for invalid buffers, IRQ FIFO/count completions, DT parsing failures, MTD registration, and cleanup after attach/probe errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/omap2.c -->
