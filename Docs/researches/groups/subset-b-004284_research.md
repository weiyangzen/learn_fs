# subset-b-004284 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/ms02-nv.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/ms02-nv.c

Purpose: DECstation/DECsystem MS02-NV battery-backed NVRAM support. It probes fixed MIPS physical slot addresses, hides firmware diagnostic SRAM, and registers the page-aligned user NVRAM region as an `MTD_RAM` device.

Important APIs/types/functions: `ms02nv_read()` and `ms02nv_write()` are direct memcpy MTD callbacks over `ms02nv_private.uaddr`; `ms02nv_probe_one()` checks firmware magic/diagnostic words with `get_dbe()`; `ms02nv_init_one()` allocates resources, `mtd_info`, and private state; `ms02nv_remove_one()` unregisters and releases all resources. The module lifecycle is `ms02nv_init()`/`ms02nv_cleanup()`.

Control flow: init checks supported MIPS machine types, derives an address stride from memory-controller CSR bits, and walks `ms02nv_addrs`. Each candidate reserves an 8 MiB module resource, probes magic/size, creates diagnostic/user/CSR child resources, computes a page-aligned user mapping, registers the MTD, and pushes it on `root_ms02nv_mtd`. Cleanup pops that list.

State and persistence: persistent bytes live in battery-backed NVRAM. Runtime state is the global MTD linked list plus resource ownership. The driver intentionally avoids the first firmware-owned page and does not erase or validate user payloads.

Dependencies/integration: tightly coupled to MIPS DEC platform headers, CKSEG1 uncached access, Linux resource management, and MTD core registration. It uses `phys_to_virt()` rather than ioremap because this is platform memory.

Risks: no range checks in callbacks because MTD core is expected to bound requests; incorrect firmware diagnostic size or unsupported slot placement can hide usable memory; module removal assumes `root_ms02nv_mtd` is non-null per call. Probe reserves resources before validating hardware and must unwind precisely.

Test signals: boot on supported DECstation variants should log detected modules and expose `mtdN`; read/write through `mtdchar` should preserve data across reboot/power if battery is good; negative tests include unsupported `mips_machtype`, bad magic, and resource-conflict paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/ms02-nv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/ms02-nv.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/ms02-nv.h

Purpose: hardware description for the DEC MS02-NV NVRAM module. It documents the decoded SRAM/CSR layout, firmware-reserved diagnostic ranges, battery LED/CSR semantics, and the private state shared with `ms02-nv.c`.

Important APIs/types/functions: exports register/memory offsets such as `MS02NV_CSR`, `MS02NV_DIAG`, `MS02NV_MAGIC`, `MS02NV_VALID`, and `MS02NV_RAM`; status masks such as `MS02NV_CSR_BATT_OK`, `MS02NV_DIAG_SIZE_MASK`; magic IDs `MS02NV_ID` and `MS02NV_VALID_ID`; `typedef volatile u32 ms02nv_uint`; and `struct ms02nv_private`.

Control flow: the header has no executable flow, but its constants drive probe validation, size calculation, and user-region alignment in the C file. `MS02NV_RAM` is the policy boundary that excludes firmware diagnostic and validity data from the MTD.

State and persistence: `struct ms02nv_private` stores the MTD linked-list pointer, owned `struct resource` handles for module/diagnostic/user/CSR areas, full physical mapping pointer, detected size, and exposed user pointer. The constants describe persistent firmware status and battery-backed RAM content.

Dependencies/integration: includes Linux `ioport` and MTD declarations and relies on u32 types from the including compilation environment. It is private to the MS02-NV driver, not a public kernel API.

Risks: comments document a critical firmware behavior: corrupting the valid-data word area can cause firmware to disable battery backup and erase data on power-off. The C file mitigates this by exposing only page-aligned RAM starting at `0x1000`.

Test signals: code using this header should probe `MS02NV_MAGIC == MS02NV_ID`, cap detected RAM before `MS02NV_CSR`, and never expose offsets below `MS02NV_RAM` through normal MTD access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/ms02-nv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/mtd_dataflash.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/mtd_dataflash.c

Purpose: SPI MTD driver for Atmel/Microchip AT45 DataFlash chips. It handles legacy status-bit identification and JEDEC ID probing, registers DataFlash as an MTD device, and optionally exposes one-time-programmable security regions.

Important APIs/types/functions: `struct dataflash` holds command scratch bytes, page geometry, mutex, SPI device, and embedded `mtd_info`. MTD callbacks are `dataflash_erase()`, `dataflash_read()`, and `dataflash_write()`. Probe helpers include `dataflash_status()`, `dataflash_waitready()`, `jedec_probe()`, `jedec_lookup()`, `add_dataflash_otp()`, and `dataflash_probe()`. OTP callbacks are compiled under `CONFIG_MTD_DATAFLASH_OTP`.

