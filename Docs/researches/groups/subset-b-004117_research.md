# subset-b-004117 research

Grouped research for Linux media PCI files under `sources/distributed-fs/ceph-client/drivers/media/pci`. Each section preserves the source path and is bounded for reconciliation into per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-core.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-core.c

Purpose: implements the operational core of the Digital Devices PCIe bridge driver. It owns module parameters for adapter allocation, CI bitrate, TS loopback, DMA shape, dummy tuner attachment, and initialization suppression. It builds the global `ddbridge` char class, per-board sysfs attributes, DMA buffers, DVB adapters/demuxes/frontends, CI/loop devices, port probing, IRQ-to-workqueue dispatch, SPI flash reads, temperature/fan handling, and the top-level `ddb_init()`/cleanup helpers consumed by `ddbridge-main.c`.

Important APIs/types/functions: exported entry points include `ddb_irq_set()`, `ddb_buffers_alloc/free()`, `ddb_ports_init/attach/detach/release()`, `ddb_device_create/destroy()`, `ddb_irq_handler*()`, `ddbridge_flashread()`, `ddb_init()`, `ddb_unmap()`, `ddb_init_ddbridge()`, and `ddb_exit_ddbridge()`. Central state is `struct ddb`, `ddb_link`, `ddb_port`, `ddb_input`, `ddb_output`, `ddb_dma`, and `ddb_dvb` from `ddbridge.h`. Frontend attach helpers bind DRXK, STV0367, CXD2841ER, STV090x/STV0910, MXL5xx, MCI/SX8, and the dummy frontend.

Control flow: module-level init creates a char class and workqueue. PCI probe calls `ddb_init()`, which optionally resets boards, initializes I2C, probes each port, allocates DMA rings, attaches DVB/CI devices, creates sysfs, and powers fans. Port probing uses board metadata and I2C signatures to classify modules. DVB feed start/stop starts and stops DMA, IRQ handlers acknowledge status bits and queue work, and workqueue callbacks move TS packets to DVB demuxes, user-space CI devices, or redirected DMA paths.

State and persistence: runtime state is in allocated kernel objects, MMIO registers, DMA ring indices, sysfs-exposed tuning values (`gap*`, `fmode*`, LEDs), link temperature tables, and global `ddbs[]` mapping minor numbers to active devices. No durable filesystem persistence is maintained; flash reads are read-only SPI transactions. Locks include DMA spinlocks, redirect mutex, flash mutex, I2C gate mutexes, device mutexes, and temperature spinlocks.

Dependencies/integration: integrates PCI/MMIO/DMA, Linux DVB core, V4L2-related frontend modules, I2C helpers, CI support, `ddbridge-i2c.c`, hardware metadata from `ddbridge-hw.c`, register definitions, MAX/MCI helpers, and CI code outside this subset. It also exposes `/dev/ddbridge/cardN` through a class device and DVB devices through the media subsystem.

Risks and test signals: high-risk areas are DMA ring accounting, redirect chains, partial attach unwind, user-triggered sysfs changes while streaming, I2C-based module detection, and MMIO failure handling (`safe_ddbreadl`). Test by probing known boards, checking `dmesg` for port classification, exercising DVB tuning and CI read/write/poll, validating `ts_irq`/`i2c_irq`, changing `gap`/`fmode`, removing the module under idle and active paths, and running with `alt_dma`, boundary `dma_buf_num`, and failure injection around frontend attach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-dummy-fe.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-dummy-fe.c

Purpose: provides a synthetic DVB-C frontend for ddbridge debug/test configurations. `ddbridge_dummy_fe_qam_attach()` allocates a small state object, copies a static `dvb_frontend_ops`, stores the state in `demodulator_priv`, and exports the symbol for `ddbridge-core.c` dummy tuner attachment.

Important APIs/types/functions: `struct ddbridge_dummy_fe_state` embeds `struct dvb_frontend`. The frontend ops implement `init`, `sleep`, `set_frontend`, `get_frontend`, `read_status`, BER, strength, SNR, uncorrected block reads, and `release`. `read_status()` always reports full lock; metrics return zero; `set_frontend()` only forwards to an attached tuner if one exists.

Control flow: attach is called by `demod_attach_dummy()` when the core is configured for a dummy tuner. Userspace sees a DVB-C frontend with fixed capability metadata. Tuning calls succeed without hardware, and release frees the allocation.

State and persistence: only the allocation behind `demodulator_priv` persists for the frontend lifetime. It has no hardware registers, no DMA, no saved settings, and no durable state.

