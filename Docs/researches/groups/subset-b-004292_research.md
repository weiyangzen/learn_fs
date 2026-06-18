# Research: subset-b-004292

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/hisi504_nand.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/hisi504_nand.c

Purpose: this is the HiSilicon HINFC504 raw NAND controller driver. It exposes one legacy `nand_chip` backed by controller registers, a separate memory-mapped data window, interrupt-completed DMA for page/OOB movement, and a small set of hardware ECC configurations.

Important APIs, types, and functions: `struct hinfc_host` is the controller state, carrying the embedded `nand_chip`, register/data mappings, command/address cache, selected chip, coherent DMA buffer, completion, IRQ status, and version. Low-level helpers are `hinfc_read()`, `hinfc_write()`, `wait_controller_finished()`, and `hisi_nfc_dma_transfer()`. Legacy NAND callbacks include `hisi_nfc_cmdfunc()`, `hisi_nfc_select_chip()`, `hisi_nfc_read_byte()`, `hisi_nfc_write_buf()`, and `hisi_nfc_read_buf()`. ECC integration is in `hisi_nfc_ecc_probe()`, `hisi_nfc_attach_chip()`, `hisi_nand_read_page_hwecc()`, `hisi_nand_read_oob()`, and `hisi_nand_write_page_hwecc()`.

Control flow: probe allocates `hinfc_host`, maps the controller register resource and the SRAM-like buffer resource, initializes legacy NAND hooks, writes default HINFC504 configuration, enables DMA interrupts, requests the IRQ, scans up to four targets, and registers the MTD device. `hisi_nfc_cmdfunc()` translates legacy NAND commands into controller register sequences. Page reads/programs use cached address registers and `hisi_nfc_dma_transfer()`; simple status/read-ID commands use the mapped data window and `HINFC504_OP`. The IRQ handler records DMA/correctable/uncorrectable events, clears interrupt bits, and completes DMA waiters.

State and persistence: persistent driver state is the selected chip, current command, address cycle/value cache, DMA buffer/OOB DMA address, and accumulated `irq_status` for ECC accounting. Hardware state persists across operations in `HINFC504_CON`, timing, interrupt-enable, DMA, and cached read-address registers. Suspend polls controller/DMA activity; resume resets each target and restores timing width values.

Dependencies and integration points: the file depends on the raw NAND legacy callback path, MTD registration, DMA coherent allocation, platform IRQ/resources, OF compatible `hisilicon,504-nfc`, and optional hardware ECC selected by the NAND core. It uses `chip->legacy.dummy_controller.ops` only for `attach_chip`, not modern `exec_op`.

Risks: support is narrow: only 2 KiB pages and 1 KiB ECC steps are accepted, and the implemented hardware ECC path only supports strength 16. `hisi_nfc_attach_chip()` calls `hisi_nfc_ecc_probe()` without checking its return value, so invalid ECC setup can be missed. The OOB ECC layout reports ECC positions as unsupported, leaving only a tiny free region. DMA timeouts only log and do not reset the engine. Address caching and `irq_status` reuse are sensitive to command ordering.

Test signals: successful probe should show NAND scan/MTD registration for `hisilicon,504-nfc`. Exercise read-ID, status, erase, full-page read/write, OOB-only read, suspend/resume target reset, DMA interrupt completion, timeout logging, and ECC statistics for correctable and uncorrectable reads, especially 2 KiB page/strength-16 devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/hisi504_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/Kconfig

Purpose: this Kconfig file declares build-time options for the Ingenic JZ47xx NAND controller and its companion ECC/BCH engines.

Important APIs, types, and functions: the user-visible root symbol is `MTD_NAND_JZ4780`, a tristate driver option depending on `MIPS || COMPILE_TEST` and `JZ4780_NEMC`. Inside that option, `MTD_NAND_INGENIC_ECC` is a hidden bool selected by the three ECC engines. User-visible ECC engine modules are `MTD_NAND_JZ4740_ECC`, `MTD_NAND_JZ4725B_BCH`, and `MTD_NAND_JZ4780_BCH`.

Control flow: selecting `MTD_NAND_JZ4780` enables the Ingenic NAND controller menu region. Selecting any hardware ECC engine selects the common `MTD_NAND_INGENIC_ECC` helper so `ingenic_ecc.c` is linked into the controller object. The SoC-specific ECC choices remain independent tristates, allowing ECC providers to be built as modules such as `jz4740-ecc`, `jz4725b-bch`, or `jz4780-bch`.