Control flow: probe first tries JEDEC `OP_READ_ID`; if unsupported, it falls back to status-byte density decoding. Registration sets page size, page offset, total pages, MTD type `MTD_DATAFLASH`, erase/write sizes, parent device, OF node, and optional platform partitions. Reads build an 8-byte continuous-read command and one RX transfer. Writes loop page by page, optionally transfer a partial page into buffer 1, program via buffer 1, wait ready, and optionally compare. Erase validates page alignment and uses block erase for aligned 8-page spans.

State and persistence: flash contents and OTP bytes are persistent. Runtime state is per-device geometry, a mutex serializing shared command buffer and SPI transactions, and optional OTP function pointers. There is no wear state or bad-block metadata in this driver.

Dependencies/integration: integrates with the SPI core (`spi_driver`, `spi_sync`, `spi_write_then_read`), platform data partitions, OF compatibles `atmel,at45`/`atmel,dataflash`, and MTD partition registration.

Risks: comments note incomplete write error handling and no erase retry/fail-address handling. `dataflash_write()` increments `*retlen` without clearing it, depending on MTD core convention. Partial-page writes modify internal SRAM buffer 1. OTP write support is revision-sensitive.

Test signals: probe logs device name/page size; JEDEC and legacy chips should both register; page-aligned erase, cross-page writes, optional write-verify failures, OTP read/write bounds, and remove/unregister paths are important coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/mtd_dataflash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/mtd_intel_dg.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/mtd_intel_dg.c

Purpose: MTD driver for Intel discrete graphics NVM exposed by i915/xe auxiliary devices. It maps firmware-defined NVM regions into a master MTD with per-region partitions and performs register-mediated read, write, and erase operations.

Important APIs/types/functions: `struct intel_dg_nvm` owns refs, MTD, runtime-PM device, MMIO bases, lock, size, and flexible region table. Low-level helpers are `idg_nvm_read32/64()`, `idg_nvm_write32/64()`, `idg_nvm_error()`, `idg_nvm_get_access_map()`, and `idg_nvm_is_valid()`. MTD callbacks are `intel_dg_mtd_read()`, `intel_dg_mtd_write()`, and `intel_dg_mtd_erase()`. Lifecycle is `intel_dg_mtd_probe()`/`intel_dg_mtd_remove()`.

Control flow: probe copies named regions from `intel_dg_nvm_aux`, enables runtime PM, maps BAR resources, validates the flash signature, reads descriptor access permissions, computes region offsets/sizes from flash descriptor records, creates MTD partitions for readable regions, and registers the master MTD. Reads and writes find the containing region, clip to its end, resume PM, lock, issue aligned 32/64-bit register accesses with workarounds, set retlen, then autosuspend. Erase requires 4 KiB alignment, walks regions, and erases 4 KiB blocks.

State and persistence: persistent state is GPU NVM content and descriptor metadata. Runtime state includes access permissions, region geometry, non-posted erase mode, BAR mappings, runtime PM usage, mutex, and kref lifetime. `_get_device`/`_put_device` hold `nvm` while partition users are active.

Dependencies/integration: depends on `linux/intel_dg_nvm_aux.h`, auxiliary bus IDs `i915.nvm` and `xe.nvm`, MMIO accessors, `pm_runtime`, MTD partition registration, and optional second BAR for non-posted erase completion.

Risks: debug logging references `nvm->regions[idx]` before checking `idx >= nregions` in read/write, which is risky on out-of-range offsets. Cross-region requests are clipped for read/write but erase loops. Partial writes read-modify-write 32-bit words, so concurrent access must remain serialized. Hardware-specific 1 KiB boundary workaround is fragile.

Test signals: validate descriptor signature failure, unreadable/writable partition masks, runtime PM get failures, unaligned erase rejection, reads/writes around unaligned offsets and 1 KiB boundaries, non-posted erase timeout/fail_addr, remove while partitions are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/mtd_intel_dg.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/mtdram.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/mtdram.c

Purpose: synthetic RAM-backed MTD device mainly for testing MTD users. It allocates vmalloc memory, initializes it to erased state, and exposes it as `MTD_RAM`.

Important APIs/types/functions: module parameters `total_size`, `erase_size`, and `writebuf_size`; global `mtd_info`; callbacks `ram_erase()`, `ram_point()`, `ram_unpoint()`, `ram_read()`, `ram_write()`; reusable initializer `mtdram_init_device()`; lifecycle `init_mtdram()`/`cleanup_mtdram()`.

