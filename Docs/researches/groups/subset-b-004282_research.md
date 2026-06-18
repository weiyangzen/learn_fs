# Research: subset-b-004282

Grouped source-tree-aligned research for the subset B work item. Each file section is delimited for deterministic reconciliation into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/most_snd.c -->
# sources/distributed-fs/ceph-client/drivers/most/most_snd.c

## Purpose

`most_snd.c` is the ALSA-facing component for the MOST core. It exposes MOST synchronous audio channels as ALSA PCM playback or capture devices, translates ALSA ring-buffer traffic to and from MOST buffer objects (`struct mbo`), and registers itself as a `struct most_component` named `"sound"`. The driver is not a hardware driver by itself; it depends on a MOST hardware dependent module, such as the USB HDM, to provide `most_interface` channels and MBO transport.

## Important APIs, Types, and Functions

The central per-channel state is `struct channel`: it binds an ALSA `snd_pcm_substream`, channel hardware constraints, the `most_interface`, `most_channel_config`, ALSA card, channel id, ring positions, stream-running state, a playback kthread, a waitqueue, and a selected endian/width copy function. `struct sound_adapter` groups all audio channels belonging to one MOST interface under a single ALSA card and tracks whether the card has been registered.

Key ALSA callbacks are `pcm_open`, `pcm_close`, `pcm_prepare`, `pcm_trigger`, and `pcm_pointer`, collected in `pcm_ops`. MOST component callbacks are `audio_probe_channel`, `audio_disconnect_channel`, `audio_rx_completion`, `audio_tx_completion`, and `audio_create_sound_card`, collected in `comp`. `audio_init` registers the component and configfs subsystem; `audio_exit` unregisters both.

Data conversion helpers are `swap_copy16`, `swap_copy24`, `swap_copy32`, and directional wrappers such as `alsa_to_most_copy16` and `most_to_alsa_copy32`. `copy_data` is the shared transfer primitive; it copies between `runtime->dma_area` and `mbo->virt_address`, handles ring wrap, advances `buffer_pos` and `period_pos`, and returns whether ALSA should be notified via `snd_pcm_period_elapsed`.

## Control Flow

Channel creation begins when MOST core calls `audio_probe_channel`. The function rejects non-synchronous channels, parses the configfs argument string as `<channels>x<sample-resolution>`, locates or allocates a `sound_adapter`, allocates a `channel`, calculates ALSA hardware constraints with `audio_set_hw_params`, creates one PCM device with either playback or capture stream count, installs `pcm_ops`, and assigns vmalloc-managed PCM buffers.

After all requested channels are configured, `audio_create_sound_card` registers the first unregistered adapter card. Opening a PCM stream stores the substream, starts a playback kthread for TX, and calls `most_start_channel`. Preparing the stream selects the copy function based on direction, sample width, and endian format, then resets the ring cursors. Trigger start flips `is_stream_running` and wakes the TX kthread; trigger stop clears it.

TX data flow is thread-driven. `playback_thread` waits until the stream is running and `most_get_mbo` returns a free MBO, then copies ALSA frames into the MBO and submits it with `most_submit_mbo`; MOST TX completion only wakes the waitqueue. RX data flow is completion-driven: `audio_rx_completion` finds the channel, copies received MBO data into the ALSA ring if the stream is running, returns the MBO with `most_put_mbo`, and notifies ALSA on period boundaries.

## State and Persistence Behavior

All state is runtime kernel state. There is no on-disk persistence. Adapter membership is kept in the global `adpt_list`; `iface->priv` points at the adapter. Per-channel ring state is `period_pos`, `buffer_pos`, and `is_stream_running`. ALSA card and PCM device lifetimes are tied to probe/disconnect and adapter release. The code assumes channel configuration remains valid for the channel lifetime because `struct channel` stores the `cfg` pointer from MOST core.

The playback kthread is created on open and stopped on close for TX channels. Capture channels do not create a worker thread. Disconnect removes the channel and releases the whole adapter/card once the last channel is gone.

## Dependencies and Integration Points

This file integrates three subsystems: ALSA PCM (`sound/core.h`, `sound/pcm.h`, `sound/pcm_params.h`), MOST core (`linux/most.h`), and kernel threading/waitqueues. It expects a MOST HDM to provide synchronous channels with `subbuffer_size`, `buffer_size`, `num_buffers`, and direction. Configfs integration comes from `most_register_configfs_subsys(&comp)`, and the user-provided PCM format string is passed through the MOST config path.

