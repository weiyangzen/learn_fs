# Research: subset-b-004289

Grouped research for NAND raw-controller sources under `sources/distributed-fs/ceph-client/drivers/mtd/nand/raw`. Each section is source-path aligned for deterministic reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/nand-controller.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/nand-controller.c

## Purpose
This is the Atmel/Microchip raw NAND controller driver. It supports older SMC-attached NAND controllers and newer HSMC/NFC controllers, including legacy Device Tree bindings. It bridges Linux raw NAND `exec_op`, MTD registration, SMC timing setup, optional DMA, ready/busy signaling, and the Atmel PMECC hardware ECC engine.

## Important APIs, Types, And Functions
Core state is split among `struct atmel_nand_controller`, `struct atmel_smc_nand_controller`, `struct atmel_hsmc_nand_controller`, `struct atmel_nand`, and per-chip-select `struct atmel_nand_cs`. Capability tables (`struct atmel_nand_controller_caps`) choose offsets, DMA support, legacy parsing, and controller operations.

The primary external integration is the platform driver `atmel_nand_controller_driver`. The NAND core callbacks are `atmel_nand_attach_chip`, `atmel_nand_setup_interface`, and `atmel_nand_exec_op`. SMC command execution uses `atmel_smc_nand_exec_op`; HSMC/NFC execution uses `atmel_hsmc_nand_exec_op` with `atmel_hsmc_op_parser`, `atmel_nfc_exec_op`, and `atmel_nfc_interrupt`. PMECC hooks are installed by `atmel_nand_ecc_init` and `atmel_hsmc_nand_ecc_init`, with read/write paths such as `atmel_nand_pmecc_read_pg`, `atmel_nand_pmecc_write_pg`, `atmel_hsmc_nand_pmecc_read_pg`, and `atmel_hsmc_nand_pmecc_write_pg`.

## Control Flow
Probe resolves a capability table from OF or platform id, upgrades legacy-compatible matches when legacy properties imply a different controller, and dispatches to SMC or HSMC probe. Common initialization obtains PMECC, optional DMA, MCK, and SMC regmaps. HSMC-specific probe additionally maps NFC IO/SRAM, requests IRQs, enables NFC, and adds NAND children.

Child NAND creation parses `reg`, ready/busy, chip-select, card-detect GPIOs, maps chip-select IO, then scans/registers MTD. Runtime NAND operations select a target CS, assert optional CS GPIO, and execute NAND instructions. HSMC controllers combine command/address cycles into NFC native operations and perform data movement through mapped IO or NFC SRAM.

## State And Persistence
Persistent runtime state includes active chip-select selection, cached HSMC NFC config (`nc->cfg`), per-CS SMC timing (`smcconf`), PMECC user state, DMA channel ownership, and registered MTD devices. Suspend/resume resets PMECC and resets every NAND target; it does not serialize flash data itself.

## Dependencies And Integration Points
The file depends on raw NAND/MTD APIs, GPIO descriptors, DMA engine, regmap/syscon, clocks, Atmel SMC/HSMC helpers, OF parsing, genalloc SRAM pools, and `pmecc.c` through `pmecc.h`. It integrates with Device Tree compatibles for AT91/SAMA5/SAM9x60 and supports old bindings for older boards.

## Risks And Test Signals
High-risk areas are timing calculation in `atmel_smc_nand_prepare_smcconf`, legacy binding compatibility, DMA fallback correctness, HSMC interrupt wait/error handling, native R/B use, and PMECC raw-vs-ECC paths. Useful tests are boot/probe on SMC and HSMC SoCs, `nand_scan` success, MTD read/write/erase, raw page/OOB reads, ECC correction and erased-page behavior, suspend/resume, DMA-disabled module parameter coverage, and DT variants with GPIO and native R/B.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/nand-controller.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/pmecc.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/pmecc.c

## Purpose
This file implements the Atmel PMECC hardware-assisted BCH ECC engine and PMERRLOC error-location helper. It exposes a reusable ECC engine object that NAND controller drivers obtain either from a standalone `ecc-engine` phandle or from legacy resources embedded in the NAND controller node.