Control flow: module init validates nonzero size, allocates `mtd_info` and vmalloc storage, calls `mtdram_init_device()`, then fills storage with `0xff`. MTD callbacks directly `memcpy` or `memset` over `mtd->priv`. `ram_point()` can return virtual and optional physical address information, trimming retlen to contiguous physical vmalloc pages.

State and persistence: all data is volatile vmalloc memory. The only module-global state is the single supported `mtd_info` pointer. Erase state is represented by bytes set to `0xff`.

Dependencies/integration: uses vmalloc, `vmalloc_to_pfn()` for physical point support, MTD registration, and configuration defaults from `CONFIG_MTDRAM_TOTAL_SIZE` and `CONFIG_MTDRAM_ERASE_SIZE`.

Risks: callbacks rely on MTD core range validation; only one device is supported; total/erase sizes are module parameters in KiB but writebuf size is bytes; physical contiguity from vmalloc is limited and carefully clipped.

Test signals: load with valid/invalid sizes, verify `/proc/mtd` registration, erase alignment failures through `check_offs_len()`, read/write round trips, `mtd_point()` behavior across non-contiguous vmalloc pages, and cleanup freeing storage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/mtdram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/phram.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/phram.c

Purpose: maps physical RAM or reserved-memory/platform regions as MTD RAM devices. It supports module/built-in `phram=` parameters and OF platform devices compatible with `phram`.

Important APIs/types/functions: `struct phram_mtd_list` embeds `mtd_info`, list node, and cached mapping flag. MTD callbacks are `phram_erase()`, `phram_point()`, `phram_read()`, and `phram_write()`. Mapping/lifecycle helpers are `phram_map()`, `phram_unmap()`, `register_device()`, `unregister_devices()`, `phram_setup()`, `phram_param_call()`, `phram_probe()`, and `phram_remove()`.

Control flow: init first enforces `security_locked_down(LOCKDOWN_DEV_MEM)`, registers a platform driver, and for built-in mode parses deferred boot parameters. Parameter parsing accepts `<name>,<start>,<length>[,<erasesize>]`, supports `ki/Mi/Gi`, validates lengths and erase alignment, maps the region, and registers an `MTD_RAM`. OF probe maps the first memory resource and names the MTD from OF label via `mtd_set_of_node()`.

State and persistence: data persists only as long as the mapped physical RAM contents persist. Runtime state is either a global list for parameter-created devices or platform driver data for OF devices. `cached` controls `memremap(MEMREMAP_WB)` versus `ioremap()` and corresponding unmap path.

Dependencies/integration: uses MTD core, platform bus, OF address resources, security lockdown, `memremap`/`ioremap`, and module parameter callback semantics.

Risks: exposing arbitrary physical memory is high impact, hence lockdown gating. The global list is not explicitly protected against concurrent parameter writes. Platform devices pass `NULL` name and depend on OF labels. Incorrect cached/no-map policy can cause cacheability hazards.

Test signals: module parameter parsing with decimal/hex/unit suffixes, too-long names/parameters, erase-size divisibility checks, lockdown rejection, OF `no-map` versus cached mappings, read/write/erase behavior, and cleanup of both parameter and platform devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/phram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/pmc551.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/pmc551.c

Purpose: MTD driver for PMC-Sierra/related PMC551 PCI battery-backed SRAM/NVRAM boards. It exposes board memory as `MTD_RAM` while handling PCI BAR windows and optional aperture bank switching.

Important APIs/types/functions: `struct mypriv` stores PCI device, window aperture, base mapping, size, and MTD list linkage. MTD callbacks are `pmc551_point()`, `pmc551_unpoint()`, `pmc551_read()`, `pmc551_write()`, and `pmc551_erase()`. Hardware setup is in `fixup_pmc551()` and module lifecycle in `init_pmc551()`/`cleanup_pmc551()`. Module params `msize` and `asize` override detected memory/aperture sizes.

Control flow: init scans PCI devices, enables supported boards, requests PCI regions, maps control/aperture resources, validates and possibly fixes board configuration, constructs an MTD per board, and links it into `pmc551list`. Reads/writes either directly access mapped memory or switch aperture windows to cover the requested offset. Erase fills the target range with `0xff`.

State and persistence: user data persists in board SRAM/NVRAM depending on hardware battery backing. Runtime state tracks PCI resources, ioremapped apertures, selected window, MTD list, and board geometry.

Dependencies/integration: PCI core, MTD core, I/O memory accessors, module parameters, and board-specific registers. It is independent of higher-level filesystems but supplies a normal MTD device for them.