The ALSA hardware model is fixed to 48 kHz, interleaved, block-transfer, mmap-capable PCM. Supported sample widths are 8, 16, packed 24, and 32 bits; for little-endian formats wider than 8 bits the driver swaps byte order when moving between ALSA and MOST.

## Risks and Edge Cases

`copy_data` relies on `cfg->subbuffer_size` as the ALSA frame byte count; a zero or inconsistent subbuffer size would break frame math, although `audio_set_hw_params` catches mismatch between channel count, sample width, and subbuffer size. The global adapter list and per-channel fields are not guarded by an explicit lock in this file, so it relies on MOST/ALSA lifecycle serialization. Stream-running state is a plain boolean shared by ALSA callbacks, completion context, and the playback thread; races are mitigated by simple idempotent behavior but not strongly synchronized.

`audio_probe_channel` releases the whole adapter on several channel-local allocation failures, which is correct for newly allocated adapters but can be hazardous if later channel probing fails after earlier channels were added to the same unregistered adapter. The driver only supports one registration pass per adapter: if `adpt->registered` is already true, probing another channel returns `-ENOSPC`.

## Test Signals

Build signals are `CONFIG_MOST` plus ALSA support and this component being compiled. Runtime signals include successful component/configfs registration, ALSA card creation named `Microchip INIC`, PCM open/prepare/trigger cycles, and absence of `most_start_channel()` or PCM format errors. Functional tests should cover TX and RX at 48 kHz for all supported widths, ring wrap across `runtime->buffer_size`, period notifications, open/close cleanup, device disconnect while idle, and behavior when MOST completions arrive while the stream is stopped.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/most_snd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/most_usb.c -->
# sources/distributed-fs/ceph-client/drivers/most/most_usb.c

## Purpose

`most_usb.c` is the USB hardware dependent module for MOST. It binds supported SMSC/Microchip USB INIC bridge devices, exposes each USB endpoint as a MOST channel, implements MBO enqueueing over bulk URBs, handles endpoint stall recovery, provides DMA allocation hooks, and optionally exposes a DCI sysfs device for direct register communication on newer INIC devices.

## Important APIs, Types, and Functions

`struct most_dev` is the per-USB-interface object. It embeds a `struct most_interface`, arrays of channel capabilities/configuration, endpoint addresses, per-channel spinlocks, health flags, padding flags, clear-halt work items, per-channel URB anchors, an I/O mutex, link-status timer/work, and an optional netinfo callback. `struct most_dci_obj` backs the sysfs `dci` child device and stores the USB device plus the arbitrary register address used by `arb_value`.

The MOST interface methods are `hdm_configure_channel`, `hdm_request_netinfo`, `hdm_enqueue`, `hdm_poison_channel`, `hdm_dma_alloc`, and `hdm_dma_free`. USB lifecycle entry points are `hdm_probe`, `hdm_disconnect`, `hdm_suspend`, and `hdm_resume` through `struct usb_driver hdm_usb`. URB completions are `hdm_write_completion` and `hdm_read_completion`. DCI helpers are `drci_rd_reg`, `drci_wr_reg`, `start_sync_ep`, `value_show`, and `value_store`.

## Control Flow

Probe allocates `most_dev`, derives the channel count from endpoint descriptors, initializes locks/timer/work, fills `most_interface` callbacks and identity fields, allocates channel arrays, and maps every endpoint to a `most_channel_capability`. Capabilities advertise control, async, isochronous, and synchronous data types with direction inferred from endpoint direction and maximum buffer/count constants. The interface is registered with MOST core. For selected OS81118/OS81119/OS81210 products, probe also registers a `dci` child device with sysfs attributes for read-only and writable DRCI registers.

Channel configuration validates buffer count and size, decides whether INIC USB padding is active, computes streaming frame size from `subbuffer_size`, `packets_per_xact`, and data type, may trim `buffer_size` to a whole number of frames, stores `extra_len` for RX padded transfers, initializes clear-halt work, and starts sync endpoints for async channels.

