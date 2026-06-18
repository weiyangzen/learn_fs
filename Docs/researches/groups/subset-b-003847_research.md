# subset-b-003847 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/i2c/Kconfig

Purpose: top-level Kconfig menu for the Linux I2C subsystem in this source tree. It gates `CONFIG_I2C`, ACPI operation-region support, board info, the userspace character device, mux/ATR support, SMBus protocol helpers, algorithm and bus-driver menus, test stubs, slave backends, and debug switches.

Important interfaces: `CONFIG_I2C` selects `RT_MUTEXES` and `IRQ_DOMAIN`; `ACPI_I2C_OPREGION` depends on built-in I2C plus ACPI; `I2C_CHARDEV`, `I2C_MUX`, `I2C_ATR`, `I2C_SMBUS`, `I2C_STUB`, `I2C_SLAVE`, `I2C_SLAVE_EEPROM`, and `I2C_SLAVE_TESTUNIT` define public build surfaces. It sources `drivers/i2c/muxes/Kconfig`, `algos/Kconfig`, and `busses/Kconfig`.

Control flow and state: this file has no runtime logic. Its persistence is Kconfig state saved in kernel configuration and used by kbuild to choose objects. Dependencies integrate I2C with ACPI, OF, slave support, debug flags, and helper auto-selection.

Risks and tests: incorrect dependency changes can hide drivers, break module/built-in link order, or expose helpers without core support. Test by running Kconfig sync/olddefconfig, checking expected symbols in `.config`, and building I2C core plus representative algorithm, bus, slave, and debug configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/Makefile -->
## sources/distributed-fs/ceph-client/drivers/i2c/Makefile

Purpose: kbuild object manifest for the I2C core and top-level helper modules. It wires selected Kconfig symbols to object files and always descends into `algos/`, `busses/`, and `muxes/`.

Important build APIs: `obj-$(CONFIG_I2C)` builds `i2c-core.o`, composed from `i2c-core-base.o` and `i2c-core-smbus.o`, with conditional additions for ACPI, slave support, OF, and OF dynamic probing. Other entries build `i2c-boardinfo.o`, `i2c-smbus.o`, `i2c-dev.o`, `i2c-mux.o`, `i2c-atr.o`, `i2c-stub.o`, and slave backends.

Control flow and state: no runtime control flow. Its state is build composition derived from Kconfig. Integration points are the core I2C subsystem, bus/algorithm subdirectories, and `ccflags-$(CONFIG_I2C_DEBUG_CORE) := -DDEBUG`, which changes compiled debug behavior.

Risks and tests: object omissions or wrong conditional composition can cause unresolved symbols or missing runtime features. Test with `make M=drivers/i2c`, allmodconfig fragments around I2C, and link checks for ACPI/OF/slave variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/i2c/algos/Kconfig

Purpose: Kconfig menu for reusable software/hardware-assisted I2C algorithm modules. It is visible only when `I2C_HELPER_AUTO` is disabled, because normal bus drivers usually select needed helpers automatically.

Important symbols: `I2C_ALGOBIT` provides bit-banged I2C callbacks, `I2C_ALGOPCF` provides PCF8584 algorithm support, and `I2C_ALGOPCA` provides PCA9564/PCA9665 algorithm support. Each is tristate, allowing built-in or module builds.

Control flow and state: no runtime flow. Kconfig state controls whether kbuild includes the matching algorithm objects and whether downstream bus drivers can link exported helper functions such as `i2c_bit_add_bus`, `i2c_pcf_add_bus`, or `i2c_pca_add_bus`.

Dependencies and integration: this file is sourced under top-level `I2C`; selecting these symbols affects `drivers/i2c/algos/Makefile`. Bus drivers such as Acorn, Elektor, ICY, PCA platform/ISA, and GPIO-like adapters integrate through these algorithms.