State and persistence: there is no runtime state. The persistent effect is kernel configuration: whether the NEMC-backed NAND controller and each ECC provider are built in, built as modules, or absent.

Dependencies and integration points: this file integrates the Ingenic drivers with Kbuild and with the broader raw NAND menu. The controller option depends on the external memory controller support (`JZ4780_NEMC`) because `ingenic_nand_drv.c` asserts banks through that API.

Risks: the menu is nested under `MTD_NAND_JZ4780`, even though the driver also has compatibles for JZ4740 and JZ4725B. That naming can be misleading for older SoC users. Hardware ECC support must be selected separately from the NAND controller, so DTs requesting an `ecc-engine` can still probe-defer or fail if the matching ECC provider is missing.

Test signals: configuration tests should verify that each ECC symbol selects `MTD_NAND_INGENIC_ECC`, that module names match help text, and that `ingenic_nand.o` links with or without the common ECC helper according to selected symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/Makefile -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/Makefile

Purpose: this Makefile maps the Ingenic raw NAND Kconfig symbols to build products.

Important APIs, types, and functions: `obj-$(CONFIG_MTD_NAND_JZ4780) += ingenic_nand.o` builds the main controller object. `ingenic_nand-y` always includes `ingenic_nand_drv.o`, while `ingenic_nand-$(CONFIG_MTD_NAND_INGENIC_ECC)` conditionally folds in `ingenic_ecc.o`. The SoC ECC providers are separate module objects: `jz4740_ecc.o`, `jz4725b_bch.o`, and `jz4780_bch.o`.

Control flow: Kbuild creates a composite `ingenic_nand.o` for the controller. If hardware ECC support is enabled, the common ECC provider API is compiled into that composite. Each SoC ECC implementation is built according to its own tristate, which lets the ECC provider modules register separately and be resolved through DT phandles at runtime.

State and persistence: there is no runtime state. Build state is reflected in which object files are linked into the kernel or emitted as modules.

Dependencies and integration points: this file must stay consistent with `Kconfig` and with symbol usage in `ingenic_nand_drv.c`, `ingenic_ecc.c`, and the three provider files. The composite object arrangement matters because `ingenic_nand_drv.c` calls `of_ingenic_ecc_get()` through either real functions or header stubs.

Risks: if `CONFIG_MTD_NAND_INGENIC_ECC` is disabled but a board expects hardware ECC, the header stubs return `-ENODEV` and the NAND controller probe fails when it requires `ecc-engine`. If a SoC ECC module is not loaded early enough, `of_ingenic_ecc_get()` reports `-EPROBE_DEFER` until the provider probes.

Test signals: build tests should cover all built-in/module combinations: NAND without ECC helper, NAND with each ECC provider built in, and NAND with ECC providers as modules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/ingenic_ecc.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/ingenic_ecc.c

Purpose: this is the common Ingenic ECC provider layer used by the Ingenic NAND controller and the JZ4740/JZ4725B/JZ4780 ECC engine drivers. It abstracts SoC-specific ECC calculation/correction operations behind `struct ingenic_ecc_ops` and handles DT phandle lookup, clock lifetime, register mapping, and driver data setup.

Important APIs, types, and functions: exported entry points are `ingenic_ecc_calculate()`, `ingenic_ecc_correct()`, `of_ingenic_ecc_get()`, `ingenic_ecc_release()`, and `ingenic_ecc_probe()`. `ingenic_ecc_get()` resolves a provider `device_node` to a `platform_device`, verifies driver data is ready, enables the provider clock, and returns the `struct ingenic_ecc`.

Control flow: SoC ECC platform drivers use `ingenic_ecc_probe()` as their probe function or call it from a wrapper. That probe allocates the shared state, fetches match-data ops, maps the MMIO resource, disables the hardware, gets the clock, initializes the mutex, stores `dev`, and publishes drvdata. The NAND controller calls `of_ingenic_ecc_get()` against its node; the helper first checks `ecc-engine`, then deprecated `ingenic,bch-controller`, then enables the provider clock and returns it. Calculate/correct calls simply dispatch through the provider ops.

State and persistence: `struct ingenic_ecc` persists the device pointer, ops, base register mapping, clock handle, and mutex. Clock enable state is reference-like: get enables, release disables and drops the provider device reference. Per-operation mutable state belongs to provider-specific registers and is serialized by the provider mutex.

Dependencies and integration points: the file depends on OF platform lookup, common clock APIs, platform resources, module exports, and `ingenic_ecc.h`. It is linked into the main `ingenic_nand` object when `CONFIG_MTD_NAND_INGENIC_ECC` is enabled, while provider modules supply the actual ops via OF match data.