MBO enqueue allocates one URB, serializes against disconnect with `io_mutex`, optionally pads TX streaming buffers, chooses bulk send or receive pipe based on direction, uses coherent DMA via `URB_NO_TRANSFER_DMA_MAP`, anchors the URB in the channel anchor, and submits it. Completion updates MBO status and processed length under the channel spinlock, schedules clear-halt work on `-EPIPE`, reports close on `-ENODEV`/`-EPROTO`, removes RX padding when needed, invokes `mbo->complete`, and frees the URB.

## State and Persistence Behavior

State is entirely live kernel/device state. `mdev->conf` stores the last MOST channel configuration. `padding_active` and `is_channel_healthy` are per-channel runtime flags. Anchored URBs are the in-flight persistence boundary during normal operation; suspend, poison, disconnect, and clear-halt recovery kill anchors to return ownership to MOST core. The link status timer reschedules every two seconds once requested and invokes deferred work to read MAC/link registers and call `on_netinfo`.

Disconnect nulls `usb_device` under `io_mutex`, cancels timer/work, unregisters the DCI child if present, and deregisters the MOST interface; release callbacks free dynamically allocated arrays and device objects.

## Dependencies and Integration Points

The driver sits between Linux USB core and MOST core. It depends on `linux/usb.h` for device matching, control messages, URB handling, anchors, DMA-coherent buffers, suspend/resume, and sysfs device registration. It uses MOST channel types and MBO APIs from `linux/most.h`. DCI sysfs attributes issue vendor USB control transfers to INIC register addresses such as NI state, packet bandwidth, MEP filter/hash registers, EUI-48 registers, arbitrary address/value, and sync endpoint trigger.

## Risks and Edge Cases

The driver assumes endpoints are all bulk-style MOST pipes and caps channels at `MAX_NUM_ENDPOINTS`. Probe returns directly on `most_register_interface` failure without following the local error labels, leaving cleanup to device release only if the device was registered; this path should be reviewed if ownership rules change. `hdm_enqueue` uses `GFP_KERNEL` even though its comment says it could in some cases be interrupt context. Padding math depends on nonzero `subbuffer_size` and valid `packets_per_xact`; misconfiguration returns `-EINVAL` or adjusts buffer size.

URB completion treats `-ESHUTDOWN` as success, which is intentional for teardown but can mask actual transfer truncation during shutdown. Clear-halt recovery stops enqueueing, kills anchors, clears the failed pipe, may also clear the async TX peer for async RX stalls, marks the channel healthy, and resumes enqueueing; tests need to ensure no new URB is submitted on a poisoned channel during this window.

## Test Signals

Build tests require USB, MOST, and this HDM enabled. Runtime signals include probe logs for supported VID/PID pairs, `most_register_interface` success, channel capability enumeration matching endpoint descriptors, successful `configure` and `enqueue` for TX/RX, URB completion status propagation, DCI sysfs reads/writes returning expected register values, netinfo callbacks every two seconds after request, suspend/resume killing and resuming enqueue queues, and disconnect with no use-after-free. Fault-injection tests should cover `-EPIPE`, `-ENODEV`, padding misconfiguration, USB submit failure, and clear-halt recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/most/most_usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/Kconfig

## Purpose

This `Kconfig` file defines the top-level Memory Technology Device menu and the main user/translation-layer options under `drivers/mtd`. It gates all lower MTD driver families and controls whether MTD core support, block views, translation layers, panic/oops storage, swap, partitioned master retention, virtual concatenation, chip drivers, map drivers, device drivers, NAND, LPDDR, SPI NOR, UBI, and HyperBus are visible to kernel configuration.

## Important Symbols and Structure

`menuconfig MTD` is the root tristate and implies `NVMEM`. Inside `if MTD`, the file defines `MTD_TESTS`, includes the partition parser submenu, and then declares user modules and translation layers. `MTD_BLKDEVS` is an internal tristate selected by block-style users. Visible block users include `MTD_BLOCK`, `MTD_BLOCK_RO`, `FTL`, `NFTL`, `INFTL`, `RFD_FTL`, `SSFDC`, `SM_FTL`, `MTD_OOPS`, `MTD_PSTORE`, and `MTD_SWAP`. Partition behavior is controlled by `MTD_PARTITIONED_MASTER`, and `MTD_VIRT_CONCAT` depends on it.