## Important APIs, Types, And Functions
Private types include `struct atmel_pmecc`, `struct atmel_pmecc_caps`, `struct atmel_pmecc_user`, `struct atmel_pmecc_gf_tables`, and the user configuration cache. Exported APIs are `devm_atmel_pmecc_get`, `atmel_pmecc_create_user`, `atmel_pmecc_reset`, `atmel_pmecc_enable`, `atmel_pmecc_disable`, `atmel_pmecc_wait_rdy`, `atmel_pmecc_correct_sector`, `atmel_pmecc_correct_erased_chunks`, and `atmel_pmecc_get_generated_eccbytes`.

Key internal algorithms are `atmel_pmecc_build_gf_tables`, `atmel_pmecc_prepare_user_req`, `atmel_pmecc_gen_syndrome`, `atmel_pmecc_substitute`, `atmel_pmecc_get_sigma`, and `atmel_pmecc_err_location`. SoC capability tables define supported BCH strengths, errloc register offsets, erased-chunk policy, and clock control.

## Control Flow
Probe creates an engine from PMECC and PMERRLOC resources, optionally sets the PMECC clock register, disables interrupts, and resets the hardware. A NAND client creates a PMECC user request; the request is normalized to valid page/OOB/sector/strength parameters, shared Galois tables are allocated lazily, and per-user work arrays are allocated in one devm block.

At read/write time, the NAND controller enables PMECC under `pmecc->lock`, waits until hardware is ready, then either extracts generated ECC bytes or corrects each sector. Correction reads syndromes from PMECC remainder registers, computes BCH error locator polynomial in software, asks PMERRLOC to find roots, and flips bits in the data or ECC area.

## State And Persistence
Engine state persists in MMIO register mappings, a mutex, capability data, and lazily-created global GF lookup tables for 512B and 1024B sectors. Per-user state persists cached register values, ECC bytes per sector, and BCH scratch arrays. The lock serializes the single hardware engine across NAND users.

## Dependencies And Integration Points
The file depends on platform devices, OF lookup, MMIO, polling helpers, raw NAND constants, and the Atmel NAND controller. It exports symbols for the controller module and supports both standalone PMECC devices and legacy `atmel,has-pmecc` bindings.

## Risks And Test Signals
Risks include invalid ECC geometry acceptance, GF table allocation races, PMERRLOC timeout handling, root-degree mismatch returning `-EBADMSG`, bit-position bounds, and correct use of mutex lock/unlock around enable/disable. Test signals include BCH correction counts, uncorrectable ECC injection, erased-page fallback behavior on capable vs incapable SoCs, legacy and phandle acquisition paths, and timeout/error logging from PMECC/PMERRLOC polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/pmecc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/pmecc.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/pmecc.h

## Purpose
This header defines the public contract between the Atmel NAND controller and the PMECC engine implementation. It provides special auto-selection constants, the user request structure, opaque engine/user types, and exported function prototypes.

## Important APIs, Types, And Functions
`ATMEL_PMECC_MAXIMIZE_ECC_STRENGTH`, `ATMEL_PMECC_SECTOR_SIZE_AUTO`, and `ATMEL_PMECC_OOBOFFSET_AUTO` let callers request automatic geometry choices. `struct atmel_pmecc_user_req` carries page size, OOB size, target ECC strength/bytes/sector size, calculated sector count, and OOB offset. The function declarations expose engine acquisition, user creation, reset, enable/disable, ready wait, sector correction, erased-chunk policy, and generated ECC-byte retrieval.

## Control Flow
The header itself has no runtime control flow. A controller includes it, obtains `struct atmel_pmecc *` with `devm_atmel_pmecc_get`, creates a `struct atmel_pmecc_user`, then uses enable/wait/correct/generate/disable calls around page reads and writes.

## State And Persistence
The header intentionally keeps `struct atmel_pmecc` and `struct atmel_pmecc_user` opaque so state remains owned by `pmecc.c`. The request structure is mutable: `atmel_pmecc_create_user` normalizes `strength`, `bytes`, `sectorsize`, `nsectors`, and `ooboffset`.