Dependencies/integration: depends on DVB frontend core and `ddbridge-dummy-fe.h`. It integrates through `dvb_attach(ddbridge_dummy_fe_qam_attach)` in the ddbridge core.

Risks and test signals: because it always reports lock, it is not a signal-quality simulator and can mask real tuning path failures if enabled accidentally. Test by loading with the relevant dummy parameter, confirming frontend registration, issuing basic tuning/status calls, and verifying module removal calls `release()` without leaks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-dummy-fe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-dummy-fe.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-dummy-fe.h

Purpose: declares the ddbridge dummy frontend attach API. It is a small include guard around the DVB frontend includes and the single constructor `ddbridge_dummy_fe_qam_attach()`.

Important APIs/types/functions: the exported API returns `struct dvb_frontend *` or `NULL` on allocation failure. Callers own the returned frontend through normal DVB frontend registration and release semantics.

Control flow: included by `ddbridge-core.c` and implemented by `ddbridge-dummy-fe.c`; no control flow beyond compile-time declaration.

State and persistence: no state is declared here beyond the function contract.

Dependencies/integration: includes `<linux/dvb/frontend.h>` and `<media/dvb_frontend.h>`, tying it directly to DVB core types.

Risks and test signals: risk is limited to API drift with the implementation. Test signals are successful compile/link when dummy frontend support is built and correct symbol resolution when `dvb_attach()` is used.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-dummy-fe.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-hw.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-hw.c

Purpose: defines Digital Devices board metadata and register maps used by ddbridge probe and core initialization. It maps PCI vendor/device/subdevice IDs to `struct ddb_info` descriptors and provides `get_ddb_info()`.

Important APIs/types/functions: static `ddb_regset` and `ddb_regmap` describe Octopus input/output, DMA, DMA buffer, and I2C register windows plus interrupt bases. Numerous `ddb_info` entries encode board type, name, port count, I2C mask, board-control reset bits, LEDs/fans/temp sensors, TS quirks, temp monitor IRQ, MCI port count, and MCI type. `ddb_device_ids[]` is searched by `get_ddb_info()`.

Control flow: `ddbridge-main.c` populates `dev->link[0].info` from PCI IDs. The core uses the resulting descriptor to initialize boards, I2C adapters, ports, DMA register offsets, temp monitoring, and sysfs attributes. Unknown boards fall back to `ddb_none`, which still has the Octopus register map but identifies unsupported hardware.

State and persistence: all data is immutable static metadata. There is no runtime mutation or persistence in this file.

Dependencies/integration: depends on constants from `ddbridge.h` and `ddbridge-hw.h`. It is the hardware database for `ddbridge-main.c`, `ddbridge-core.c`, and `ddbridge-i2c.c`.

Risks and test signals: incorrect metadata can misprobe hardware, use wrong I2C masks, assert wrong reset bits, or attach unsupported frontends. Test by matching `dmesg` board names and hardware/regmap IDs against real cards, verifying port counts and temp/fan attributes, and confirming new PCI IDs do not regress existing subdevice matches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-hw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-hw.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-hw.h

Purpose: exposes the ddbridge hardware metadata lookup interface. It defines the Digital Devices vendor ID and `struct ddb_device_id`.

Important APIs/types/functions: `DDVID` is `0xdd01`. `struct ddb_device_id` stores PCI vendor/device/subvendor/subdevice plus a pointer to `struct ddb_info`. `get_ddb_info()` resolves PCI IDs to immutable board info.

Control flow: included by `ddbridge-main.c` for probe-time board lookup and by `ddbridge-hw.c` for implementation.

State and persistence: no mutable state; this header only declares metadata shape and lookup API.

Dependencies/integration: includes `ddbridge.h` for `struct ddb_info`.

Risks and test signals: API changes affect PCI probing. Compile coverage plus probe of known supported PCI IDs are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-hw.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-i2c.c

Purpose: implements ddbridge hardware-backed I2C adapters. It maps board register metadata into Linux `i2c_adapter` instances, performs MMIO-buffered transfers, and uses ddbridge IRQ completions to wait for transaction completion.

Important APIs/types/functions: `ddb_i2c_init()` creates adapters for each link whose `i2c_mask` enables a controller; `ddb_i2c_release()` removes them. `ddb_i2c_master_xfer()` supports single read, single write, and write-then-read transactions. `ddb_i2c_cmd()` writes `I2C_COMMAND`, waits up to one second, checks hardware error bits, and logs timeout diagnostics. `i2c_handler()` completes pending commands.

Control flow: during `ddb_init()`, adapters are registered after board reset and before port probing. Port detection and frontend attach then use those adapters. IRQ dispatch from `ddbridge-core.c` invokes `i2c_handler()` through `ddb_irq_set()`.