Risks: aperture switching is error-prone for unaligned or cross-window operations; direct memory operations rely on correct resource sizing; PCI resource cleanup must match each partial init path. Hardware age means limited modern coverage and platform availability.

Test signals: PCI probe with default and override sizes, direct versus bank-switched aperture access, cross-aperture reads/writes, erase alignment and content checks, multiple-card list cleanup, and forced init failures after each resource allocation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/pmc551.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/powernv_flash.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/powernv_flash.c

Purpose: exposes PowerNV OPAL PNOR flash as a Linux MTD NOR device. Actual flash access is delegated to firmware OPAL async calls.

Important APIs/types/functions: `struct powernv_flash` embeds `mtd_info` and OPAL flash id. `enum flash_op` selects read/write/erase. `powernv_flash_async_op()` is the shared operation engine. MTD callbacks are `powernv_flash_read()`, `powernv_flash_write()`, and `powernv_flash_erase()`. Probe helpers are `powernv_flash_set_driver_info()` and `powernv_flash_probe()`.

Control flow: probe allocates state, reads `ibm,opal-id`, reads erase size and total size from OF properties, fills MTD callbacks/geometry/name, and registers the device. Each operation obtains an OPAL async token, starts the requested firmware operation with physical buffer address when needed, waits for completion if OPAL reports async completion, maps OPAL result codes to errno, updates retlen on success, and releases the token.

State and persistence: persistent state is platform PNOR content managed by firmware. Runtime state is minimal: OPAL id and registered MTD. OPAL owns flash serialization and may return busy if service processor or firmware activity conflicts.

Dependencies/integration: PowerNV OPAL API, OF properties `ibm,opal-id`, `ibm,flash-block-size`, and `reg`, MTD core, and platform bus matching `ibm,opal-flash`.

Risks: interruptible wait handling is subtle: if interrupted, the driver must still wait for OPAL completion so the MTD buffer is not freed while firmware is using it. `OPAL_BUSY` is intentionally surfaced so userspace can notice possible flash changes. Buffers passed to OPAL must be physically addressable.

Test signals: OF property absence, OPAL token failure including interrupt conversion, successful async read/write retlen, erase failure setting `fail_addr`, OPAL_BUSY propagation, and unregister on platform remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/powernv_flash.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/serial_flash_cmds.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/serial_flash_cmds.h

Purpose: small shared header defining serial flash opcodes and feature flags used by legacy serial flash controller drivers, notably `st_spi_fsm.c`.

Important APIs/types/functions: command definitions include volatile configuration register opcodes `SPINOR_OP_WRVCR`/`SPINOR_OP_RDVCR` and several JEDEC/SFDP page-program opcodes for single, dual, and quad I/O widths. Feature masks group capabilities into single, dual, and quad read/write flags plus erase/chip erase, 32-bit address, reset, and DYB locking flags.

Control flow: no executable flow. Drivers use the flags to choose preferred command sequences by testing whether a flash table entry supports a candidate read/write mode.

State and persistence: no state. The flags describe persistent hardware capabilities and supported command sets; they do not store runtime state.

Dependencies/integration: protected by `_MTD_SERIAL_FLASH_CMDS_H`. It intentionally complements standard `linux/mtd/spi-nor.h` command definitions with older driver-local capability flags.

Risks: capability bits are local conventions; mixing them with other SPI NOR capability schemes can misconfigure command widths. Some opcode names overlap vendor-specific meanings, so users must interpret them through the target chip table.

Test signals: compile coverage from consumers, especially sequence selection in `st_spi_fsm.c`, and table entries choosing expected commands for single/dual/quad modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/serial_flash_cmds.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/slram.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/slram.c

Purpose: maps contiguous system RAM excluded from normal kernel use into one or more uncached/cached MTD RAM devices. It is configured by `slram=` boot parameter or module `map=` array.

Important APIs/types/functions: `slram_priv_t` stores mapped start/end pointers; `slram_mtd_list_t` links allocated MTDs. MTD callbacks are `slram_erase()`, `slram_point()`, `slram_read()`, and `slram_write()`. Setup helpers are `register_device()`, `unregister_devices()`, `handle_unit()`, `parse_cmdline()`, `mtd_slram_setup()`, and `init_slram()`.

Control flow: init parses triples of name/start/end-or-+length. `parse_cmdline()` handles decimal/hex plus K/M suffixes, converts an absolute end into length unless a `+length` form is used, validates `SLRAM_BLK_SZ` alignment, maps memory with `memremap()`, allocates MTD/private/list nodes, and registers the device. Cleanup unregisters all devices and unmaps memory.