## Dependencies And Integration Points
It depends on the including C file having kernel types such as `bool` and `struct device` available. Its direct integration point is `nand-controller.c`, but the exported API is module-visible for any Atmel PMECC client.

## Risks And Test Signals
The main risk is callers assuming request fields are input-only; the implementation writes back selected ECC geometry. Compile coverage must catch missing type includes, and runtime tests should validate auto constants, invalid geometry rejection, and raw NAND read/write paths that depend on this API.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/atmel/pmecc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/au1550nd.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/au1550nd.c

## Purpose
This is a board/platform glue driver for NAND flash on Alchemy Au1550/Pb1550-style systems. It maps the static-memory NAND window, detects the chip-select, implements raw NAND operations with command/address/data register offsets, and registers an MTD device using platform partition data.

## Important APIs, Types, And Functions
`struct au1550nd_ctx` owns a `nand_controller`, `nand_chip`, chip-select number, and mapped base. Buffer helpers `au_write_buf`, `au_read_buf`, `au_write_buf16`, and `au_read_buf16` perform byte/word PIO and drain write buffers with `wmb()`. `find_nand_cs` decodes static-memory controller registers. `au1550nd_exec_instr` and `au1550nd_exec_op` implement raw NAND `exec_op`; `au1550nd_attach_chip` defaults soft ECC to Hamming.

## Control Flow
Probe requires platform data, allocates context, claims and maps the memory resource, detects the NAND CS, initializes the NAND controller, configures 16-bit width from platform data, defaults to software ECC, scans one target, and registers MTD partitions. Runtime operation asserts chip enable through `AU1000_MEM_STNDCTL`, executes each instruction, then deasserts chip enable.

## State And Persistence
Persistent state is only the context, mapped IO base, CS number, and NAND/MTD registration. No flash metadata is cached. Remove unregisters MTD, cleans NAND state, unmaps IO, releases the memory region, and frees context.

## Dependencies And Integration Points
The driver depends on MIPS Alchemy headers, `struct au1550nd_platdata`, platform resources, raw NAND core, and platform partition registration. It is a platform driver named `au1550-nand`.

## Risks And Test Signals
Risks include the inverted-looking `request_mem_region` error check, platform-data dependency, static-memory CS decode assumptions, polling timeout in `au1550nd_waitrdy`, and PIO length handling on 16-bit buses. Test signals are probe on real board data, CS detection, 8/16-bit read/write/erase, soft-Hamming correction, partition registration, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/au1550nd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/Makefile

## Purpose
This Makefile builds the BCM47xx BCMA NAND flash driver object from its common probe file and BCM4706-specific operation implementation.

## Important APIs, Types, And Functions
`bcm47xxnflash-y` includes `main.o` and `ops_bcm4706.o`; `obj-$(CONFIG_MTD_NAND_BCM47XXNFLASH)` links the composite `bcm47xxnflash.o` when the Kconfig option is enabled.

## Control Flow
There is no runtime flow. Build-time control is standard kbuild composite-object aggregation, ensuring the platform driver in `main.c` and the operation initializer in `ops_bcm4706.c` are linked together.

## State And Persistence
No runtime state. Build state is controlled by `CONFIG_MTD_NAND_BCM47XXNFLASH`.

## Dependencies And Integration Points
It integrates with the kernel MTD NAND kbuild subtree and depends on the Kconfig symbol being selected elsewhere.

## Risks And Test Signals
The main risk is missing object inclusion if additional chip operation files are added later. Test signals are successful module/built-in compilation and symbol resolution for `bcm47xxnflash_ops_bcm4706_init`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/bcm47xxnflash.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/bcm47xxnflash.h

## Purpose
This header declares the private BCM47xx NAND driver state shared between the platform probe and BCM4706 operation file.

## Important APIs, Types, And Functions
`struct bcm47xxnflash` stores the BCMA ChipCommon pointer, embedded `nand_chip`, current legacy NAND command, page address, column, and cached ID bytes. It declares `bcm47xxnflash_ops_bcm4706_init`.

## Control Flow
The header has no control flow. `main.c` allocates and initializes the struct, then calls the BCM4706 initializer to install legacy NAND callbacks and scan the device.