Risks: `clk_prepare_enable()` return value is ignored in `ingenic_ecc_get()`, so clock-enable failure would not be reported to the NAND controller. Provider lookup returns `-EPROBE_DEFER` until drvdata exists, so boot ordering affects NAND probe. There is no module reference acquisition around provider ops beyond `get_device()`, so provider unbind behavior depends on platform-driver lifetime expectations.

Test signals: useful tests are provider probe with valid/invalid match data, DT lookup through both `ecc-engine` and deprecated phandle names, clock enable/disable balance across NAND bind/remove, probe deferral when provider is absent, and provider calculation/correction dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/ingenic_ecc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/ingenic_ecc.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/ingenic_ecc.h

Purpose: this internal header defines the common interface between the Ingenic NAND controller, the shared ECC provider layer, and the SoC-specific ECC/BCH engines.

Important APIs, types, and functions: `struct ingenic_ecc_params` carries ECC step size, bytes, and strength. Public declarations include `ingenic_ecc_calculate()`, `ingenic_ecc_correct()`, `ingenic_ecc_release()`, `of_ingenic_ecc_get()`, and `ingenic_ecc_probe()` when `CONFIG_MTD_NAND_INGENIC_ECC` is enabled. Disabled-config stubs return `-ENODEV` or no-op. `struct ingenic_ecc_ops` defines provider callbacks, and `struct ingenic_ecc` stores device, ops, MMIO base, clock, and mutex.

Control flow: consumers include this header and treat ECC providers uniformly. When hardware ECC support is compiled out, calls compile but fail cleanly through stubs. When enabled, provider drivers initialize a `struct ingenic_ecc` through `ingenic_ecc_probe()` and expose ops to the NAND controller through the DT phandle lookup path.

State and persistence: the header itself has no runtime state, but it defines the persistent in-memory ECC provider state and the per-call parameter contract used by all three SoC engines.

Dependencies and integration points: the header depends on Linux error, mutex, type, and compiler definitions, plus forward declarations for clocks, devices, platform devices, and DT nodes. It is a local driver-internal ABI; changes must be coordinated across `ingenic_nand_drv.c`, `ingenic_ecc.c`, and the JZ ECC provider files.

Risks: the compile-out stubs make missing hardware ECC support look like a runtime `-ENODEV` rather than a build failure. The parameter structure is intentionally generic, so provider-specific limits must be enforced in provider reset/config code rather than in the common API. The include guard name contains `INTERNAL`, which accurately signals local use but does not prevent accidental wider inclusion.

Test signals: build coverage should include `CONFIG_MTD_NAND_INGENIC_ECC=y/m/n`. Runtime tests should validate that each provider honors the same size/bytes/strength contract and that disabled builds fail the NAND hardware-ECC path predictably.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/ingenic_ecc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/ingenic_nand_drv.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/ingenic_nand_drv.c

Purpose: this is the Ingenic JZ47xx NAND controller driver for NAND chips attached through the JZ4780 NEMC-style external memory controller. It provides raw NAND `exec_op` support, per-bank chip initialization, optional hardware ECC through an external ECC engine phandle, board/SoC-specific OOB layouts, and GPIO ready/write-protect integration.

Important APIs, types, and functions: `struct jz_soc_info` describes data/address/command offsets, OOB layout, and whether the SoC needs OOB-first reads. `struct ingenic_nfc` owns the shared controller, ECC provider, bank mappings, and chip list. `struct ingenic_nand` embeds each `nand_chip` and GPIO state. Key functions include `ingenic_nand_attach_chip()`, `ingenic_nand_exec_instr()`, `ingenic_nand_exec_op()`, `ingenic_nand_init_chip()`, `ingenic_nand_init_chips()`, probe/remove, and ECC callbacks `ingenic_nand_ecc_hwctl()`, `ingenic_nand_ecc_calculate()`, and `ingenic_nand_ecc_correct()`.

Control flow: probe gets the number of NEMC banks, allocates `ingenic_nfc`, selects SoC match data, resolves the ECC engine before scanning chips, initializes `nand_controller`, then walks each child node. Each child supplies a `reg` bank, has that bank configured as NAND through `jz4780_nemc_set_type()`, maps its resource, obtains optional `rb` and `wp` GPIOs, initializes `nand_chip`, scans one target, registers the MTD, and links it into the controller chip list. `exec_op` asserts the NEMC bank, writes command/address/data cycles to SoC-specific offsets, waits through GPIO or software ready polling, honors instruction delays, then deasserts the bank.