State and persistence: contents are physical RAM and generally volatile. Runtime state is the global singly linked list of MTD devices plus each mapped range. Erase means setting bytes to `0xff`.

Dependencies/integration: module params or early boot `__setup`, `memremap(MEMREMAP_WB|WT|WC)`, MTD core, and command-line memory reservation by the user.

Risks: this older driver has partial allocation unwind gaps in `register_device()` if later allocation or `memremap()` fails. It exposes arbitrary physical ranges and assumes users avoided kernel/device memory conflicts. No locking protects the global list, but devices are normally created only at init.

Test signals: valid module and built-in command-line parsing, `+length` and absolute-end forms, unit suffixes, block-size alignment rejection, read/write/erase round trips, multi-device cleanup, and failure injection around allocation/mapping/register paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/slram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/spear_smi.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/spear_smi.c

Purpose: ST SPEAr Serial Memory Interface controller driver for attached serial NOR flashes. It replaces the normal SPI controller path with SMI hardware modes and registers one MTD per detected bank.

Important APIs/types/functions: `struct spear_smi` owns clock, registers, IRQ wait queue, controller lock, and bank pointers. `struct spear_snor_flash` owns per-bank MTD, lock, geometry, base memory window, erase command, and fast-mode flag. Key helpers are `spear_smi_read_sr()`, `spear_smi_wait_till_ready()`, `spear_smi_int_handler()`, `spear_smi_hw_init()`, `spear_smi_write_enable()`, `spear_smi_erase_sector()`, `spear_smi_probe_flash()`, and `spear_smi_setup_banks()`. MTD callbacks are `spear_mtd_read()`, `spear_mtd_write()`, and `spear_mtd_erase()`.

Control flow: platform probe obtains DT/platform data, IRQ, MMIO, clock, initializes hardware and wait queue, then probes each configured bank via RDID in software mode. A matched flash gets its memory window ioremapped, MTD geometry filled from the device table, and registered. Reads switch to hardware read mode and `memcpy_fromio()` from the bank window. Writes wait ready, issue write-enable, enable write-burst mode, then copy bytes/words to I/O memory respecting hardware write-size constraints. Erase loops sector commands.

State and persistence: flash contents are persistent NOR data. Runtime state includes controller register mode, last IRQ status, wait queue completions, per-bank locks, and MTD registrations. No filesystem or wear metadata is stored by the driver.

Dependencies/integration: platform bus, optional OF compatible `st,spear600-smi`, `linux/mtd/spear_smi.h` platform data, clocks, IRQs, I/O memory, MTD partitions, and NOR flash ID table.

Risks: DT parsing allocates one `board_flash_info` but iterates children as if multiple entries exist, which is a potential array/logic hazard. Many operations depend on interrupts and status bits with short timeouts. Write-burst mode requires uniform incremental access; the driver uses byte copies for unaligned cases to avoid mixed access sizes.

Test signals: probe with multiple banks, RDID failure, IRQ timeout paths, fast-mode reads, page-boundary writes, unaligned write-buffer paths, sector erase loops, suspend/resume clock reinitialization, and unregistering all banks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/spear_smi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/sst25l.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/sst25l.c

Purpose: SPI MTD NOR driver for SST25L flash chips using SST-specific status, erase, ID, and Auto Address Increment program commands.

Important APIs/types/functions: `struct sst25l_flash` stores SPI device, mutex, and embedded MTD. `struct flash_info` describes known device IDs and geometry. Helpers are `sst25l_status()`, `sst25l_write_enable()`, `sst25l_wait_till_ready()`, `sst25l_erase_sector()`, and `sst25l_match_device()`. MTD callbacks are `sst25l_erase()`, `sst25l_read()`, and `sst25l_write()`.

Control flow: probe reads ID with command `0x90`, matches two supported chips, allocates state, fills MTD NOR geometry, and registers optional platform partitions. Erase validates erase-size alignment, waits ready, then loops sectors with write-enable and sector-erase commands. Read sends opcode/address then receives data. Write requires `to` aligned to `writesize`, enables writes, uses `AAI_PROGRAM` with full address for the first byte of each page and 2-byte continuation writes for remaining bytes, then disables writes.

State and persistence: persistent state is NOR contents and protection bits. Runtime state is a per-device mutex and MTD geometry. `sst25l_write_enable()` also writes status register protection bits to enable or disable writes.

Dependencies/integration: SPI core, MTD partitions via `flash_platform_data`, jiffies timeout/`cond_resched`, and devm allocation.