State and persistence: each `struct ddb_i2c` stores adapter identity, link, register offsets, hardware buffer offsets, buffer size, and a completion. State is runtime-only and tied to the PCI device lifetime.

Dependencies/integration: depends on `ddbridge.h`, register constants, MMIO helpers, Linux I2C core, and board register maps from `ddbridge-hw.c`.

Risks and test signals: risks include timeout handling, I2C buffer length limits, shared read/write buffer assumptions, interrupt loss, and error propagation as generic `-EIO`. Test with probe-time frontend detection, EEPROM/temperature reads, forced absent devices, concurrent frontend gate use, and interrupt-disabled timeout paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-i2c.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-i2c.h

Purpose: declares ddbridge I2C lifecycle APIs and provides small helper wrappers for common I2C register operations.

Important APIs/types/functions: `ddb_i2c_init()` and `ddb_i2c_release()` are implemented in `ddbridge-i2c.c`. Inline helpers include `i2c_io`, `i2c_write`, `i2c_read`, `i2c_read_regs`, `i2c_read_regs16`, `i2c_write_reg16`, `i2c_write_reg`, `i2c_read_reg16`, and `i2c_read_reg`.

Control flow: helpers are used heavily during port probing, frontend attachment, LED/SNR/temp sysfs reads, and board-specific initialization. They translate successful `i2c_transfer()` message counts into zero and failures into `-1`.

State and persistence: no state beyond stack `i2c_msg` arrays.

Dependencies/integration: includes Linux I2C and `ddbridge.h`; used by core, MAX, and hardware-probing code.

Risks and test signals: helpers collapse all transfer failures to `-1`, so diagnostics come from callers or adapter logs. Test by compiling all call sites, probing known I2C devices, and checking that 8-bit versus 16-bit register addressing matches each frontend/tuner chip.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-i2c.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-io.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-io.h

Purpose: provides inline MMIO helpers for ddbridge devices and links.

Important APIs/types/functions: `ddbreadl()`/`ddbwritel()` access device registers, `ddblreadl()`/`ddblwritel()` access link-tagged registers through the same mapped BAR, `ddbcpyto()`/`ddbcpyfrom()` copy to and from MMIO buffers, and `safe_ddbreadl()` detects all-ones MMIO read failures and logs an error.

Control flow: all runtime files use these helpers to access hardware registers, I2C buffers, DMA tables, interrupts, SPI flash, LNB control, MCI commands, and temp monitor registers.

State and persistence: no state; operations directly read/write memory-mapped hardware.

Dependencies/integration: includes `<linux/io.h>` and `ddbridge.h`.

Risks and test signals: register offsets must already include any required link tag; misuse can affect the wrong link. `safe_ddbreadl()` only catches `~0`, not stale or semantically invalid values. Test by checking probe logs, IRQ counters, I2C transactions, and register dump attributes on real hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-main.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-main.c

Purpose: is the PCI driver entry point for ddbridge. It registers the PCI driver, maps BAR0, sets DMA masks, initializes interrupts/MSI, identifies board metadata, and delegates device setup to `ddbridge-core.c`.

Important APIs/types/functions: `ddb_probe()`, `ddb_remove()`, `ddb_irq_init()`, `ddb_irq_exit()`, `ddb_msi_exit()`, `module_init_ddbridge()`, and `module_exit_ddbridge()`. The PCI ID table matches many Digital Devices device IDs using `DDB_DEVICE_ANY()`. The `msi` module parameter controls MSI/MSI-X use when configured.

Control flow: module init calls `ddb_init_ddbridge()` then `pci_register_driver()`. Probe enables the PCI device, sets bus mastering and DMA mask, allocates `struct ddb`, fills link IDs, calls `get_ddb_info()`, maps registers, reads HW/regmap IDs, disables DMA bases, requests IRQs, and calls `ddb_init()`. Remove unwinds sysfs/DVB/I2C/IRQ/MSI/DMA/MMIO/PCI state.

State and persistence: per-device state is allocated with `vzalloc()` and stored via `pci_set_drvdata()`. `dev->msi` records allocated vectors. No durable state is stored.

Dependencies/integration: integrates PCI core, DMA API, interrupt APIs, board metadata from `ddbridge-hw.c`, core lifecycle, I2C release, MMIO helpers, and register constants.

Risks and test signals: error unwinds must match initialization order; `dma_set_mask()` failure after `pci_enable_device()` is a sensitive path; MSI split interrupt handling depends on hardware mask programming. Test with module load/unload, legacy IRQ and MSI modes, unsupported boards, BAR read failure, and active-stream device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-main.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-max.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-max.c