State and persistence: persistent state is the list of registered chips, per-bank MMIO base/bank number, the shared ECC provider reference, and each chip's GPIO descriptors and `reading` flag. Hardware state is mostly external NEMC bank assertion/type configuration and NAND bus writes.

Dependencies and integration points: this driver integrates with `linux/jz4780-nemc.h`, raw NAND `exec_op`, MTD registration, optional Ingenic ECC providers from `ingenic_ecc.c`, DT child nodes, and compatibles `ingenic,jz4740-nand`, `ingenic,jz4725b-nand`, and `ingenic,jz4780-nand`.

Risks: `of_ingenic_ecc_get()` returning `NULL` is treated as no ECC provider, but `ERR_PTR` aborts probe; boards using hardware ECC depend on the phandle and provider load order. Hardware ECC bytes are computed manually and must fit OOB minus marker space. The driver sets `NAND_NO_SUBPAGE_WRITE`, moves flash BBT markers outside OOB when needed, and has legacy `qi,lb60` OOB behavior that can affect interoperability with existing flash contents. Remove releases the ECC provider before unregistering chips, even though cleanup should no longer perform ECC operations.

Test signals: test all three compatibles, multiple child banks up to NEMC capacity, 8-bit and 16-bit bus data paths, `rb` GPIO and software wait-ready fallback, hardware ECC calculate/correct with each provider, software/no-ECC modes, OOB layouts including `qi,lb60`, flash BBT placement, and cleanup after partial chip initialization failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/ingenic_nand_drv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/jz4725b_bch.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/jz4725b_bch.c

Purpose: this is the Ingenic JZ4725B BCH hardware ECC provider. It implements the common `ingenic_ecc_ops` interface for JZ4725B BCH encode/decode registers and supports correction through BCH error-index registers.

Important APIs, types, and functions: provider ops are `jz4725b_bch_disable()`, `jz4725b_calculate()`, and `jz4725b_correct()`. Helpers include `jz4725b_bch_config_set()`, `jz4725b_bch_config_clear()`, `jz4725b_bch_reset()`, `jz4725b_bch_write_data()`, `jz4725b_bch_read_parity()`, and `jz4725b_bch_wait_complete()`.

Control flow: calculate locks the shared ECC mutex, resets/configures BCH for encoding, streams the data step into `BCH_BHDR`, polls for `BCH_BHINT_ENCF`, reads parity bytes from `BCH_BHPAR0`, disables hardware, and unlocks. Correct resets/configures for decoding, streams data then stored ECC, polls for `BCH_BHINT_DECF`, handles all-0/all-FF, uncorrectable, or correctable status, reads error indexes from `BCH_BHERR0`, flips affected bits in the data buffer, disables hardware, and unlocks.

State and persistence: per-operation state lives in BCH control/count/interrupt/error registers and is serialized by `bch->lock`. `jz4725b_bch_reset()` clears interrupt status, enables BCH, selects 4-bit or 8-bit mode with `BCH_BHCR_BSEL`, sets encode/decode mode, initializes the engine, and writes encode/decode counts.

Dependencies and integration points: this file is a platform driver matched by `ingenic,jz4725b-bch`; its probe is the common `ingenic_ecc_probe()`. It depends on `iopoll`, MMIO accessors, and the shared Ingenic ECC header.

Risks: the reset path only distinguishes strength 8 versus all other strengths, so unsupported strengths can be misprogrammed unless constrained by the NAND controller. Parameter size and size-plus-ECC byte limits are checked against register masks, but bit indexes returned by hardware are trusted when flipping `buf[bit >> 3]`. Polling timeout is fixed at 100 ms. All-0/all-FF handling suppresses correction but depends on hardware status bits.

Test signals: validate ECC generation for 4-bit and 8-bit configurations, correctable multi-bit data flips, uncorrectable pages returning `-EBADMSG`, size-limit rejection, timeout handling, all-FF erased pages, and mutual exclusion under concurrent MTD activity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/jz4725b_bch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/jz4740_ecc.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/jz4740_ecc.c

Purpose: this is the Ingenic JZ4740 Reed-Solomon ECC provider. It implements the common Ingenic ECC ops for the older JZ4740 NAND ECC block, including special erased-page ECC handling.

Important APIs, types, and functions: key functions are `jz4740_ecc_reset()`, `jz4740_ecc_calculate()`, `jz_nand_correct_data()`, `jz4740_ecc_correct()`, and `jz4740_ecc_disable()`. The provider registers `jz4740_ecc_ops` through compatible `ingenic,jz4740-ecc`. `empty_block_ecc` encodes the hardware parity pattern produced for all-0xff data.