The bottom of the file sources submenus for `chips`, `maps`, `devices`, `nand`, `lpddr`, `spi-nor`, `ubi`, and `hyperbus`.

## Control Flow

Kconfig processing starts at `MTD`. When disabled, none of the nested menus or sourced child Kconfigs apply. When enabled as built-in or module, child symbols become available subject to their own dependencies. Several options select `MTD_BLKDEVS` to ensure `mtd_blkdevs.o` is built when a block or translation-layer facade needs it. Child Kconfigs extend the menu in place, so this file is the routing point from generic MTD support to physical chip and bus-specific drivers.

## State and Persistence Behavior

The file does not persist runtime state; it persists build-time configuration in the kernel `.config`. The selected symbols determine which objects are compiled and which MTD APIs are available at runtime. Dangerous test modules are explicitly gated by `depends on m`, encouraging modular use rather than built-in destructive tests.

## Dependencies and Integration Points

The symbols connect to `drivers/mtd/Makefile` object selection. Block-oriented options depend on `BLOCK`; `MTD_PSTORE` depends on `PSTORE_BLK`; `MTD_SWAP` depends on `SWAP`; `SM_FTL` selects NAND core and software Hamming ECC. The sourced child Kconfigs define chip probing, map drivers, raw NAND, SPI NOR, UBI, and other physical/backend integrations.

## Risks and Edge Cases

Several translation layers carry historical patent and data-loss warnings. `MTD_TESTS` can erase whole devices. `MTD_BLOCK` is documented as unsafe for general flash write emulation because erase sizes are larger than block sizes. `MTD_PARTITIONED_MASTER` changes device hierarchy and can expose master and partitions concurrently, which is useful but can be dangerous if users write overlapping regions.

## Test Signals

Configuration tests should verify that expected object files appear for each symbol combination and that dependency constraints prevent invalid builds. Runtime validation should cover MTD core registration, partition parser availability, block facade creation only when selected, UBI preference warnings remaining visible, and destructive tests only being built as modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/Makefile

## Purpose

This `Makefile` maps top-level MTD Kconfig symbols to built objects and subdirectories. It builds the MTD core aggregate, optional user-facing block/translation modules, panic/pstore/swap support, and delegates chip, map, device, NAND, test, LPDDR, SPI NOR, UBI, and HyperBus families to their own subdirectory Makefiles.

## Important Build Targets

`obj-$(CONFIG_MTD) += mtd.o` builds the core aggregate from `mtdcore.o`, `mtdsuper.o`, `mtdconcat.o`, `mtdpart.o`, and `mtdchar.o`, with `mtd_virt_concat.o` added when `CONFIG_MTD_VIRT_CONCAT` is enabled. `obj-y += parsers/` always descends into partition parsers so their own Kconfig selections can build. User-facing modules include `mtd_blkdevs.o`, `mtdblock.o`, `mtdblock_ro.o`, `ftl.o`, `nftl.o`, `inftl.o`, `rfd_ftl.o`, `ssfdc.o`, `sm_ftl.o`, `mtdoops.o`, `mtdpstore.o`, and `mtdswap.o`. `nftl-objs` and `inftl-objs` define multi-object modules.

## Control Flow

Kbuild evaluates each `obj-*` line from the resolved `.config`. Built-in selections are linked into vmlinux; module selections become loadable modules where supported. The unconditional `obj-y += chips/ lpddr/ maps/ devices/ nand/ tests/` causes traversal of those directories, but their contained objects still depend on their local `obj-$(CONFIG_...)` rules. SPI NOR, UBI, and HyperBus subdirectories are only descended when their root symbols are enabled.

## State and Persistence Behavior

This file has no runtime state. Its effect is persistent in build artifacts: it decides which object files and modules exist. The aggregate `mtd.o` shape is important because it controls which core services are always present once `CONFIG_MTD` is enabled.

## Dependencies and Integration Points

The file is the implementation side of `drivers/mtd/Kconfig`. Its names must stay aligned with source files and symbols. The `mtd-y` aggregate integrates MTD core, superblock helpers, concatenation, partitioning, and char device support. Block translation modules depend on `mtd_blkdevs.o` selected by Kconfig. Subdirectory descent integrates chip probing and concrete bus/device families.

## Risks and Edge Cases