## State And Persistence
The current command/page/column fields are persistent controller emulation state used by legacy callbacks in `ops_bcm4706.c`. `id_data[8]` caches READID output because the hardware requires a known number of chip-select asserted reads.

## Dependencies And Integration Points
It depends on BCMA structures via users including BCMA headers and on raw NAND/MTD types. It is internal to the `bcm47xxnflash` directory.

## Risks And Test Signals
Risks are stale command/column state and fixed ID cache length. Compile tests should ensure both C files agree on struct layout; runtime tests should exercise READID, STATUS, read, OOB, erase, and page program sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/bcm47xxnflash.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/main.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/main.c

## Purpose
This is the BCMA platform driver entry point for the older BCM47xx NAND flash path. It allocates driver state, selects the supported chip-specific operation implementation, registers the MTD device with BCM47xx partition probing, and cleans up on remove.

## Important APIs, Types, And Functions
The driver registers as platform driver `bcma_nflash`. `bcm47xxnflash_probe` consumes `struct bcma_nflash` platform data, stores the containing `bcma_drv_cc`, initializes BCM4706 operations through `bcm47xxnflash_ops_bcm4706_init`, and registers MTD with probe type `bcm47xxpart`. `bcm47xxnflash_remove` unregisters MTD and calls `nand_cleanup`.

## Control Flow
Probe allocates `struct bcm47xxnflash`, binds it to the embedded `nand_chip`, sets MTD parent, detects BCM4706 by BCMA chip id, runs operation initialization and `nand_scan` indirectly, stores driver data, then parses/registers partitions. Unsupported chips fail with `-ENOTSUPP`.

## State And Persistence
State is devm-managed driver-private memory and NAND core registration. Remove handles MTD/NAND teardown but leaves devm allocation to device lifetime.

## Dependencies And Integration Points
It depends on BCMA ChipCommon platform data, raw NAND core, MTD partition parser `bcm47xxpart`, and the BCM4706 operation implementation. This path explicitly excludes chips handled by the generic `brcmnand` BCMA glue.

## Risks And Test Signals
Risks include platform-data absence, only BCM4706 support, partition parser expectations, and error unwinding after `nand_scan` inside the initializer but before MTD registration. Test signals are platform probe, unsupported-chip rejection, partition discovery, MTD read/write/erase, and remove cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/ops_bcm4706.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/ops_bcm4706.c

## Purpose
This file implements BCM4706-specific NAND operations over BCMA ChipCommon NFLASH registers. It uses legacy raw NAND callbacks because the hardware command/address/data sequencing does not match the generic legacy command helpers.

## Important APIs, Types, And Functions
Important helpers are `bcm47xxnflash_ops_bcm4706_ctl_cmd`, `bcm47xxnflash_ops_bcm4706_poll`, `bcm47xxnflash_ops_bcm4706_read`, and `bcm47xxnflash_ops_bcm4706_write`. Legacy NAND callbacks include `cmd_ctrl`, `select_chip`, `dev_ready`, `cmdfunc`, `read_byte`, `read_buf`, and `write_buf`. `bcm47xxnflash_ops_bcm4706_init` installs callbacks, enables NAND access, programs wait counters, scans NAND, and configures controller geometry.

## Control Flow
The initializer enables NAND flash access in `BCMA_CC_4706_FLASHSCFG`, calculates wait counters from package option or PLL-derived clock, then calls `nand_scan`. After scan, it validates that flash size is a power of two, derives row/column address byte sizes, and writes `BCMA_CC_NFLASH_CONF`.

At runtime, `cmdfunc` records current column/page and performs special hardware sequences for RESET, READID, STATUS, READOOB, ERASE, SEQIN, and PAGEPROG. Data reads are chunked to 0x200 bytes, set row/column registers, start read commands, poll ready, and drain data words. Writes feed data words and issue write controls.

## State And Persistence
Persistent state lives in `struct bcm47xxnflash`: current command, page, column, and cached READID bytes. Hardware state includes wait counters, flash config, current row/column registers, and enabled NAND access. ECC is explicitly disabled (`NAND_ECC_ENGINE_TYPE_NONE`), and bad block table use is configured for flash.