Risks: `sst25l_read()` ignores the return value of `spi_sync()` after waiting ready and returns 0 even if transfer failed. `sst25l_write()` overwrites an earlier error with the return from write-disable in `out`, potentially masking failures. Supported chip table is very small.

Test signals: unknown ID rejection, write-enable status verification, 3-second busy timeout, erase alignment checks, AAI writes across page boundaries, transfer error injection for read/write, and remove unregister warning path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/sst25l.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/st_spi_fsm.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/devices/st_spi_fsm.c

Purpose: ST Fast Sequence Mode serial flash controller driver. It detects supported SPI NOR chips, synthesizes hardware FSM micro-sequences for read/write/erase/status operations, configures flash vendor features, and registers a NOR MTD.

Important APIs/types/functions: `struct stfsm_seq` is the packed register image for an FSM sequence; `struct stfsm` owns MMIO base, clock, MTD, lock, selected flash info, and prepared sequences; `struct seq_rw_config` and `struct flash_info` drive command selection. Core helpers include `stfsm_load_seq()`, `stfsm_wait_seq()`, `stfsm_read_fifo()`, `stfsm_clear_fifo()`, `stfsm_write_fifo()`, `stfsm_wait_busy()`, `stfsm_read_status()`, `stfsm_write_status()`, `stfsm_prepare_rw_seq()`, vendor config functions, and MTD callbacks `stfsm_mtd_read()`, `stfsm_mtd_write()`, `stfsm_mtd_erase()`.

Control flow: probe maps registers, enables clock, resets and configures the FSM, fetches boot/reset platform flags, probes JEDEC ID, marks >16 MiB parts as 32-bit address capable, runs vendor-specific configuration or defaults, fills MTD geometry, and registers. Read/write callbacks lock the controller and split transfers into 256-byte chunks/pages. Low-level transfers set sequence data size/address, handle FIFO alignment padding, start sequences, drain/fill FIFO, wait for completion, and optionally enter/exit 32-bit address mode around each operation. Erase chooses chip erase for full device or sector sequence loops.

State and persistence: persistent state is NOR data plus flash configuration bits such as QE, dummy-cycle VCR, DYB sector locks, and 32-bit address mode. Runtime state includes prepared sequences, controller mode/frequency, FIFO direction delay, boot-from-SPI reset policy, and status/error handling flags.

Dependencies/integration: platform driver compatible `st,spi-fsm`, MMIO registers, clocks, optional syscon/regmap boot-device data, OF properties `st,reset-signal` and `st,reset-por`, MTD/SPI-NOR command definitions, and local `serial_flash_cmds.h`.

Risks: reset safety is nuanced on boot-from-SPI systems; leaving a flash in 32-bit or quad mode across warm reset can break boot. `stfsm_write()` always returns 0 even when `stfsm_wait_busy()` reports errors, except for status clearing side effects. Several paths use `BUG_ON` for alignment/idleness rather than recoverable errors. Vendor DYB unlock loop and S25FL offset condition deserve scrutiny.

Test signals: JEDEC detection for each vendor family, selected read/write sequence versus flags, QE bit update, 32-bit address enter/exit under boot reset constraints, FIFO clearing with residual bytes, unaligned buffer/size reads and writes, S25FL error flags, chip erase and sector erase timeout paths, suspend/resume clock behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/devices/st_spi_fsm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ftl.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/ftl.c

Purpose: legacy Flash Translation Layer block translation driver for PCMCIA-style FTL-formatted MTD devices. It exposes a 512-byte-sector block device through `mtd_blktrans_ops`.

Important APIs/types/functions: `partition_t` stores the blktrans device, FTL header, virtual block map, erase-unit info, transfer-unit info, BAM cache, and counters. Discovery/build functions are `scan_header()` and `build_maps()`. Maintenance functions include `erase_xfer()`, `prepare_xfer()`, `copy_erase_unit()`, `reclaim_block()`, `find_free()`, and `set_bam_entry()`. Block callbacks are `ftl_readsect()`, `ftl_writesect()`, `ftl_discardsect()`, and `ftl_getgeo()`.

Control flow: when an MTD appears, `ftl_add_mtd()` scans the first MiB for an `FTL100` header, validates geometry against MTD erasesize, builds erase-unit and virtual-sector maps from headers/BAMs, then registers a blktrans device. Reads translate virtual sectors through `VirtualBlockMap` to erase-unit offsets or return zeroes for unmapped sectors. Writes reclaim space if needed, reserve a free BAM entry, write the data sector, mark old mappings deleted, then publish the new mapping. Reclaim chooses a prepared transfer unit, copies a selected erase unit into it, swaps metadata, and erases the old unit.