Control flow: calculate resets the ECC block in encoding mode, polls `JZ_NAND_STATUS_ENC_FINISH`, disables the block, reads parity bytes from the parity registers, and rewrites the known all-FF parity pattern to 0xff bytes for subpage-write compatibility. Correct resets in decode mode, writes the read ECC bytes to parity registers, marks parity ready, polls decode finish, disables the block, returns `-EBADMSG` for uncorrectable status, or reads error records and applies `jz_nand_correct_data()` for in-range data errors.

State and persistence: the driver uses only hardware register state and the common provider state from `ingenic_ecc`. Unlike the BCH providers, calculate/correct do not explicitly lock `ecc->lock`; serialization is therefore provided only by higher layers and the NAND request path, not by this file.

Dependencies and integration points: the file depends on the common Ingenic ECC API, platform OF matching, MMIO accessors, and raw NAND ECC callback flow through `ingenic_nand_drv.c`.

Risks: polling loops use a hard-coded iteration count of 1000 without delay, so timeout behavior is CPU-speed dependent. Lack of local mutex locking differs from the JZ4725B/JZ4780 BCH providers. `jz_nand_correct_data()` rewrites a 9-bit span around an index and must match the hardware error encoding exactly. The provider assumes the caller has selected 9 ECC bytes for JZ4740 strength-4 operation.

Test signals: verify ECC bytes for normal and all-FF buffers, single and multiple correctable bit errors, uncorrectable error reporting, decode timeout behavior, and integration with the JZ4740 NAND path using OOB-first hardware-ECC page reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/jz4740_ecc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/jz4780_bch.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/jz4780_bch.c

Purpose: this is the Ingenic JZ4780 BCH hardware ECC provider for the common Ingenic ECC API. It supports configurable BCH strength, parity byte count, a fixed 200 MHz ECC clock target, and hardware-reported bitmask/index corrections.

Important APIs, types, and functions: provider operations are `jz4780_bch_disable()`, `jz4780_calculate()`, and `jz4780_correct()`. Helpers include `jz4780_bch_reset()`, `jz4780_bch_write_data()`, `jz4780_bch_read_parity()`, `jz4780_bch_wait_complete()`, and probe wrapper `jz4780_bch_probe()`.

Control flow: probe calls `ingenic_ecc_probe()` then sets the ECC clock to `BCH_CLK_RATE`. Calculate locks the ECC mutex, resets for encoding with size/parity/strength fields, writes data to `BCH_BHDR`, polls for `BCH_BHINT_ENCF`, reads parity bytes, disables the block, and unlocks. Correct locks, resets for decode, writes data and stored ECC, polls `BCH_BHINT_DECF`, handles uncorrectable status, and for correctable errors reads each `BCH_BHERR` entry, using its 16-bit mask and index to XOR two data bytes per reported location.

State and persistence: persistent state is inherited from `struct ingenic_ecc`. Operation state is in BCH count, control, interrupt, parity, and error registers. The mutex serializes all encode/decode use. The provider leaves the clock rate request in effect after probe.

Dependencies and integration points: the file registers a platform driver for `ingenic,jz4780-bch`, uses `clk_set_rate()`, `readl_poll_timeout()`, and feeds the shared `ingenic_ecc_ops` contract consumed by `ingenic_nand_drv.c`.

Risks: reset writes `params->strength` directly into the BSEL field without local range validation. Correct uses hardware indexes to XOR `buf[(index * 2)]` and the next byte, so bad hardware status or mismatched step size can corrupt memory. `clk_set_rate()` return value is ignored. Timeout is fixed at 100 ms and interrupts are polled rather than used.

Test signals: validate probe clock programming, ECC generation for expected JZ4780 NAND strengths, corrected bit-count returns, uncorrectable `-EBADMSG`, timeout paths, erased-page reads, and concurrent access serialization through the shared mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/ingenic/jz4780_bch.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/intel-nand-controller.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/intel-nand-controller.c

Purpose: this is the Intel LGM External Bus Unit NAND controller driver. It combines a low-speed EBU command/address/data path with a high-speed NAND engine and DMA channels for hardware-ECC page reads/writes.

Important APIs, types, and functions: `struct ebu_nand_controller` owns the embedded `nand_controller`, single `nand_chip`, EBU/HSNAND register mappings, TX/RX DMA channels, completion, clock, chip-select data, and `nd_para0` ECC/page geometry register value. Key functions include `ebu_nand_set_timings()`, `ebu_nand_exec_op()`, `ebu_dma_start()`, `ebu_nand_trigger()`, `ebu_nand_read_page_hwecc()`, `ebu_nand_write_page_hwecc()`, `ebu_nand_attach_chip()`, and probe/remove.