Unconditional descent into `tests/` is safe only because the tests subdirectory must guard objects by `CONFIG_MTD_TESTS`; a bad local Makefile could accidentally build destructive tests. Removing or renaming aggregate members would silently drop core APIs. Symbol/object drift between Kconfig and this Makefile can produce selected features that do not build or dead objects that are never reachable.

## Test Signals

Build matrix tests should check `CONFIG_MTD=y`, `CONFIG_MTD=m`, and selected translation layers. `make drivers/mtd/` or equivalent kernel build targets should confirm that aggregate members and subdirectory modules are produced only for selected symbols. Link tests should cover `nftl-objs` and `inftl-objs` composition.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/chips/Kconfig

## Purpose

This file defines the RAM/ROM/Flash chip-driver Kconfig menu for MTD. It covers CFI and JEDEC probing, CFI command-set drivers, CFI geometry and byte-swap specialization, OTP support, simple RAM/ROM/absent-chip map drivers, and XIP-aware operation for supported NOR flash.

## Important Symbols and Structure

`MTD_CFI` enables Common Flash Interface probing and selects generic probe and CFI utility support. `MTD_JEDECPROBE` enables JEDEC-style probing for non-CFI-compatible flash and also selects the generic probe/utilities. `MTD_GEN_PROBE` and `MTD_CFI_UTIL` are internal support symbols.

Advanced configuration is gated by `MTD_CFI_ADV_OPTIONS`. The byte-swap choice selects `MTD_CFI_NOSWAP`, `MTD_CFI_BE_BYTE_SWAP`, or `MTD_CFI_LE_BYTE_SWAP`. `MTD_CFI_GEOMETRY` exposes bus-width and chip-interleave selectors: map bank widths from 1 to 32 bytes and interleave counts from 1 to 8. `MTD_OTP` enables protection-register/one-time-programmable operations. Command-set drivers are `MTD_CFI_INTELEXT` for command set 0001, `MTD_CFI_AMDSTD` for command set 0002, and `MTD_CFI_STAA` for command set 0020. Simple map-backed devices are `MTD_RAM`, `MTD_ROM`, and `MTD_ABSENT`. `MTD_XIP` enables execute-in-place-aware CFI operation on eligible architectures.

## Control Flow

The menu is visible when `MTD != n`. Probe choices feed the common CFI/JEDEC probe path, which identifies flash geometry and command-set IDs. The command-set selections decide which `cfi_cmdset_*.o` driver is available to bind to probed chips. Geometry symbols are compile-time specialization knobs that can reduce code size or enable exotic widths/interleaves. XIP support is only offered for non-SMP architectures with `ARCH_MTD_XIP` and Intel/AMD CFI command-set support.

## State and Persistence Behavior

The file stores compile-time capabilities in `.config`. Some choices materially affect generated code paths, particularly byte swapping, bank-width helpers, interleave support, OTP APIs, and XIP handling. No runtime state is created by this file itself.

## Dependencies and Integration Points

Selections align with `drivers/mtd/chips/Makefile`, especially `cfi_probe.o`, `jedec_probe.o`, `gen_probe.o`, `cfi_util.o`, and the command-set modules. `MTD_XIP` integrates with architecture support and command-set driver XIP paths. OTP configuration exposes MTD protection-register hooks implemented by command-set drivers such as `cfi_cmdset_0001.c` and `cfi_cmdset_0002.c`.

## Risks and Edge Cases

Incorrect byte-swap or geometry selections can make probe commands unreadable by the chip. Reducing supported bank widths/interleaves can save code size but break boards with different wiring. OTP support is inherently risky: writes and locks are one-time operations. XIP support has tight constraints around interrupt masking and flash array mode; enabling it on unsuitable platforms would be dangerous, hence the strict dependencies.

## Test Signals

Config tests should verify that CFI and JEDEC probes select their utility dependencies, command-set symbols build the expected objects, advanced geometry defaults include common 8/16/32-bit bus widths and 1/2 interleaves, and XIP is only visible under its architecture constraints. Hardware tests should confirm probe success, correct endianness, OTP visibility when enabled, and successful command-set binding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/chips/Makefile

## Purpose

This `Makefile` maps MTD chip-driver Kconfig symbols to probe, utility, command-set, and simple map-backed chip driver objects.

## Important Build Targets