## Dependencies And Integration Points
The file depends on BCMA ChipCommon register definitions, raw NAND legacy callbacks, `nand_scan`, and the shared header. It is linked by the local Makefile and called from `main.c`.

## Risks And Test Signals
Risks include word-aligned assumptions for buffers/lengths, unsupported commands, fixed retry loops without delay, no ECC implementation, nonstandard READID caching, and geometry derivation from chip size. Test signals include READID, STATUS, full page read/write, OOB reads, erase, page program polling, invalid command logging, and error path disabling `NF1` when scan/configuration fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/bcm47xxnflash/ops_bcm4706.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/Kconfig

## Purpose
This Kconfig file declares the Broadcom NAND controller core and the SoC glue driver options that adapt it to BCM63xx, BCMA, BCMBCA, BRCMSTB, and iProc platforms.

## Important APIs, Types, And Functions
`MTD_NAND_BRCMNAND` is the core tristate and depends on supported architectures or `COMPILE_TEST` plus `HAS_IOMEM`. Child symbols are `MTD_NAND_BRCMNAND_BCM63XX`, `MTD_NAND_BRCMNAND_BCMA`, `MTD_NAND_BRCMNAND_BCMBCA`, `MTD_NAND_BRCMNAND_BRCMSTB`, and `MTD_NAND_BRCMNAND_IPROC`.

## Control Flow
There is no runtime flow. Kconfig selection determines which platform glue objects are compiled and therefore which platform drivers can call the shared `brcmnand_probe`.

## State And Persistence
No runtime state. Build configuration persists in the kernel `.config`.

## Dependencies And Integration Points
The file integrates with MTD raw NAND configuration. BCMA glue depends on `BCMA_NFLASH` and `BCMA`; other glue drivers default to their platform architecture symbols.

## Risks And Test Signals
Risks are missing dependencies for compile-test coverage or incorrect defaults causing unavailable glue. Test signals are all relevant combinations building as modules and built-in, especially core-only and each glue plus core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/Makefile -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/Makefile

## Purpose
This Makefile links the Broadcom NAND core and platform glue drivers according to Kconfig selections.

## Important APIs, Types, And Functions
Objects are selected by `CONFIG_MTD_NAND_BRCMNAND_*` symbols. The comment notes link order matters: more specific drivers such as `iproc_nand.o` should precede more generic `brcmstb_nand.o`. The core `brcmnand.o` is built for `CONFIG_MTD_NAND_BRCMNAND`; BCMA glue is appended separately.

## Control Flow
No runtime control flow. Build order controls platform-driver registration order when multiple compatibles could overlap.

## State And Persistence
No runtime state. Build output persistence is the generated object/module set.

## Dependencies And Integration Points
It integrates with the brcmnand Kconfig file and the MTD raw NAND kbuild tree.

## Risks And Test Signals
Risks include registration-order regressions and unresolved symbols if glue is built without the core. Test signals are build coverage for each symbol combination and module load order on platforms with multiple matching drivers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcm6368_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcm6368_nand.c

## Purpose
This is the BCM6368 MIPS DSL platform glue for the shared Broadcom NAND controller. It supplies interrupt acknowledge and enable operations through a platform-specific NAND interrupt register block.

## Important APIs, Types, And Functions
`struct bcm6368_nand_soc` embeds `struct brcmnand_soc` and stores the interrupt MMIO base. `bcm6368_nand_intc_ack` checks and acknowledges `BCM6368_CTRL_READY`; `bcm6368_nand_intc_set` enables or disables that interrupt source. `bcm6368_nand_probe` maps `nand-int-base`, initializes hooks, clears/acks interrupts, and calls `brcmnand_probe`.

## Control Flow
Probe allocates glue state, maps the named interrupt resource, assigns `ctlrdy_ack` and `ctlrdy_set_enabled`, disables and acknowledges all interrupts, then delegates full controller setup to the core. Remove and PM use shared `brcmnand_remove` and `brcmnand_pm_ops`.

## State And Persistence
The glue persists only the interrupt base mapping and hook table. Hardware interrupt enable/status bits persist in the SoC register until changed.