Purpose: implements MAX S4/S8 and MCI-based MAX frontend attachment plus LNB voltage/tone/DiSEqC routing policy. It adapts MXL5xx and SX8 frontends to ddbridge DVB inputs and board LNB hardware.

Important APIs/types/functions: exported `ddb_lnb_init_fmode()`, `ddb_fe_attach_mxl5xx()`, and `ddb_fe_attach_mci()`. Internal helpers send `LNB_CMD_*`, buffer DiSEqC messages, set satellite/tone/voltage, remap frontend input, read firmware from SPI flash, and override frontend SEC operations. Module parameters are `fmode`, `fmode_sat`, and `old_quattro`.

Control flow: during DVB input attach, the core calls either MXL5xx or MCI attach. Attach initializes demod/tuner mapping, LNB command channel for the first four inputs, fmode, frontend callbacks, and `sec_priv`. Runtime `set_voltage`, `set_tone`, and DiSEqC operations update shared link LNB state and write hardware commands.

State and persistence: mutable state lives in `dev->link[lnr].lnb`: lock, tone bitmap, voltage arrays, aggregate `voltages`, old voltage cache, and fmode. State is runtime-only but exposed through sysfs `fmode*`.

Dependencies/integration: depends on ddbridge registers/MMIO, MXL5xx frontend, MCI config from `ddbridge-sx8.c`, SPI flash read from core, and DVB frontend SEC APIs.

Risks and test signals: LNB state is shared by inputs and sensitive to fmode/quattro mapping; incorrect locking or voltage caching can leave wrong power on satellite inputs. Test by tuning multiple inputs, toggling 13/18V and tone, sending DiSEqC, reading firmware-backed MXL attach, changing fmode through sysfs, and validating old/new quattro behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-max.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-max.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-max.h

Purpose: declares ddbridge MAX support entry points used by the core.

Important APIs/types/functions: `ddb_lnb_init_fmode()` changes link-level LNB frontend emulation mode; `ddb_fe_attach_mxl5xx()` attaches MXL5xx MAX frontends; `ddb_fe_attach_mci()` attaches MCI/SX8 frontends based on port type.

Control flow: included by `ddbridge-core.c` for frontend attachment and sysfs fmode changes, and implemented by `ddbridge-max.c`.

State and persistence: the header declares no state; implementations mutate `struct ddb_link.lnb`.

Dependencies/integration: includes `ddbridge.h` for `struct ddb`, `ddb_link`, and `ddb_input`.

Risks and test signals: signature drift breaks core builds. Runtime validation belongs to MAX frontend attach and fmode/LNB tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-max.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-mci.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-mci.c

Purpose: implements the generic ddbridge microcode interface used by MCI frontends such as MAX SX8. It serializes commands to a shared firmware block and creates DVB frontend instances backed by MCI state.

Important APIs/types/functions: `ddb_mci_cmd()` sends a full `struct mci_command` and reads `struct mci_result`; `ddb_mci_config()` writes SX8 TS config; `ddb_mci_attach()` allocates per-frontend state and shared `mci_base`. Internal `mci_reset()`, `_mci_cmd_unlocked()`, `mci_handler()`, and `match_base()` manage reset, command execution, IRQ completion, and base sharing.

Control flow: attach creates or reuses a shared base keyed by link or port, installs IRQ 0 completion, resets firmware, runs optional base/instance init, copies frontend ops, and returns the frontend. Commands take `mci_lock`, write command words, set start and done-interrupt bits, wait up to one second, then read result words.

State and persistence: `mci_list` stores shared bases for active frontends. `mci_base` holds the link, completion, locks, count, key, and type; `mci` stores frontend, demod, tuner, and number. All state is runtime-only.

Dependencies/integration: uses ddbridge link MMIO helpers, MCI register/protocol definitions, and frontend configs supplied by `ddbridge-sx8.c`.

Risks and test signals: command timeout, leaked shared bases, incorrect reference counts, and concurrent tuner/MCI locking are key risks. Test with multiple SX8 frontend opens, simultaneous tune requests, module unload after partial attach, firmware reset failure, and status command timeout injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-mci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-mci.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-mci.h

Purpose: defines the ddbridge MCI protocol, result/command layouts, shared state structures, frontend configuration contract, and public MCI APIs.