`chipreg.o` is built whenever `CONFIG_MTD` is enabled. CFI and JEDEC support build `cfi_probe.o`, `jedec_probe.o`, `gen_probe.o`, and `cfi_util.o` according to the selected symbols. Command-set implementations map directly to `cfi_cmdset_0020.o`, `cfi_cmdset_0002.o`, and `cfi_cmdset_0001.o`. Simple map drivers are `map_ram.o`, `map_rom.o`, and `map_absent.o`.

## Control Flow

Kbuild descends here from `drivers/mtd/Makefile`. Each `obj-$(CONFIG_...)` line is resolved from `.config`. Probe support and command-set support can be built independently enough that a probe can identify devices while command-set modules provide the operation callbacks for matching IDs.

## State and Persistence Behavior

The file has no runtime state, but it controls whether the kernel image or module tree contains the chip registry, CFI/JEDEC probing, command-set drivers, and simple RAM/ROM/absent devices. Missing objects translate directly into unsupported flash at runtime.

## Dependencies and Integration Points

This file is paired with `drivers/mtd/chips/Kconfig`. `cfi_cmdset_0001.o` and `cfi_cmdset_0002.o` export command-set entry points consumed by generic CFI probe code. `chipreg.o` supports chip-driver registration. `cfi_util.o` provides shared helpers used by the command-set drivers.

## Risks and Edge Cases

Symbol/object mismatch is the main risk. For example, enabling `MTD_CFI_AMDSTD` must build `cfi_cmdset_0002.o`; otherwise AMD/Fujitsu CFI flash probes would identify devices but lack operation methods. Conversely, building probe utilities without command-set support may detect but not use some chips.

## Test Signals

Build tests should assert that each chip Kconfig symbol produces the expected object or module. Runtime smoke tests should verify CFI probe plus command-set binding for Intel/Sharp and AMD/Fujitsu flash, and simple map RAM/ROM registration when those symbols are selected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0001.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0001.c

## Purpose

`cfi_cmdset_0001.c` implements the MTD NOR flash command-set driver for CFI command set 0001, the Intel/Sharp extended command set, with aliases for command sets 0003 and 0200. It turns probed CFI/Jedec map data into an `mtd_info`, supplies read/write/erase/lock/OTP/suspend/resume/reset operations, handles Intel/Sharp-specific status polling and suspend behavior, and applies many vendor/device fixups.

## Important APIs, Types, and Functions

The exported entry points are `cfi_cmdset_0001`, `cfi_cmdset_0003`, and `cfi_cmdset_0200`, all registered with `EXPORT_SYMBOL_GPL`. `cfi_intelext_chipdrv` names the chip driver and points destruction to `cfi_intelext_destroy`.

Setup is split between `read_pri_intelext`, `cfi_cmdset_0001`, `cfi_intelext_setup`, and `cfi_intelext_partition_fixup`. Fixups include Atmel PRI conversion, FWH lock support, ST buffer-write corrections, Sharp LH28F640BF partition reset, point support for linear maps, write-buffer enablement, and power-up lock handling.

Operational methods installed into `mtd_info` include `_read`, `_write`, `_writev`, `_erase`, `_sync`, `_lock`, `_unlock`, `_is_locked`, `_suspend`, `_resume`, and optional OTP hooks under `CONFIG_MTD_OTP`. Core helpers are `get_chip`, `chip_ready`, `put_chip`, `do_read_onechip`, `do_write_oneword`, `do_write_buffer`, `do_erase_oneblock`, `do_xxlock_oneblock`, and `cfi_intelext_otp_walk`.

## Control Flow

Binding starts when generic CFI code calls `cfi_cmdset_0001(map, primary)`. The driver allocates `mtd_info`, installs default operations, reads the Intel/Sharp primary query extension for real CFI devices, validates versions 1.0 through 1.5, endian-swaps feature fields and OTP/partition extension data, applies CFI/Jedec/generic fixups, initializes per-chip write/erase timeout fields and waitqueues, sets `map->fldrv`, and calls `cfi_intelext_setup`.

`cfi_intelext_setup` computes total MTD size and erase regions from CFI geometry, allocates per-region lock maps, installs OTP callbacks when enabled, optionally rewrites the CFI chip model for hardware partitions, takes a module reference, and registers a reboot notifier. Hardware partition fixup can replace one physical `cfi_private` with virtual `flchip` entries sharing `flchip_shared` arbitration state.