Risks and tests: visibility or tristate mistakes can produce impossible module combinations. Test by building with helper auto on/off and by selecting each algorithm as `y` and `m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/Makefile -->
## sources/distributed-fs/ceph-client/drivers/i2c/algos/Makefile

Purpose: kbuild manifest for I2C algorithm modules. It maps `CONFIG_I2C_ALGOBIT`, `CONFIG_I2C_ALGOPCF`, and `CONFIG_I2C_ALGOPCA` to their object files.

Important entries: `i2c-algo-bit.o` implements GPIO/bit-bang style master transfers; `i2c-algo-pcf.o` implements PCF8584 controller sequencing; `i2c-algo-pca.o` implements PCA9564/PCA9665 controller sequencing. `ccflags-$(CONFIG_I2C_DEBUG_ALGO) := -DDEBUG` enables debug-only code paths in algorithm sources.

Control flow and state: no runtime logic. The file contributes build-time state by choosing objects and compile flags. It integrates with top-level I2C Makefile recursion and with bus drivers that select or depend on algorithm modules.

Risks and tests: missing objects break exported-symbol consumers; debug flag changes can alter module parameters and logging paths. Test by compiling each algorithm as built-in and module, with `CONFIG_I2C_DEBUG_ALGO` enabled and disabled, and verifying `modpost` exports for algorithm add-bus APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-bit.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-bit.c

Purpose: generic bit-banging I2C master algorithm for adapters that expose callbacks to set/read SDA and SCL. It exports `i2c_bit_algo`, `i2c_bit_add_bus`, and `i2c_bit_add_numbered_bus`.

Important APIs and flow: `struct i2c_algo_bit_data` callbacks drive `sdalo`, `sdahi`, `scllo`, and `sclhi`; `sclhi` waits for clock stretching up to `adap->timeout`. `bit_xfer` runs optional `pre_xfer`, emits START/repeated START/STOP, calls `bit_doAddress`, then `sendbytes` or `readbytes`. Reads support `I2C_M_RECV_LEN`; addressing supports 7-bit, 10-bit, `I2C_M_REV_DIR_ADDR`, `I2C_M_IGNORE_NAK`, `I2C_M_NOSTART`, and `I2C_M_STOP`. `bit_xfer_atomic` reuses the normal path after warning if the adapter is not marked atomic-capable.

State and dependencies: per-adapter state lives in callback data, `udelay`, `timeout`, quirks, and optional pre/post hooks. Module parameters `bit_test` and debug level influence diagnostics. Integration is through `i2c_adapter.algo` and I2C core registration.

Risks and tests: clock-stretch timeouts, write-only line callbacks, incomplete arbitration handling, and invalid SMBus block lengths are key risks. Test with GPIO-backed adapters, forced NAK/timeouts, `bit_test=2`, SMBus emulation, 10-bit addressing, and atomic-transfer callers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-bit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pca.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pca.c

Purpose: reusable I2C master algorithm for Philips/NXP PCA9564 and PCA9665 parallel-bus I2C controllers. It exports `i2c_pca_add_bus` and `i2c_pca_add_numbered_bus`.

Important APIs and flow: hardware callbacks come from `struct i2c_algo_pca_data`: `write_byte`, `read_byte`, `wait_for_completion_cb`, optional reset, clock data, and bus settings. `pca_xfer` waits for idle status `0xf8`, then walks the PCA state machine for START, repeated START, address ACK/NAK, TX, RX, arbitration lost, and bus error statuses. `pca_reset`, `pca_probe_chip`, and `pca_init` distinguish PCA9564 from PCA9665 and program clock/mode timing.

State and dependencies: the algorithm persists per-adapter chip type, requested clock, and reset-time bus settings. It depends on I2C core message semantics and PCA register definitions from `linux/i2c-algo-pca.h`.

Risks and tests: state-machine status handling is hardware-sensitive; reset must restore PCA9665 indirect-register timing; NAK/arbitration cases can return partial progress. Test with both chip variants, invalid clock rates, NAKs, arbitration loss, stuck SDA/SCL, repeated-start transfers, and module debug output.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pca.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.c

Purpose: generic algorithm for PCF8584 I2C controllers. It exports `i2c_pcf_add_bus`, initializes the chip, and exposes an I2C master algorithm.

Important APIs and flow: callbacks in `struct i2c_algo_pcf_data` read/write PCF data/control registers and supply own address, clock, wait-for-PIN, optional transfer begin/end, and arbitration-lost delay. `pcf_init_8584` performs register detection and initialization. `pcf_xfer` waits for bus free, sends an address, issues START for the first message, waits for PIN, checks LRB ACK, then uses `pcf_sendbytes` or `pcf_readbytes`. Multi-message transfers end with STOP or repeated START.

State and dependencies: state is mostly hardware register state plus adapter callbacks; arbitration loss resets control bits via `handle_lab`. It depends on I2C core, PCF public callback definitions, and local PCF bit masks.

Risks and tests: timeout constants are short and polling/callback timing is board-specific. Risks include incorrect dummy-read receive sequencing, lost arbitration recovery, and no 10-bit handling despite protocol-mangling functionality. Test PCF detection, ACK/NAK, multi-message repeated starts, LAB events, stuck bus, and begin/end hooks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.h -->
## sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.h

Purpose: local register-bit header for the PCF8584 algorithm implementation. It encodes control, status, clock, transmission-rate, and internal-register selection constants.

Important definitions: control bits include `I2C_PCF_PIN`, `ESO`, `ES1`, `ES2`, `ENI`, `STA`, `STO`, and `ACK`; compound commands include `I2C_PCF_START`, `STOP`, `REPSTART`, and `IDLE`. Status bits include initialization, bus error, last received bit, addressed-as-slave, lost arbitration, and bus busy. Clock and transfer constants define supported oscillator and serial rates.

Control flow and state: no functions. Its constants are consumed by `i2c-algo-pcf.c` to select PCF internal registers and interpret hardware state.

Dependencies and integration: private to the PCF algorithm, complementing public callback declarations in `linux/i2c-algo-pcf.h`.

Risks and tests: bit definition errors directly corrupt bus sequencing. Test indirectly through PCF8584 init, status polling, START/STOP/repeated-start transfers, LRB ACK detection, and LAB recovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/algos/i2c-algo-pcf.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/Kconfig -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/Kconfig

Purpose: full I2C hardware bus-driver Kconfig menu. It groups host adapters into PC SMBus, ACPI, Mac, embedded/SoC, external USB/parallel, and other bus-driver categories.

Important symbols in this subset: `I2C_ALI1535`, `I2C_ALI1563`, `I2C_ALI15X3`, `I2C_AMD756`, `I2C_AMD8111`, `I2C_AMD_MP2`, `I2C_AMD_ASF`, `I2C_ALTERA`, `I2C_ASPEED`, and `I2C_ACORN`. Dependencies cover PCI, ACPI, HAS_IOPORT, OF, architecture gates, `I2C_PIIX4`, and slave support. Several entries select helper algorithms or SMBus/slave helpers.

Control flow and state: no runtime code; Kconfig state controls build inclusion and dependency legality. It integrates directly with `busses/Makefile` and indirectly with platform firmware descriptions, PCI IDs, ACPI IDs, and OF compatible strings in the drivers.

Risks and tests: wrong dependencies can enable drivers on unsupported buses or hide valid compile-test coverage. Test by generating configs for PCI-only, OF-only, ACPI-only, and COMPILE_TEST combinations, then building targeted modules and checking selected helper symbols.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/Makefile -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/Makefile

Purpose: kbuild manifest for all I2C hardware bus drivers. It maps Kconfig symbols to object files and records composite driver objects.

Important entries for this work item: ALi and AMD legacy SMBus drivers map one-to-one (`i2c-ali1535.o`, `i2c-ali1563.o`, `i2c-ali15x3.o`, `i2c-amd756.o`, `i2c-amd8111.o`); `CONFIG_I2C_AMD_MP2` builds both `i2c-amd-mp2-pci.o` and `i2c-amd-mp2-plat.o`; `CONFIG_I2C_AMD_ASF` builds `i2c-amd-asf-plat.o`; `I2C_ALTERA`, `I2C_ASPEED`, and `I2C_ACORN` map to their bus objects. The file also defines composite objects such as DesignWare, AT91, STM32F7, Octeon, and ThunderX.

Control flow and state: no runtime flow. It integrates Kconfig state with link/module composition and debug compilation via `ccflags-$(CONFIG_I2C_DEBUG_BUS) := -DDEBUG`.

Risks and tests: missing composite pairings cause link failures or half-present drivers, especially MP2 PCI/platform split. Test allmodconfig, per-symbol module builds, and `modpost` for shared exports.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-acorn.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-acorn.c

Purpose: Acorn IOC/IOMD platform I2C adapter implemented through the generic bit-banging algorithm. It targets the Acorn system bus where devices such as PCF8583 RTC/static RAM live.

Important APIs and flow: `ioc_setscl`, `ioc_setsda`, `ioc_getscl`, and `ioc_getsda` manipulate `IOC_CONTROL` bits while preserving unrelated control bits. `force_ones` tracks output values for SCL/SDA and fixed high bits. `ioc_data` provides `struct i2c_algo_bit_data` with 80 us delay and HZ timeout; `ioc_ops` defines numbered adapter 0. `i2c_ioc_init` initializes SCL/SDA high and calls `i2c_bit_add_numbered_bus`.

State and dependencies: state is global `force_ones` and IOC hardware register contents. It depends on Acorn architecture headers, raw IOC I/O helpers, and `i2c-algo-bit`.

Risks and tests: preserving non-I2C bits in `IOC_CONTROL` is critical; there is no remove path because this is init-only platform support. Test on ARCH_ACORN or compile coverage, line toggling, bit-algo bus test, and adapter numbering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-acorn.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali1535.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali1535.c

Purpose: polling SMBus host driver for the ALi M1535 south bridge PMU SMBus controller.

Important APIs and flow: `ali1535_setup` enables the PCI device, derives the SMBus I/O base, checks ACPI conflicts, requests I/O space, validates SMB/host enables, and programs clock. `ali1535_access` maps SMBus quick/byte/byte-data/word/block operations into host registers, clamps block length, resets block pointer, calls `ali1535_transaction`, then reads results. `ali1535_transaction` clears status, handles busy/error bits, starts via `SMBHSTPORT`, polls status, and issues kill/timeout recovery actions. PCI probe registers a single `i2c_adapter` with `smbus_xfer`.

State and dependencies: global `ali1535_smba`, `ali1535_offset`, and static adapter mean one controller instance. Dependencies include PCI, ACPI resource checks, I/O port access, and I2C core.

Risks and tests: busy bits can be unrecoverable without power reset; no interrupts; collision and no-response share status; remove intentionally avoids `pci_disable_device`. Test probe on matching hardware, ACPI conflict refusal, all advertised SMBus transaction types, block reads/writes, timeouts, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali1535.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali1563.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali1563.c

Purpose: polling SMBus driver for the ALi 1563 southbridge, whose SMBus 2.0 controller resembles Intel i801.

Important APIs and flow: `ali1563_setup` reads the SMB base/enable register, tries to enable I/O space if needed, checks ACPI conflicts, and requests a 16-byte I/O region. `ali1563_access` waits for idle, clears status, maps SMBus sizes to controller encodings, writes address/command/data, and either calls `ali1563_transaction` or the special block path. `ali1563_block` transfers block bytes through repeated `ali1563_block_start` byte-ready cycles. Probe registers one HWMON-class adapter.

State and dependencies: global `ali1563_smba` and static adapter imply single instance. It uses PCI IDs, ACPI region checks, port I/O, sleeps for polling, and I2C core `smbus_xfer`.

Risks and tests: block transfer sequencing is more complex than simple transactions; timeout/kill handling may leave controller state ambiguous; busy wait before access spins without sleep. Test quick/byte/word/block operations, block length clamping, device error/no-response, bus collision, probe enable path, and remove resource release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali1563.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali15x3.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali15x3.c

Purpose: polling SMBus host driver for ALi M1514/M1543-era south bridge controllers.

Important APIs and flow: `ali15x3_setup` unlocks address registers, reads or forces the I/O base (`force_addr` module parameter), checks ACPI conflicts, requests I/O space, enables SMBus device/controller bits, and sets SMBus clock. `ali15x3_access` writes transaction registers for quick/byte/byte-data/word/block transfers, calls `ali15x3_transaction`, then fetches readback data. `ali15x3_transaction` clears stale status, tries timeout reset on busy state, starts the transaction, polls for done/error, and reports collision/no-response, device error, or timeout.

State and dependencies: static `ali15x3_smba`, `force_addr`, and one static adapter define persistent state. Integration is PCI ID based, HWMON-class I2C adapter registration, I/O ports, ACPI conflict checks, and module parameters.

Risks and tests: forced addresses can collide with platform firmware; collision/no-response are indistinguishable; busy recovery can require power reset. Test normal and forced probe, resource conflict rejection, all SMBus sizes, block pointer reset, timeout handling, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-ali15x3.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-altera.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-altera.c

Purpose: platform driver for Altera Soft IP I2C controllers, using MMIO registers, FIFO thresholds, clocks, and threaded interrupts.

Important APIs and flow: `struct altr_i2c_dev` stores register base, current message, completion, clock, FIFO size, cached interrupt state, and adapter. `altr_i2c_init` programs bus timing from input clock and `clock-frequency`. `altr_i2c_xfer_msg` prepares one message, drains RX FIFO, writes START/address, enables RX/TX/error interrupts, waits for completion, checks timeout and idle state, and disables the core. Top-level `altr_i2c_xfer` processes messages sequentially. The IRQ pair captures status quickly then handles FIFO service, NACK, arbitration loss, RX overflow, and completion.

State and dependencies: runtime state is per device and protected by `isr_mutex`. Dependencies include platform resources, OF compatible `altr,softip-i2c-v1.0`, clocks, IRQs, completions, MMIO, and I2C core.

Risks and tests: multi-message transfers get STOP per message rather than combined repeated-start semantics; IRQ masking must match status bits; FIFO sizing from firmware matters. Test reads/writes, NACK/arbitration/RX overflow, clock-frequency limits, timeout, remove, and OF probe.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-altera.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-asf-plat.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-asf-plat.c

Purpose: AMD Alert Standard Format platform driver layered on PIIX4-compatible SMBus resources. It supports ASF block writes and I2C slave/target receive callbacks for DASH/MCTP-style traffic.

Important APIs and flow: `amd_asf_xfer` rejects reads, enforces ASF length, requests SB800 MMIO ownership, temporarily switches controller to master mode, sends block data through `amd_asf_access`, then restores target setup. `amd_asf_reg_target` configures listening address and enables target interrupts; `amd_asf_process_target` runs in delayed work to read banks and emit `i2c_slave_event` write-request/write-received/stop events. IRQ handling schedules target work or updates controller interrupt bits and writes EOI.

State and dependencies: `struct amd_asf_dev` stores adapter, EOI MMIO, registered target, delayed work, SB800 MMIO config, and port resource. It depends on `i2c-piix4.h` helpers and imports namespace `PIIX4_SMBUS`.

Risks and tests: shared PIIX4/SB800 resource ownership, bank handling, delayed slave event timing, and PEC enablement are sensitive. Test ACPI `AMDI001A` probe, target register/unregister, block length boundaries, IRQ/EOI behavior, and coexistence with PIIX4 SMBus.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-asf-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-pci.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-pci.c

Purpose: PCI-side communication driver for AMD MP2 I2C hardware. It owns the PCI device, MMIO mailbox, IRQ, runtime PM, and shared command serialization used by platform I2C adapters.

Important APIs and flow: exported functions include `amd_mp2_bus_enable_set`, `amd_mp2_rw`, `amd_mp2_process_event`, `amd_mp2_rw_timeout`, callback register/unregister, and `amd_mp2_find_device`. Commands are encoded into C2P message registers; small transfers use C2P message data, larger transfers pass DMA addresses. The IRQ handler reads per-bus P2C event registers, clears them, disables interrupt generation, stores the event, and calls the registered platform completion callback. Event processing validates response/status, length, and slave address, copies read data when needed, and unlocks the shared C2P mutex.

State and dependencies: `struct amd_mp2_dev` tracks two bus callbacks, MMIO, lock owner, PCI state, and IRQ. Dependencies are PCI, DMA, runtime PM, and the shared MP2 header.

Risks and tests: the single C2P mailbox makes lock/unlock correctness critical; timeout paths must release locks; only one MP2 device is discoverable by platform code. Test two-bus concurrency, DMA and <=32-byte paths, interrupts, suspend/resume, timeout recovery, and remove register clearing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-pci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-plat.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-plat.c

Purpose: ACPI platform-side AMD MP2 I2C adapter driver. It creates I2C adapters for MP2 bus IDs and delegates command transport to the PCI-side MP2 driver.

Important APIs and flow: `i2c_amd_probe` reads ACPI UID as bus ID, finds the MP2 PCI device, registers a callback, configures adapter quirks and speed, enables the bus, and calls `i2c_add_adapter`. `i2c_amd_xfer` runtime-PM gets the PCI device, sends each message via `i2c_amd_xfer_msg`, then releases PM. Messages over 32 bytes are mapped with DMA; completion waits on a per-adapter completion and then calls `amd_mp2_process_event`. Suspend/resume disable and re-enable the MP2 bus.

State and dependencies: `struct amd_i2c_dev` wraps shared `amd_i2c_common`, platform device, adapter, and completion. It depends on ACPI `AMDI0011`, MP2 PCI exports, DMA-safe I2C buffers, runtime PM, and I2C core.

Risks and tests: probe assumes one MP2 PCI device; remove must block transfers while clearing callbacks; DMA unmap on timeout is delicate. Test ACPI UID 0/1, deferred probe, long transfers, timeout, suspend/resume, removal during bus lock, and speed mapping.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2-plat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2.h -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2.h

Purpose: shared private ABI between AMD MP2 PCI transport and platform adapter drivers.

Important definitions: register offsets define C2P/P2C mailboxes and interrupt registers. `enum i2c_cmd`, `speed_enum`, `mem_type`, `response_type`, and `status_type` encode firmware protocol values. `union i2c_cmd_base` packs command, bus ID, slave address, length, speed, and memory type into a 32-bit command. `union i2c_event` unpacks response/status, memory type, bus ID, length, and address. `struct amd_i2c_common` is per-bus shared command state; `struct amd_mp2_dev` is per-PCI-device state.

Control flow and state: inline runtime PM helpers operate on the PCI device. Function declarations define exported transport operations consumed by the platform driver.

Risks and tests: bitfield layout and enum values are hardware ABI; changing them breaks firmware communication. Test by compiling both MP2 objects together, validating command/event encoding with hardware traces, and exercising all speed and transfer-size modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd-mp2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd756.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd756.c

Purpose: polling SMBus driver for AMD756/766/768/8111 SMBus 1.0 and Nvidia nForce controllers.

Important APIs and flow: `amd756_probe` filters PCI function numbers, reads chipset-specific I/O base, validates enable bits, checks ACPI conflicts, requests I/O space, and registers one HWMON-class adapter. `amd756_access` maps SMBus quick/byte/byte-data/word/block operations into host registers and controller cycle type, then calls `amd756_transaction`. The transaction path waits for host/SMBus busy to clear, starts the cycle, polls completion, reports protocol/no-response, collision, timeout, or success, clears status bits, and aborts on stuck states.

State and dependencies: global `amd756_ioport` and static adapter limit support to one device. It depends on PCI IDs, ACPI resource checking, I/O ports, sleeps, and I2C `smbus_xfer`.

Risks and tests: singleton state, chipset-specific function filtering, and abort recovery are risks; block transfer uses simple FIFO-like host block data access. Test supported IDs/functions, all SMBus operations, collision/no-response/timeout injection, ACPI conflict rejection, and unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd756.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd8111.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd8111.c

Purpose: AMD8111 SMBus 2.0 driver implemented through the ACPI embedded-controller register model exposed over PCI I/O space.

Important APIs and flow: `amd_ec_wait_write`, `amd_ec_wait_read`, `amd_ec_read`, and `amd_ec_write` serialize EC command/data access. `amd8111_access` programs SMBus command, data, block count, address, and protocol registers for quick, byte, byte-data, word, block, I2C block, process call, block process call, and PEC-enabled operations. It polls status for done and validates status bits before reading response data. Probe allocates per-device `struct amd_smbus`, checks I/O resources and ACPI conflicts, requests region, disables PCI misc interrupt routing, and registers the adapter.

State and dependencies: per-device state holds PCI device, adapter, base, and size. Dependencies are PCI, ACPI resource conflict checking, I/O ports, I2C core, and EC-style timing.

Risks and tests: EC waits are tight udelay loops; status code detail is collapsed to `-EIO`; block `len` reuse must remain correct. Test every advertised functionality bit, PEC variants, busy EC timeouts, resource conflicts, and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-amd8111.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-aspeed.c -->
## sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-aspeed.c

Purpose: platform driver for Aspeed AST24xx/25xx/26xx I2C controllers with interrupt-driven master transfers, optional slave mode, bus recovery, clock setup, and reset handling.

Important APIs and flow: `struct aspeed_i2c_bus` stores adapter, MMIO base, reset, spinlock, completion, clock function, transfer state, multi-master flag, and optional slave state. `aspeed_i2c_master_xfer` prepares message state, recovers a busy single-master bus if needed, starts transfer, waits for completion, and resets/recovers on timeout. `aspeed_i2c_master_irq` advances a detailed master state machine across START, TX, RX, STOP, error, SMBus block receive length, and bus-recovery completion. Slave IRQ support maps hardware events to `i2c_slave_event`. Probe maps resources, reads clock/reset/frequency/OF match, initializes hardware, requests IRQ, and registers the adapter.

State and dependencies: persistent state is per bus, protected by spinlock and I2C bus locking. Dependencies include OF compatibles, clocks, resets, IRQs, completions, optional `CONFIG_I2C_SLAVE`, and MMIO registers.

Risks and tests: coalesced master/slave interrupts, pending master during slave activity, bus recovery, clock divider clamping, and timeout reset are high-risk. Test AST2400/2500/2600 compatibles, multi-master, slave mode, SMBus block receive, hung SDA/SCL recovery, NAK/arbitration, suspend-like reset, and remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-aspeed.c -->