Important APIs/types/functions: constants define MCI control, command, result, SX8 TS config, demod statuses, commands, and status values. `struct mci_command` and `struct mci_result` model firmware payloads for DVB-S/S2 search, IQ modes, input enable, signal info, and IQ samples. `struct mci_base`, `struct mci`, and `struct mci_cfg` define shared and per-frontend state. Public APIs are `ddb_mci_cmd()`, `ddb_mci_config()`, and `ddb_mci_attach()`.

Control flow: consumers fill `mci_cfg` with frontend ops and optional init callbacks, then call attach; later frontend ops issue commands through `ddb_mci_cmd()`.

State and persistence: structures describe runtime state only; firmware state exists in hardware and is controlled by commands.

Dependencies/integration: declares `ddb_max_sx8_cfg` from `ddbridge-sx8.c` and depends on DVB frontend and ddbridge core types via included context.

Risks and test signals: bitfield/layout correctness is critical because command structs are written directly as `u32` words. Test by verifying firmware responses for all command types, lock/status transitions, IQ mode configuration, and endian-sensitive fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-mci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-regs.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-regs.h

Purpose: centralizes ddbridge MMIO register offsets and bit definitions for SPI, GPIO, board control, interrupts, temperature monitor, I2C, DMA/TS, CI, and LNB command blocks.

Important APIs/types/functions: register macros include `SPI_CONTROL`, `GPIO_*`, `BOARD_CONTROL`, `INTERRUPT_*`, `MSI*_ENABLE`, `TEMPMON_*`, `I2C_*`, `TS_CONTROL*`, `DMA_BUFFER_*`, `CI_*`, and `LNB_*`. Parameterized macros derive per-I/O or per-CI offsets.

Control flow: no executable flow. These constants drive all MMIO in core, main, I2C, MAX, and CI paths.

State and persistence: no state; constants represent hardware layout.

Dependencies/integration: included by ddbridge C files that access hardware registers.

Risks and test signals: wrong offsets or bit masks can corrupt unrelated hardware functions. Test through register-level smoke tests: interrupts enable/ack, I2C transfer, DMA start/stop, CI access, temp monitor, and LNB DiSEqC commands on supported board revisions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-regs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-sx8.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-sx8.c

Purpose: implements the DVB frontend behavior for Digital Devices MAX SX8 MCI hardware. It allocates tuners/demods, starts DVB-S/S2/S2X searches, handles IQ modes, reports status/strength/CNR, and exports an `mci_cfg` used by `ddbridge-max.c`.

Important APIs/types/functions: `struct sx8_base` extends `mci_base` with tuner use counts, gain modes, LDPC bitrate accounting, demod use bitmap, IQ mode, burst size, and direct mode. `struct sx8` extends `mci` with lock/start state and last signal info. Key ops are `set_parameters()`, `start()`, `start_iq()`, `stop()`, `read_status()`, `tune()`, `set_input()`, and `release()`. `ddb_max_sx8_cfg` supplies ops and sizes.

Control flow: tuning stops any previous search, derives IQ mode from stream ID, chooses TS config, reserves a demod and LDPC budget under `tuner_lock`, enables tuner input, sends MCI search or IQ commands, then polling reads status and signal info. Stop sends MCI stop, disables IQ output, releases tuner/demod accounting, and restores normal TS config.

State and persistence: shared base state tracks all active SX8 frontends on the link. Per-frontend state tracks selected tuner/demod, started flag, and signal cache. No durable persistence.

Dependencies/integration: depends on MCI command API, ddbridge MMIO helpers, DVB frontend property cache, and MAX attach wrapper for LNB operations.

Risks and test signals: demod allocation and LDPC bitrate limits can reject valid workloads or oversubscribe firmware; IQ mode excludes other demods; release must balance shared base count. Test concurrent multi-tuner tuning, high-symbol-rate transponders, multistream stream IDs, IQ modes, stop/re-tune loops, signal stat reads, and module unload after multiple frontends.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge-sx8.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge.h

Purpose: is the main shared header for the ddbridge driver. It defines versioning, limits, board/link/port/tuner constants, register map metadata, device identity structures, DMA and DVB state, I2C adapters, ports, LNB state, IRQ slots, links, the top-level device object, and exported core lifecycle APIs.

Important APIs/types/functions: important structs are `ddb_regset`, `ddb_regmap`, `ddb_ids`, `ddb_info`, `ddb_dma`, `ddb_dvb`, `ddb_ci`, `ddb_io`/input/output aliases, `ddb_i2c`, `ddb_port`, `ddb_lnb`, `ddb_irq`, `ddb_link`, and `ddb`. Constants define maximum adapters/ports/links and tuner/CI classes. Prototypes declare flash read, IRQ handlers, port/buffer/device lifecycle, `ddb_init()`, `ddb_unmap()`, and module-level core init/exit helpers.