Control flow: probe maps named resources `ebunand`, `hsnand`, `nand_csN`, and `addr_selN`, reads the child node's chip select, enables the clock, requests TX/RX DMA channels, programs address selection, attaches the child node to the NAND chip, initializes controller ops, scans one target, and registers MTD. Generic operations are handled by `exec_op()`, which selects the chip in `EBU_CON` and writes command/address/data bytes through memory offsets. Hardware-ECC page operations call `ebu_nand_trigger()`, perform DMA over the full page data area, optionally read/write the first 8 OOB bytes through message registers, clear the GO bit, and return.

State and persistence: persistent state includes active chip select, EBU address-selection register value, DMA channels, `nd_para0` computed during attach, and EBU bus timings. Runtime operation state lives in HSNAND CTL/CTL1/CTL2/PARA/CMSG/interrupt registers and DMA completion state.

Dependencies and integration points: the driver depends on raw NAND `exec_op`, `setup_interface`, hardware ECC callbacks, DMAengine, platform named resources, clocks, OF compatible `intel,lgm-ebunand`, and MTD OOB layout APIs. It requires an MTD label from the child node.

Risks: `ebu_dma_start()` maps buffers with the DMA channel device but unmaps with `ebu_host->dev`, which may be a different device. The successful DMA path returns without unmapping the buffer, which is a DMA mapping leak. `WAITRDY` multiplies timeout milliseconds by 1000 and passes that to a helper named in milliseconds but implemented as a microsecond poll timeout. Hardware ECC has limited page/block geometry encodings and rejects unsupported OOB capacity. The write-complete poll waits for `!(val & WR_C)`, which is easy to misread against the interrupt-status semantics.

Test signals: exercise ONFI identification via `exec_op`, SDR timing setup writes, supported 512/1024-byte ECC sizes and strengths, DMA read/write completion and timeout cleanup, OOB message register handling, MTD label validation, resource-name validation, and removal cleanup including DMA channel release and EBU disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/intel-nand-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/internals.h -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/internals.h

Purpose: this header defines raw NAND core-internal declarations and helper wrappers. It is explicitly for core raw NAND files, not controller drivers.

Important APIs, types, and functions: it lists manufacturer IDs, `struct nand_manufacturer_ops`, `struct nand_manufacturer_desc`, external manufacturer operation tables, `nand_flash_ids[]`, the `dist3_pairing_scheme`, and raw NAND core functions for manufacturer lookup, bad-block management, erase, ONFI/Jedec detection, timing selection, feature access, raw-page unsupported stubs, parameter page reads, ID decoding, panic wait, and string sanitization. Inline helpers include `nand_has_exec_op()`, `nand_check_op()`, `nand_exec_op()`, and `nand_controller_can_setup_interface()`.

Control flow: core code includes this header to dispatch optional controller operations and to share non-public core entry points. `nand_check_op()` calls a controller's `exec_op(..., true)` when present. `nand_exec_op()` validates target index and calls `exec_op(..., false)`, returning `-ENOTSUPP` when no modern operation hook exists. `nand_controller_can_setup_interface()` gates interface setup on the controller op being present and `NAND_KEEP_TIMINGS` being absent.

State and persistence: the header does not allocate state, but it defines global raw NAND registries and core contracts. Manufacturer ops may initialize per-chip vendor state and later clean it up; BBT and pairing declarations point at persistent core behavior implemented elsewhere.

Dependencies and integration points: the only include is `<linux/mtd/rawnand.h>`. Integration points span the raw NAND manufacturer database, ONFI/JEDEC parsers, controller operation model, bad-block table implementation, and timing negotiation.

Risks: because this is internal ABI, changing function signatures or helper semantics can break many raw NAND core files at once. `nand_exec_op()` uses `WARN_ON()` for out-of-range chip select, so invalid callers produce noisy kernel warnings. Controller drivers should not include this header, and doing so would couple them to unstable core internals.

Test signals: relevant coverage is raw NAND core build coverage, manufacturer detection for listed vendors, ONFI/JEDEC detection, invalid chip-select warning behavior, fallback behavior for legacy controllers without `exec_op`, and setup-interface gating when `NAND_KEEP_TIMINGS` is set.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/internals.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/loongson-nand-controller.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/loongson-nand-controller.c