State and persistence: persistent on-flash state is the FTL header, per-erase-unit headers, BAM entries, erase counts, data sectors, deleted/free/control markers, and transfer units. Runtime state caches those maps and one BAM. `shuffle_freq` affects wear-leveling selection.

Dependencies/integration: MTD read/write/erase/sync APIs, MTD block translation framework, `linux/mtd/ftl.h` format macros, vmalloc/kmalloc, and 512-byte sector semantics.

Risks: legacy format has patent/licensing caveats for non-PCMCIA uses. Error handling often returns generic `-EIO` and may leave partially updated BAM state after power loss. Reclaim logic is complex and relies on correct transfer-unit preparation. `ftl_add_mtd()` leaks built maps if `add_mtd_blktrans_dev()` fails after successful build.

Test signals: formatted and corrupt header scans, erasesize mismatch, map build from representative BAM states, read unmapped sectors as zero, write update ordering, discard deleting mappings, reclaim under low free space, transfer erase failures, and blktrans add/remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/ftl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/Kconfig

Purpose: Kconfig menu for HyperBus/HyperFlash support and two controller drivers.

Important APIs/types/functions: `menuconfig MTD_HYPERBUS` enables the framework, depends on `HAS_IOMEM`, and selects CFI/map prerequisites. `config HBMC_AM654` enables TI AM65x HyperBus controller support, depends on `ARCH_K3 || COMPILE_TEST`, selects `MULTIPLEXER`, and implies `MUX_MMIO`. `config RPCIF_HYPERBUS` enables Renesas RPC-IF HyperBus support, depends on `RENESAS_RPCIF` and `MTD_CFI_BE_BYTE_SWAP`.

Control flow: build-time only. Enabling the menu exposes child controller options; child symbols compile their respective objects through the Makefile.

State and persistence: no runtime state. The symbols determine which code is built and which dependencies are forced into the kernel configuration.

Dependencies/integration: integrates HyperBus with MTD CFI AMD-standard probing and complex mappings. Controller configs ensure their platform helper frameworks are present.

Risks: incorrect dependencies can produce build failures or runtime-incomplete drivers. `RPCIF_HYPERBUS` specifically requires byte-swap CFI behavior, so testing on big/little endian mappings matters.