Control flow: not executable, but all ddbridge C files consume these contracts to share state and call across modules.

State and persistence: describes in-memory runtime state only. Persistent hardware identities are read into `ddb_ids`; durable flash is only read through declared APIs.

Dependencies/integration: includes Linux PCI, I2C, interrupt, workqueue, DVB, demux, CA, net, and ringbuffer headers.

Risks and test signals: structure layout and constants affect all driver modules; changing limits or class/type constants can break array indexing and frontend dispatch. Compile all ddbridge objects and test representative board classes: tuner, CI, loop, MAX, and MCI.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/ddbridge/ddbridge.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dm1105/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/dm1105/Kconfig

Purpose: declares the `DVB_DM1105` kernel configuration option for SDMC DM1105 PCI DVB cards such as DvbWorld 2002.

Important APIs/types/functions: option is tristate and depends on `DVB_CORE`, `PCI`, `I2C`, `I2C_ALGOBIT`, `HAS_IOPORT`, and `RC_CORE`. With media subdriver autoselect it selects frontend/tuner helpers including `DVB_PLL`, `DVB_STV0299`, `DVB_STV0288`, `DVB_STB6000`, `DVB_CX24116`, `DVB_SI21XX`, `DVB_DS3000`, and `DVB_TS2020`.

Control flow: Kconfig controls whether `dm1105.o` can be built and whether dependent demod/tuner modules are selected automatically.

State and persistence: no runtime state.

Dependencies/integration: matches `dm1105.c` dependencies: PCI, I/O port access, I2C including bit-banged GPIO, DVB core, and RC core.

Risks and test signals: missing selects cause frontend attach failures at runtime; overbroad dependencies can expose uncompilable combinations. Test with `allyesconfig`, `allmodconfig`, and `COMPILE_TEST`-like build matrix for the media PCI subtree.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dm1105/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dm1105/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/dm1105/Makefile

Purpose: builds the DM1105 driver object when `CONFIG_DVB_DM1105` is enabled.

Important APIs/types/functions: `obj-$(CONFIG_DVB_DM1105) += dm1105.o` and `ccflags-y += -I $(srctree)/drivers/media/dvb-frontends`.

Control flow: participates in Kbuild only; no runtime behavior.

State and persistence: no state.

Dependencies/integration: adds include path for DVB frontend headers used directly by `dm1105.c`.