## Dependencies And Integration Points
It depends on OF compatible `brcm,nand-bcm6368`, platform resource `nand-int-base`, and the exported brcmnand core API.

## Risks And Test Signals
Risks include status/enable bitfield mistakes, wrong acknowledge semantics, missing named resource, and interrupt storms if status bits are mishandled. Test signals include probe, controller-ready IRQ completion, fallback polling behavior if IRQ fails, suspend/resume interrupt re-enable, and MTD read/write/erase.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcm6368_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcma_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcma_nand.c

## Purpose
This file adapts the shared Broadcom NAND controller core to BCMA ChipCommon NAND blocks on chips other than BCM4706. It provides non-MMIO register access callbacks and cache-address preparation required by BCMA.

## Important APIs, Types, And Functions
`struct brcmnand_bcma_soc` embeds `brcmnand_soc` and stores `struct bcma_drv_cc *`. `brcmnand_bcma_read_reg` and `brcmnand_bcma_write_reg` translate brcmnand offsets to BCMA ChipCommon offsets and swap selected register values. `brcmnand_bcma_prepare_data_bus` resets the NAND cache address before data access. `brcmnand_bcma_nand_probe` wires hooks and calls `brcmnand_probe`.

## Control Flow
Probe retrieves `struct bcma_nflash` platform data, obtains its containing ChipCommon driver, rejects BCM4706 in favor of `bcm47xxnflash`, installs custom IO ops and data-bus preparation, then delegates setup to the brcmnand core. The core later uses a static key for non-MMIO ops when these callbacks are present.

## State And Persistence
Persistent state is the ChipCommon pointer and hook table. The prepare hook resets `BCMA_CC_NAND_CACHE_ADDR`, affecting hardware cache state before sub-page transfers.

## Dependencies And Integration Points
It depends on BCMA, `BCMA_NFLASH`, ChipCommon register definitions, and brcmnand exported APIs. It registers platform driver `bcma_brcmnand`.

## Risks And Test Signals
Risks include register-offset translation errors, incorrect endian swapping for spare/devid registers, accidental BCM4706 binding, and cache address not reset before reads. Test signals are BCMA non-4706 probe, READID/parameter page correctness, OOB data endianness, flash cache reads/writes, and full MTD tests through the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcma_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcmbca_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcmbca_nand.c

## Purpose
This is BCMBCA platform glue for the shared Broadcom NAND controller. It provides controller-ready interrupt handling and a data-bus read helper that avoids unsafe unaligned memcpy behavior against the NAND cache.

## Important APIs, Types, And Functions
`struct bcmbca_nand_soc` embeds `brcmnand_soc` and stores the interrupt base. `bcmbca_nand_intc_ack` acknowledges `BCMBCA_CTLRDY`; `bcmbca_nand_intc_set` toggles the enable bit. `bcmbca_read_data_bus` chooses direct `memcpy` only when both flash cache and destination meet architecture alignment requirements, otherwise using `memcpy_fromio`.

## Control Flow
Probe maps `nand-int-base`, installs interrupt hooks and `read_data_bus`, then calls `brcmnand_probe`. The core invokes the read-data hook during flash-cache PIO reads.

## State And Persistence
The glue stores the mapped interrupt base and hooks. The alignment policy is compile-time dependent: ARM64 requires 8-byte alignment, other builds use 4-byte alignment.

## Dependencies And Integration Points
It binds `brcm,nand-bcm63138`, depends on named platform resources, and integrates through `struct brcmnand_soc`.

## Risks And Test Signals
Risks include incorrect interrupt clear polarity, alignment assumptions on future architectures, and data corruption if NAND cache is accessed with an incompatible copy primitive. Test signals are aligned and unaligned read buffers, controller-ready IRQs, MTD read/write/erase, OOB reads, and suspend/resume through core PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/bcmbca_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmnand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmnand.c

## Purpose
This is the shared Broadcom raw NAND controller core. It supports controller revisions v2.1 through v7.3, multiple chip-selects, hardware ECC, OOB layouts, flash-cache PIO, FLASH_DMA, EDU DMA, optional SoC-specific interrupt/register hooks, write protect control, and suspend/resume state restoration.