Test signals: `allmodconfig`/`COMPILE_TEST` builds, dependency visibility in menuconfig, and object inclusion for `MTD_HYPERBUS`, `HBMC_AM654`, and `RPCIF_HYPERBUS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/Makefile

Purpose: maps HyperBus Kconfig symbols to object files.

Important APIs/types/functions: builds `hyperbus-core.o` for `CONFIG_MTD_HYPERBUS`, `hbmc-am654.o` for `CONFIG_HBMC_AM654`, and `rpc-if.o` for `CONFIG_RPCIF_HYPERBUS`.

Control flow: build-system only. The core can be built independently when the framework is enabled; controller objects are included only for selected drivers.

State and persistence: no runtime state.

Dependencies/integration: consumed by Kbuild under `drivers/mtd/hyperbus`; must stay synchronized with Kconfig symbol names and source filenames.

Risks: stale symbol/object names silently omit driver code or break builds. Controller objects depend on the core export symbols, so configurations should include core when controllers are enabled through Kconfig nesting.

Test signals: compile each symbol as built-in and module where allowed; verify linked modules contain the expected platform drivers and exported core symbols resolve.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/hbmc-am654.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/hbmc-am654.c

Purpose: TI AM654 HyperBus Memory Controller adapter. It maps a child HyperFlash resource, optionally selects a mux, calibrates CFI access, accelerates large reads with DMA, and registers the device through the HyperBus core.

Important APIs/types/functions: `struct am654_hbmc_priv` embeds `hyperbus_ctlr`, `hyperbus_device`, and mux control. `struct am654_hbmc_device_priv` stores DMA completion, physical base, controller, and RX DMA channel. Operations are `am654_hbmc_calibrate()` and `am654_hbmc_read()` in `am654_hbmc_ops`; lifecycle is `am654_hbmc_probe()`/`am654_hbmc_remove()`.

Control flow: probe gets the first child DT node, translates its resource, optionally selects `mux-controls`, ioremaps the child memory window into `hbdev.map`, initializes controller ops, allocates private DMA state, requests a memcpy DMA channel, then calls `hyperbus_register_device()`. Reads use DMA for buffers that are not stack objects, are virt-address-valid, and have length at least 1 KiB; otherwise they fall back to `memcpy_fromio()`. Calibration sends CFI query commands until five consecutive query-present checks pass or attempts run out.

State and persistence: persistent state is HyperFlash contents. Runtime state is mux selection, mapped memory window, optional DMA channel, completion, and HyperBus/MTD registration.

Dependencies/integration: HyperBus core, MTD CFI helpers, DMA engine, mux consumer API, OF address parsing, platform bus compatible `ti,am654-hbmc`.

Risks: calibration returns the last `cfi_qry_present()` value and core treats zero as failure, so semantics must match CFI helper expectations. DMA timeout scales as `len + 1000` ms and may be excessive for large reads. DMA is skipped for stack or non-linear buffers.

Test signals: probe with/without mux, child resource parsing, DMA channel defer/unavailable paths, DMA success/fallback/timeout, calibration success/failure, HyperBus registration failure cleanup, and remove releasing DMA/mux/node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/hbmc-am654.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/hyperbus-core.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/hyperbus-core.c

Purpose: common HyperBus-to-MTD framework. It adapts controller-specific HyperBus operations to the MTD map/CFI layer and registers HyperFlash devices.

Important APIs/types/functions: map callbacks `hyperbus_read16()`, `hyperbus_write16()`, `hyperbus_copy_from()`, and `hyperbus_copy_to()` dispatch through `hyperbus_ctlr.ops`. Public exports are `hyperbus_register_device()` and `hyperbus_unregister_device()`.

Control flow: registration validates `hbdev`, child node, controller, and controller device; requires compatible `cypress,hyperflash`; initializes `map_info` with bankwidth 2 and OF node; installs map callbacks for provided controller ops; optionally calibrates once per controller; probes CFI with `do_map_probe("cfi_probe")`; sets parent/OF node; and registers the resulting MTD. Unregister removes MTD and destroys the map.

State and persistence: core runtime state lives in caller-owned `hyperbus_device` and `hyperbus_ctlr`, including `ctlr->calibrated` and `hbdev->mtd`. Persistent data remains in HyperFlash.

Dependencies/integration: MTD map API, CFI probe stack selected by Kconfig, OF compatible validation, and exported symbols for controller modules.

Risks: the calibration condition logs "Calibration failed" when `ops->calibrate()` returns zero, implying controller calibrate callbacks must return nonzero on success; this inverted convention is easy to misuse. Missing controller ops can leave default simple-map accessors, so map fields must be valid.

Test signals: invalid argument rejection, missing compatible, controller with each subset of ops, calibration success/failure, CFI probe failure, MTD register failure cleanup, and unregister idempotence for absent `mtd`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/hyperbus-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/rpc-if.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/rpc-if.c

Purpose: Renesas RPC-IF HyperFlash adapter. It maps HyperBus operations onto the Renesas RPC-IF framework and registers the resulting HyperFlash through the HyperBus core.

Important APIs/types/functions: `struct rpcif_hyperbus` embeds `struct rpcif`, `hyperbus_ctlr`, and `hyperbus_device`. `rpcif_op_tmpl` encodes 8-bit DDR command/address/data defaults. Operation helpers are `rpcif_hb_prepare_read()`, `rpcif_hb_prepare_write()`, `rpcif_hb_read16()`, `rpcif_hb_write16()`, and `rpcif_hb_copy_from()`. Lifecycle is `rpcif_hb_probe()`/`rpcif_hb_remove()`.

Control flow: probe allocates state, initializes RPC-IF software state from the parent device, enables runtime PM, initializes hardware in HyperBus mode, fills HyperBus map size/virt from RPC-IF direct map, installs read/write/copy ops, grabs the first parent child node, and registers with HyperBus core. 16-bit accesses prepare a manual RPC-IF transfer and call `rpcif_manual_xfer()`. Bulk reads prepare a read op then use `rpcif_dirmap_read()`.

State and persistence: persistent state is HyperFlash contents. Runtime state is RPC-IF device configuration, runtime PM enablement, direct-map pointer/size, child OF node, and HyperBus MTD registration.

Dependencies/integration: Renesas RPC-IF API (`memory/renesas-rpc-if.h`), HyperBus core, platform device id `rpc-if-hyperflash`, parent OF layout, runtime PM, and MTD.

Risks: probe obtains a child OF node but remove does not release it with `of_node_put()`, unlike the AM654 driver. Write bulk `copy_to` is not provided, so map users only get 16-bit writes plus bulk reads. Runtime PM is enabled/disabled but individual operations rely on RPC-IF internals for active state.

Test signals: RPC-IF init/hw-init failure paths, manual 16-bit read/write correctness, dirmap reads across ranges, HyperBus registration failure cleanup, runtime PM enable/disable, and OF node reference accounting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/hyperbus/rpc-if.c -->