Read and point operations acquire chips with `get_chip` in `FL_READY` or `FL_POINT`, switch to array mode with command `0xff` when necessary, copy from the map, and release with `put_chip`. Write paths handle unaligned bytes by constructing partial `map_word` values, then issue Intel word program (`0x40` or performance `0x41`) or write-buffer program (`0xe8`/`0xe9`, count, data, `0xd0`). Erase issues clear status (`0x50`), block erase (`0x20`, `0xd0`), waits, reads status, retries selected failures, and maps protection/VPP/status failures to Linux errors.

## State and Persistence Behavior

Persistent hardware state includes programmed flash contents, erased blocks, block lock bits, and OTP protection registers. Runtime state is held in `cfi_private`, `flchip`, `flchip_shared`, `mtd_erase_region_info.lockmap`, and the `mtd_info` callbacks. `flchip->state` tracks modes such as `FL_READY`, `FL_STATUS`, `FL_ERASING`, `FL_WRITING`, `FL_POINT`, `FL_PM_SUSPENDED`, and `FL_SHUTDOWN`; `oldstate`, suspend flags, and in-progress block fields allow erase/write suspend and resume.

For chips flagged `MTD_POWERUP_LOCK`, suspend saves lock state into per-region bitmaps and resume unlocks blocks that were previously unlocked, compensating for chips that power up locked. Reboot and destroy reset all chips to read-array mode so firmware can execute from flash after soft reboot.

## Dependencies and Integration Points

The driver depends on MTD map, CFI, XIP, reboot notifier, bitmap, and waitqueue/mutex infrastructure. It consumes CFI probe data from `map->fldrv_priv`, uses map callbacks for command writes and memory copies, and exposes standard MTD operations to filesystems, UBI, block facades, and user tools. `fwh_lock.h` supplies firmware-hub lock fixups. `CONFIG_MTD_XIP` changes wait behavior to suspend flash operations around pending interrupts while code executes from flash.

## Risks and Edge Cases

This file is a dense hardware state machine. Major risks are incorrect CFI tables, erase-region sums not matching device size, mishandled hardware partitions, suspend interactions across shared partitions, and chips that report support for features with errata. The code contains explicit workarounds for buggy Micron/Numonyx erase suspend on small blocks, Sharp partition registers, Atmel PRI layout, and power-up lock behavior.

Write-buffer programming must not cross write-buffer boundaries and must clear status bits before starting. OTP writes and locks are irreversible. XIP paths disable interrupts and require `__xipram`-safe code; mistakes can deadlock systems executing from flash. Lock/unlock commands may take up to 1.5 seconds on older Intel flashes.

## Test Signals

Build signals include `CONFIG_MTD_CFI_INTELEXT`, optional `CONFIG_MTD_OTP`, and optional `CONFIG_MTD_XIP`. Hardware validation should cover CFI and JEDEC probe binding, erase-region layout, linear-map point/unpoint reference counts, word and buffer writes including unaligned boundaries, erase suspend while reading/writing another block, block lock/unlock/is_locked, suspend/resume preserving lock state, OTP read/write/lock on expendable parts, reboot reset to array mode, and failure injection for VPP/protection/status timeout paths. MTD test modules can exercise read/write/erase behavior but must be used only on disposable flash.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0001.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0002.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0002.c

## Purpose

`cfi_cmdset_0002.c` implements the MTD NOR flash command-set driver for CFI command set 0002, the AMD/Fujitsu/Spansion standard command set, with aliases for command sets 0006 and 0701. It provides MTD read, word write, write-buffer write, erase, panic write, OTP/SecSi access, lock support for selected protection schemes, power management, and reset handling for AMD-style command sequences.

## Important APIs, Types, and Functions

The exported entry points are `cfi_cmdset_0002`, `cfi_cmdset_0006`, and `cfi_cmdset_0701`. `cfi_amdstd_chipdrv` registers the driver name and destroy method. The command-set setup path is `cfi_cmdset_0002` followed by `cfi_amdstd_setup`.