## Important APIs, Types, And Functions
Central state is `struct brcmnand_controller`, `struct brcmnand_host`, `struct brcmnand_cfg`, and DMA descriptor `struct brcm_nand_dma_desc`. Public exports are `brcmnand_probe`, `brcmnand_remove`, and `brcmnand_pm_ops`. NAND callbacks are supplied through `brcmnand_controller_ops`, especially `brcmnand_attach_chip` and `brcmnand_exec_op`.

Revision and register helpers include `brcmnand_revision_init`, `brcmnand_flash_dma_revision_init`, `brcmnand_cs_offset`, `brcmnand_read_reg`, `brcmnand_write_reg`, `brcmnand_set_cfg`, and ECC helpers such as `brcmnand_set_ecc_enabled`, `brcmnand_get_ecc_settings`, and `brcmstb_choose_ecc_layout`. Runtime paths include `brcmnand_read`, `brcmnand_write`, raw/OOB variants, `brcmnand_send_cmd`, `brcmnand_waitfunc`, `brcmnand_low_level_op`, `brcmnand_exec_instructions`, and the legacy native-command path.

## Control Flow
`brcmnand_probe` validates OF compatibility, allocates the controller, enables optional non-MMIO static-key access, maps registers/flash cache, enables the NAND clock, initializes revision-specific capabilities, sets instruction handlers based on revision, configures FLASH_DMA or EDU if present, disables auto device ID and XOR addressing, configures write protection, requests IRQs, then initializes each `brcm,nandcs` child or platform-data chip-select.

Each chip-select is initialized by `brcmnand_init_cs`: it assigns ECC operations, forces READID to 8-bit bus mode before scan, calls `nand_scan`, and registers MTD partitions. Attach then calculates hardware geometry, ECC settings, OOB layout, correction threshold, and ACC_CONTROL flags.

Reads prefer DMA/EDU when possible, otherwise use flash-cache PIO per 512B sector and OOB registers. ECC address registers and correction counters drive `-EBADMSG`/`-EUCLEAN` handling; older controllers verify erased pages in software. Writes disable write protect, clear OOB registers, prefer DMA/EDU when legal, otherwise fill flash cache per sector and issue program commands.

## State And Persistence
Persistent controller state includes revision-derived register maps, feature flags, DMA/EDU resources, completions, cached flash cache bytes for parameter reads, host list, selected instruction handlers, write-protect policy, and low-power saved registers. Per-host state includes chip-select id and `hwcfg`, including geometry, ECC, timing, ACC_CONTROL, and config registers. Suspend saves CS configuration, select/xor/correction threshold, and DMA/EDU mode; resume restores them, re-enables SoC interrupts, and resets chips.

## Dependencies And Integration Points
The core depends on raw NAND/MTD APIs, OF/platform data, clk, DMA mapping, interrupts/completions, static keys, and `brcmnand.h`. Glue drivers provide `struct brcmnand_soc` for custom interrupt acknowledge/enable, register IO, data-bus preparation, or data-bus copy. Device Tree child nodes use `brcm,nandcs`; platform data remains supported.

## Risks And Test Signals
High-risk areas are revision-specific offsets and bitfields, ECC level/sector-size encoding, OOB layout calculations, endianness in flash cache and descriptors, DMA/EDU completion/error handling, `oops_panic_write` fallback, WP behavior controlled by module parameter and DT, and legacy-vs-low-level `exec_op` command coverage. Test signals include compile coverage across glue drivers, probe on every revision family, parameter page/READID reads, page/OOB raw and ECC reads/writes, ECC correction and uncorrectable injection, erased-page bitflip handling, DMA and PIO fallback, suspend/resume, multi-CS setups, write-protect transitions, and bad-block table behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmnand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmnand.h -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmnand.h

## Purpose
This header defines the exported interface between Broadcom NAND platform glue drivers and the shared `brcmnand.c` core.

## Important APIs, Types, And Functions
`struct brcmnand_soc` contains optional hooks for controller-ready IRQ ack/enable, data-bus prepare/unprepare, custom data-bus reads, and register IO ops. `struct brcmnand_io_ops` provides non-MMIO `read_reg`/`write_reg` callbacks. Inline wrappers abstract SoC hooks and endian-safe `brcmnand_readl`/`brcmnand_writel`. The exported functions are `brcmnand_probe`, `brcmnand_remove`, and `brcmnand_pm_ops`.