Risks and test signals: stale include flags or object names break compilation. Test via modular and built-in builds with `CONFIG_DVB_DM1105=m/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dm1105/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dm1105/dm1105.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/dm1105/dm1105.c

Purpose: implements a DVB PCI driver for SDMC DM1105-based satellite cards. It handles PCI setup, port I/O registers, DMA TS capture, DVB demux/net/frontend registration, hardware and GPIO/bit-banged I2C, LNB voltage control, infrared remote input, and board autodetection/override.

Important APIs/types/functions: `struct dm1105_dev` holds PCI, IR, DVB, I2C, IRQ/workqueue, DMA, and lock state. Board metadata lives in `dm1105_boards[]` and `dm1105_subids[]`. Key functions include GPIO helpers, `dm1105_i2c_xfer()`, `dm1105_set_voltage()`, DMA map/unmap, feed start/stop, `dm1105_dmx_buffer()`, `dm1105_irq()`, IR init/exit, `dm1105_hw_init/exit()`, `frontend_init()`, `dm1105_probe()`, and `dm1105_remove()`.

Control flow: probe selects a board from module parameter or PCI subsystem IDs, enables PCI/I/O/DMA, initializes hardware and both I2C adapters, registers DVB adapter/demux/frontends/net, attaches a board-appropriate demod/tuner chain, creates an IR device, workqueue, and shared IRQ. TS IRQs update write pointers and queue software filtering; IR IRQs schedule key emission. Feed users enable/disable TS interrupts.

State and persistence: runtime state includes DMA buffer pointers, write pointers, packet error counters, full TS user count, board number, frontend pointer, I2C adapters, and RC device. MAC is read from EEPROM but not persisted by the driver.

Dependencies/integration: integrates PCI I/O port APIs, DMA coherent allocation, Linux DVB core, many frontend/tuner modules, I2C core/bit algo, RC core, and workqueues.

Risks and test signals: risks include unchecked `dm1105_dma_map()` return in hardware init, long busy-wait I2C delays, DMA wrap copying into extra buffer space, IR registration unwind gaps, and removal ordering. Test with each supported board type, frontend attach fallbacks, TS streaming, packet error reset path, IR key events, card module parameter, EEPROM MAC read, and probe/remove fault injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dm1105/dm1105.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/Kconfig

Purpose: declares `VIDEO_DT3155` for the DataTranslation DT3155 frame grabber.

Important APIs/types/functions: tristate option depends on `PCI` and `VIDEO_DEV`, and selects `VIDEOBUF2_DMA_CONTIG`.

Control flow: enables building `dt3155.o` and ensures contiguous DMA videobuf2 support is present.

State and persistence: no runtime state.

Dependencies/integration: matches `dt3155.c` use of PCI, V4L2, and vb2 DMA-contig.

Risks and test signals: missing dependencies would surface as build failures. Test with `CONFIG_VIDEO_DT3155=m/y` in media build configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/Makefile

Purpose: builds the DT3155 frame-grabber driver object.

Important APIs/types/functions: `obj-$(CONFIG_VIDEO_DT3155) += dt3155.o`.

Control flow: Kbuild-only.

State and persistence: no state.

Dependencies/integration: tied to the `VIDEO_DT3155` Kconfig option.

Risks and test signals: object naming or config mismatch breaks builds. Test by enabling the option as module and built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/dt3155.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/dt3155.c

Purpose: implements a V4L2 PCI frame-grabber driver for DT3155 hardware. It initializes MMIO and internal IIC registers, exposes a grayscale capture node, manages videobuf2 DMA-contiguous queues, handles frame interrupts, and supports input/standard selection.

Important APIs/types/functions: internal IIC helpers read/write/wait on indirect registers. vb2 ops are `dt3155_queue_setup`, `dt3155_buf_prepare`, `dt3155_start_streaming`, `dt3155_stop_streaming`, and `dt3155_buf_queue`. IRQ handler `dt3155_irq_handler_even()` completes current buffers and programs the next DMA addresses. V4L2 ops provide querycap, format, standard, and input controls. PCI lifecycle is `dt3155_probe()`/`dt3155_remove()`.

Control flow: probe allocates `dt3155_priv`, registers a V4L2 device, initializes queue/video device state, enables PCI and maps BAR0, initializes board LUTs/ADC registers, requests IRQ, and registers `/dev/video*`. Streaming programs even/odd DMA starts into one planar GREY buffer and enables field interrupts. IRQ completion swaps buffers from `dmaq`; stop disables capture and returns queued buffers with error.

State and persistence: `dt3155_priv` stores current buffer, queue, selected input, standard, dimensions, sequence, MMIO base, and cached CSR/config values. No durable state.

Dependencies/integration: depends on PCI, V4L2 core, vb2 DMA-contig, interrupt handling, and DT3155 register definitions in `dt3155.h`.

Risks and test signals: risks include assuming `curr_buf` exists at stream start, DMA address arithmetic by width for odd fields, busy-wait IIC timing, buffer completion under IRQ spinlock, and format setters that cannot change format. Test with v4l2-compliance, streaming with multiple buffers, PAL/NTSC standard changes while idle/busy, input switching, IRQ sharing, and remove during idle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/dt3155.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/dt3155.h -->
# sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/dt3155.h

Purpose: defines DT3155 driver constants, register offsets, bit masks, version strings, and the private device state structure.

Important APIs/types/functions: MMIO offsets cover DMA starts/strides, pixel format, FIFO, CSR, interrupt, masks, IIC control. Internal IIC register indexes cover CSR/config, ID, clipping, AD/PM LUTs. Bit masks define capture, FIFO, interrupt, IIC, CSR2, config, AD command, and board ID values. `struct dt3155_priv` holds V4L2/vb2/PCI/buffer/lock/format/MMIO state.

Control flow: consumed by `dt3155.c` for all board programming and state management.

State and persistence: declares runtime state fields but no storage itself.

Dependencies/integration: includes PCI, interrupt, V4L2 device/video, and vb2 V4L2 headers.

Risks and test signals: bit definitions are hardware-contract critical. Test through board ID validation, interrupt flag handling, DMA programming, input selection, and compile checks for all included media APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/dt3155/dt3155.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/Kconfig

Purpose: is the top-level Intel media PCI Kconfig menu fragment. It sources IPU3, IPU6, and IVSC submenus and declares the `IPU_BRIDGE` helper library.

Important APIs/types/functions: `IPU_BRIDGE` is tristate, depends on ACPI and I2C, and documents support for Windows-shipped systems needing synthetic firmware nodes for IPU camera sensors.

Control flow: Kconfig inclusion controls which Intel IPU drivers and bridge helper are available.

State and persistence: no runtime state.

Dependencies/integration: connects `ipu-bridge.c` to consumers such as ipu3-cio2 and atomisp, while sourcing additional Intel media driver families.

Risks and test signals: bridge must be selectable for drivers that call its exported symbols. Test Kconfig combinations where IPU3 is built with bridge built-in/module/off and where ACPI or I2C are unavailable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/Makefile

Purpose: defines Kbuild objects and subdirectories for Intel media PCI drivers.

Important APIs/types/functions: builds `ipu-bridge.o` for `CONFIG_IPU_BRIDGE`, always descends into `ipu3/` and `ivsc/`, and descends into `ipu6/` when `CONFIG_VIDEO_INTEL_IPU6` is enabled.

Control flow: build-system only.

State and persistence: no state.

Dependencies/integration: aligns top-level Intel Kconfig options with actual objects and subdirectories.

Risks and test signals: incorrect object/subdir gating breaks symbol availability or builds unnecessary code. Test with modular and built-in combinations of IPU bridge, IPU3, IPU6, and IVSC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu-bridge.c -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu-bridge.c

Purpose: creates software-node firmware graphs for Intel IPU camera sensors on ACPI systems whose firmware lacks native fwnode graph data. It also handles IVSC/MEI CSI routing and optional VCM lens instantiation.

Important APIs/types/functions: exported namespace APIs are `ipu_bridge_parse_ssdb()`, `ipu_bridge_instantiate_vcm()`, and `ipu_bridge_init()`. Static data lists supported sensor ACPI HIDs and link frequencies, upside-down DMI quirks, property names, VCM types, and IVSC ACPI IDs. Key helpers discover IVSC devices, read SSDB buffers, parse rotation/orientation, create property entries and software nodes, register node groups, connect sensors, defer until IVSC is ready, and unregister on failure.

Control flow: consumer IPU drivers call `ipu_bridge_init()` with a sensor-fwnode parser. If the IPU already has a graph, bridge exits. Otherwise it waits for IVSC readiness, registers an IPU HID software node, iterates supported sensor HIDs, parses SSDB, creates sensor/IPU/IVSC/VCM graph nodes, attaches secondary fwnodes to ACPI devices, and sets the IPU secondary fwnode. Sensor drivers may call `ipu_bridge_instantiate_vcm()` to queue work that creates an I2C VCM client with runtime-PM linkage.

State and persistence: allocated `struct ipu_bridge` and software nodes intentionally survive like device-side firmware description during driver lifetime; VCM clients may persist across module reloads. ACPI and device references are held and released by unregister paths.

Dependencies/integration: integrates ACPI, DMI, I2C, platform bus, MEI client bus, PM runtime, software nodes, V4L2 fwnode parsing, and media IPU bridge headers.

Risks and test signals: risks include fwnode lifetime ownership, recursive graph checks, IVSC device readiness/defer logic, SSDB layout assumptions, DMI quirks, and asynchronous VCM creation races. Test on systems with/without existing graphs, with IVSC present/absent, with supported sensors and VCMs, across module reload, and by verifying media graph endpoints, lane counts, link frequencies, orientation, and runtime PM links.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu-bridge.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/Kconfig

Purpose: declares `VIDEO_IPU3_CIO2`, the Intel IPU3 CIO2 CSI-2 receiver driver option.

Important APIs/types/functions: tristate option depends on `VIDEO_DEV`, `PCI`, `ACPI || COMPILE_TEST`, `X86`, and a permissive `IPU_BRIDGE || !IPU_BRIDGE` expression. It selects `MEDIA_CONTROLLER`, `VIDEO_V4L2_SUBDEV_API`, `V4L2_FWNODE`, and `VIDEOBUF2_DMA_SG`.

Control flow: controls whether the IPU3 CIO2 PCI capture driver is built.

State and persistence: no runtime state.

Dependencies/integration: pairs with `intel/ipu3/Makefile` and may use IPU bridge support depending on config and platform.

Risks and test signals: dependency expression must permit valid build combinations while ensuring required media APIs. Test with IPU bridge built-in/module/off and IPU3 built-in/module, especially symbol resolution for bridge namespace users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/Makefile

Purpose: builds the IPU3 CIO2 object when enabled.

Important APIs/types/functions: `obj-$(CONFIG_VIDEO_IPU3_CIO2) += ipu3-cio2.o`.

Control flow: Kbuild-only.

State and persistence: no state.

Dependencies/integration: tied to `VIDEO_IPU3_CIO2` in the sibling Kconfig.

Risks and test signals: object/config mismatch breaks IPU3 builds. Test module and built-in builds of `CONFIG_VIDEO_IPU3_CIO2`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/pci/intel/ipu3/Makefile -->