Purpose: this is the Loongson family raw NAND controller driver. It implements modern `exec_op` through a controller-specific operation parser, DMA-backed data transfers, regmap-based register programming, SoC-specific address packing, and limited software/no-ECC operation.

Important APIs, types, and functions: `struct loongson_nand_op` is the parsed operation form; `struct loongson_nand_data` holds SoC capabilities and callbacks; `struct loongson_nand_host` owns the NAND chip/controller, regmap, MMIO base, DMA base/channel, completion, and SoC data. Key functions include `loongson_nand_parse_instructions()`, `loongson_nand_op_cmd_mapping()`, `ls1b_nand_set_addr()`, `ls1c_nand_set_addr()`, `loongson_nand_trigger_op()`, `loongson_nand_dma_transfer()`, parser exec handlers, `loongson_nand_check_op()`, `loongson_nand_attach_chip()`, controller/chip init, and probe/remove.

Control flow: probe selects match data, maps controller registers and a named `nand-dma` resource, maps the DMA resource for device access, initializes regmap/timing/ID-cycle/CS-RDY map/DMA routing, requests an `rxtx` DMA channel, then initializes exactly one child NAND chip. `exec_op(check_only)` validates command patterns; real execution goes through `nand_op_parser_exec_op()`. Data operations are parsed, addresses are packed into register fields, command scope/length are written, the operation is triggered, data moves by DMA, and optional ready completion is polled. Read-ID and status operations read dedicated ID/status registers after triggering.

State and persistence: persistent state includes SoC match data, `addr_cs_field` derived from detected capacity, DMA channel/cookie/completion, mapped DMA target address, timing register values, and controller cell-size configuration. Per-operation state is transient in `loongson_nand_op`, but command/address/parameter registers persist until overwritten.

Dependencies and integration points: the driver depends on raw NAND `exec_op`, the NAND op parser, DMAengine, regmap MMIO, OF child nodes, named resources, and compatibles for `loongson,ls1b-nand-controller`, `ls1c`, `ls2k0500`, and `ls2k1000`. LS2K1000 also programs a named `dma-config` resource.

Risks: only one NAND chip is supported. Hardware ECC is rejected; only none or software ECC are allowed. `dma_map_resource()` is not unmapped on remove or probe failure. DMA completion is not reinitialized before every submitted transfer unless timeout recovery occurs, so stale completions can affect later transfers. Subpage writes are rejected, unaligned reads allocate a temporary coherent buffer, and unsupported page/chip-size combinations fail attach. Status bit extraction uses field masks that must match SoC data exactly.

Test signals: verify every compatible's ID-cycle, timing, address-packing, and DMA-mask behavior; supported capacity/page-size encodings; read-ID byte order; read-status field extraction; aligned and unaligned reads; subpage-write rejection; operation pattern validation; DMA timeout recovery; and clean failure when multiple child chips or missing MTD labels are present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/loongson-nand-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/lpc32xx_mlc.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/lpc32xx_mlc.c

Purpose: this is the NXP LPC32xx MLC NAND controller driver. It supports automatic hardware encode/decode for 512-byte subpages, controller/NAND-ready interrupts, optional PL080-style DMA, write-protect GPIO handling, fixed flash BBT placement, and DT-configured timing.

Important APIs, types, and functions: `struct lpc32xx_nand_cfg_mlc` stores DT timing fields. `struct lpc32xx_nand_host` stores the embedded `nand_chip`, platform data, clock, WP GPIO, MMIO base, IRQ, completions, DMA channel/config/buffers, and subpage count. Major functions are `lpc32xx_nand_setup()`, command/ready/wait helpers, `lpc32xx_xmit_dma()`, `lpc32xx_read_page()`, `lpc32xx_write_page_lowlevel()`, OOB read/write hooks, `lpc32xx_nand_attach_chip()`, probe/remove, and suspend/resume.

Control flow: probe maps registers, parses required `nxp,*` timing properties, gets optional WP GPIO, enables the clock, installs legacy command/ready/data addresses, resets and configures the MLC timing registers, optionally sets up DMA if global `use_dma` is enabled, requests the IRQ, scans one NAND target, and registers the MTD. Attach configures on-host ECC with 512-byte steps, strength 4, 10 ECC bytes, custom OOB layout, page/OOB callbacks, and subpage count. Reads issue a page read, start auto-decode for each subpage, wait for controller-ready, account ECC failures/corrections from `MLC_ISR`, and pull 512 data plus 16 OOB bytes from the controller buffer. Writes start auto-encode per subpage, push 512 data plus selected OOB bytes, wait ready, then finish program.