## Control Flow
Glue drivers populate a `brcmnand_soc` and pass it to `brcmnand_probe`. The core calls hooks when acknowledging interrupts, toggling interrupt enable, preparing parameter/data bus access, reading cache data, or accessing registers through non-MMIO paths.

## State And Persistence
The header itself has no storage, but its hook structs define the persistent glue state shape. `BRCMNAND_NON_MMIO_FC_ADDR` is a sentinel offset used by non-MMIO register ops to target flash-cache data.

## Dependencies And Integration Points
It depends on Linux types and IO helpers. It is included by all brcmnand glue files and the core.

## Risks And Test Signals
Risks include glue drivers providing incomplete IO ops, endian mismatch on MIPS big-endian systems, and misuse of the flash-cache sentinel. Test signals are compile coverage for each glue, non-MMIO BCMA operation, big-endian MIPS access, and suspend/resume calling exported PM ops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmnand.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmstb_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmstb_nand.c

## Purpose
This is the generic Broadcom STB platform glue for the shared brcmnand controller. It binds the generic `brcm,brcmnand` compatible and delegates all behavior to the core without SoC-specific hooks.

## Important APIs, Types, And Functions
`brcmstb_nand_probe` calls `brcmnand_probe(pdev, NULL)`. The platform driver uses `brcmnand_remove` and `brcmnand_pm_ops`, and matches `brcm,brcmnand`.

## Control Flow
Probe is a direct pass-through. The core uses normal MMIO register access and standard controller-ready IRQ handling because no `brcmnand_soc` hook table is supplied.

## State And Persistence
No glue-specific runtime state. All state belongs to `brcmnand.c` and platform resources.

## Dependencies And Integration Points
It depends on the shared core and OF platform matching. Its link order is intentionally after more specific glue such as iProc.

## Risks And Test Signals
Risks are overmatching platforms that need specific hooks and driver registration order conflicts. Test signals are generic STB OF probe, standard IRQ completion, MMIO access, MTD registration, suspend/resume, and ensuring iProc/other specific compatibles bind earlier when present.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/brcmstb_nand.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/iproc_nand.c -->
# sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/iproc_nand.c

## Purpose
This is iProc platform glue for the shared Broadcom NAND controller. It handles iProc-specific controller-ready interrupt registers and APB endianness/mode switching around NAND FIFO and parameter-page accesses.

## Important APIs, Types, And Functions
`struct iproc_nand_soc` embeds `brcmnand_soc`, maps IDM and external register blocks, and uses `idm_lock` to protect IO-control updates. `iproc_nand_intc_ack` acknowledges controller-ready in the external block. `iproc_nand_intc_set` toggles IDM interrupt-read-enable. `iproc_nand_apb_access` switches APB little-endian mode depending on CPU endianness and whether parameter or data access is being prepared.

## Control Flow
Probe allocates glue state, initializes the spinlock, maps `iproc-idm` and `iproc-ext`, installs interrupt and data-bus preparation hooks, then calls `brcmnand_probe`. During core PIO/data operations, prepare/unprepare toggles APB mode under the spinlock.

## State And Persistence
Persistent state consists of mapped IDM/ext bases, hook table, and spinlock. Hardware IO-control state is modified around data access and interrupt enable operations; resume is handled by the core and hook callbacks.

## Dependencies And Integration Points
It binds `brcm,nand-iproc`, requires named resources `iproc-idm` and `iproc-ext`, and integrates with core brcmnand through `struct brcmnand_soc`.

## Risks And Test Signals
Risks include APB endian mode left in the wrong state, missing locking around shared IDM IO control, incorrect behavior for BE vs LE parameter reads, and IRQ enable/ack bit mistakes. Test signals include parameter-page reads on LE/BE builds, normal page/OOB transfers, controller-ready IRQ completion, suspend/resume, and concurrent access stress around APB mode changes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mtd/nand/raw/brcmnand/iproc_nand.c -->