Operational callbacks installed in `mtd_info` include `_read`, `_write`, `_erase`, `_sync`, `_suspend`, `_resume`, `_panic_write`, OTP info/read/write/lock callbacks, and optionally `_lock`, `_unlock`, and `_is_locked` for Atmel or PPB protection schemes. Important helpers include `chip_ready`, `chip_good`, `cfi_check_err_status`, `get_chip`, `put_chip`, `do_read_onechip`, `do_write_oneword`, `do_write_buffer`, `cfi_amdstd_panic_write`, `do_erase_chip`, `do_erase_oneblock`, `do_atmel_lock`, `do_ppb_xxlock`, and `cfi_amdstd_otp_walk`.

## Control Flow

Binding allocates `mtd_info`, installs default operations, reads the AMD/Fujitsu extended query table for CFI-mode devices, validates versions 1.0 through 1.5, stores it as `cmdset_priv`, applies fixups, configures optional advanced sector protection from the device tree property `use-advanced-sector-protection`, normalizes boot-block region order, and sets default unlock addresses. If no PRI exists, no-PRI SST fixups can still provide geometry and unlock details. JEDEC mode applies FWH lock fixups for selected SST devices.

`cfi_amdstd_setup` computes total size and erase regions from CFI geometry, validates the sum against chip size, registers the reboot notifier, and returns the ready `mtd_info`. Unlike the Intel driver, this file does not allocate per-region lock maps by default.

Read operations reset to AMD array mode with `0xf0` when needed and copy from map memory. Word writes use the AMD unlock sequence `AA`/`55`/`A0`, skip no-op writes where the old word already equals the new word, retry failures up to `MAX_RETRIES`, and use toggle-bit or status-register polling depending on CFI software features. Write-buffer operations use `AA`/`55`, buffer load `0x25`, word count, data, confirm `0x29`, and a dedicated wait/reset sequence. Erase operations use the AMD erase unlock sequence ending in chip erase `0x10` or sector erase command, poll until ready or timeout, and retry failures.

## State and Persistence Behavior

Hardware persistence includes flash contents, erased sectors, SecSi/OTP contents, OTP lock register bits, Atmel locks, and PPB sector protection bits. Runtime state lives in `cfi_private`, `flchip`, and `mtd_info`. `flchip->state`, `oldstate`, waitqueues, suspend flags, and in-progress block fields serialize operations and allow erase suspend for reads/points and, on capable chips, writes.

The panic write path deliberately bypasses normal locking because it is intended for `mtdoops` during kernel panic. It repeatedly resets and polls the chip, then writes words with the same AMD command sequence to maximize odds of preserving panic logs.

## Dependencies and Integration Points

The driver depends on MTD CFI/map infrastructure, reboot notifiers, optional Open Firmware device-tree data, and XIP support. It integrates with generic CFI and JEDEC probes through exported command-set symbols and with MTD users through standard `mtd_info` callbacks. It uses `fwh_lock.h` for firmware-hub locking on selected SST devices. OTP/SecSi hooks are exposed through the MTD protection-register API.

## Risks and Edge Cases

The AMD-style status model is subtle: some chips use DQ polling while newer devices advertise status-register polling, and `CFI_QUIRK_DQ_TRUE_DATA` changes expected-data checks. Incorrect CFI boot-block data is common enough that the file has extensive boot-location and sector-count fixups for AMD, AMIC, Macronix, SST, Samsung, and Spansion parts. M29EW devices need dummy-cycle and resume-delay workarounds around erase suspend.

Write-buffer mode notes that interleaved mode is not tested and probably unsupported. PPB unlock is especially risky because the hardware unlock command unlocks all sectors on the chip; the driver snapshots other sector lock states and relocks them, but failures in the middle can temporarily expose sectors. OTP writes and locks are irreversible. Panic writes trade synchronization safety for crash-time logging.

## Test Signals

Build signals include `CONFIG_MTD_CFI_AMDSTD`, optional XIP, and platform/device-tree PPB configuration. Hardware tests should cover CFI and JEDEC binding, top/bottom boot-region swapping, SST no-PRI fixups, normal reads, unaligned and aligned word writes, write-buffer writes across boundaries, chip erase versus sector erase, erase suspend/resume, status-register polling devices, panic write on a disposable partition, Atmel and PPB lock/unlock/is_locked paths, OTP/SecSi read/write/lock where safe, suspend/resume, and reboot reset to array mode. MTD test modules can validate erase/read/write behavior on sacrificial devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/chips/cfi_cmdset_0002.c -->