State and persistence: persistent state includes timing configuration, DMA buffers, completion objects, IRQ registration, WP GPIO state, clock state, and flash BBT absolute-page descriptors. Suspend enables write protect and disables the clock; resume reenables clock, reinitializes the controller, and disables write protect.

Dependencies and integration points: the driver uses legacy raw NAND callbacks, MTD partitions from platform/DT config, DMAengine fallback through `lpc32xx_mlc_platform_data`, IRQ completions, clock APIs, and compatible `nxp,lpc3220-mlc`.

Risks: DMA is controlled by a file-scope `use_dma` variable initialized to false and has no module parameter here. Some DMA waits ignore timeout return values. The driver assumes large-block, five-address-cycle MLC behavior and fixed 512-byte subpage ECC. `write_oob` is a no-op because automatic ECC conflicts with standalone OOB writes. Timing DT properties are mandatory and unchecked for division edge cases beyond nonzero.

Test signals: validate 2 KiB and 4 KiB page reads/writes, ECC failure/correction statistics, OOB layout per 16-byte subpage, IRQ completion for NAND/controller ready, suspend/resume WP and timing restore, probe failures for missing timings/WP/IRQ/DMA, and both FIFO and optional DMA transfer paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/lpc32xx_mlc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/lpc32xx_slc.c -->
## sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/lpc32xx_slc.c

Purpose: this is the NXP LPC32xx SLC NAND controller driver. It uses legacy raw NAND callbacks with DMA-assisted data transfers, hardware-generated Hamming ECC, syndrome/interleaved ECC placement, small-page-specific OOB/BBT layouts, timing from DT, and write-protect GPIO handling.

Important APIs, types, and functions: `struct lpc32xx_nand_cfg_slc` contains DT timing fields. `struct lpc32xx_nand_host` stores the NAND chip, platform data, clock, WP GPIO, MMIO/DMA addresses, completion, DMA channel/config/SG, and combined data/ECC work buffer. Key functions include `lpc32xx_nand_setup()`, command/ready/read/write byte/buffer hooks, `lpc32xx_slc_ecc_copy()`, `lpc32xx_xmit_dma()`, `lpc32xx_xfer()`, syndrome page read/write/raw hooks, OOB hooks, `lpc32xx_nand_attach_chip()`, probe/remove, and suspend/resume.

Control flow: probe maps registers, parses required `nxp,*` timing properties, gets optional WP GPIO and clock, installs legacy callbacks, resets/configures SLC timing, allocates a data/ECC work buffer, requests a DMA channel, scans one chip, and registers the MTD. Attach configures on-host ECC with 256-byte steps, strength 1, 3 ECC bytes, interleaved placement, hardware calculate no-op, software Hamming correction, and syndrome page callbacks. Page reads issue a read command, call `lpc32xx_xfer()` to DMA data while collecting hardware ECC words, read OOB through FIFO, convert hardware ECC words into stored OOB format, and correct each ECC step. Writes DMA data out with hardware ECC enabled, convert generated ECC into OOB bytes, write OOB, and finish program.

State and persistence: persistent state includes timing parameters, the DMA channel and SG config, work buffer split into data and ECC regions, clock and WP GPIO state, and custom small-page BBT descriptors. Suspend forces CE high, enables write protect, and disables the clock. Resume reenables the clock, reinitializes timing/control registers, and disables write protect.

Dependencies and integration points: the driver uses MTD/raw NAND legacy callbacks, DMAengine, clock APIs, optional platform DMA filter fallback, GPIO descriptors, DT compatible `nxp,lpc3220-slc`, and `rawnand_sw_hamming_correct` for correction.

Risks: the DMA path is mandatory after probe; no FIFO fallback exists for ECC page transfers if DMA setup fails. DMA wait timeouts are not checked in `lpc32xx_xmit_dma()`. Buffer sizing constants are capped at 4096-byte pages plus ECC storage. Hardware ECC is converted manually with bit inversion/shift assumptions. Small-page BBT and OOB layouts differ from large-page defaults and must match existing flash contents. Remove/suspend code appears to clear CE using `SLC_CTRL` with an `SLC_CFG` bit, which deserves hardware validation.

Test signals: test small and large page devices, OOB/ECC placement, BBT marker placement, read/write ECC correction and failure accounting, DMA timeout/FIFO-empty behavior, highmem-buffer bounce copying, suspend/resume clock/WP/CE behavior, and probe failures for missing DT timing or DMA resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/lpc32xx_slc.c -->
