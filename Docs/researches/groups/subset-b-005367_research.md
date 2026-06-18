# Research: subset-b-005367

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qmc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qmc.c

## Purpose
Implements the Freescale CPM1/QE QMC multichannel controller as a platform driver and as an exported channel API for child protocol drivers. It binds to `fsl,cpm1-scc-qmc` and `fsl,qe-ucc-qmc`, configures SCC/UCC QMC mode, programs TSA time-slot tables, owns shared DPRAM/MURAM parameter areas, and exposes QMC channel operations for HDLC and transparent modes.

## Important APIs, Types, and Functions
- Internal state centers on `struct qmc` and `struct qmc_chan`. `struct qmc` owns SCC/UCC registers, SCC PRAM, DPRAM, DMA-coherent BD and interrupt tables, TSA serial handle, channel list, and channel lookup array. `struct qmc_chan` owns mode, time-slot masks, Tx/Rx BD rings, completion descriptors, counters, and stop/halt flags.
- Exported channel API: `qmc_chan_get_info()`, `qmc_chan_get_ts_info()`, `qmc_chan_set_ts_info()`, `qmc_chan_set_param()`, `qmc_chan_write_submit()`, `qmc_chan_read_submit()`, `qmc_chan_stop()`, `qmc_chan_start()`, `qmc_chan_reset()`, phandle/child lookup helpers, and devres variants.
- Hardware setup functions include `qmc_init_resources()`, `qmc_qe_soft_qmc_init()`, `qmc_init_tsa()`, `qmc_setup_chan()`, `qmc_setup_ints()`, `qmc_init_xcc()`, and `qmc_finalize_chans()`.
- Interrupt path is `qmc_irq_handler()` -> `qmc_irq_gint()` -> `qmc_chan_write_done()` / `qmc_chan_read_done()` plus underrun/busy handling.

## Control Flow
Probe allocates `struct qmc`, gets the TSA serial phandle, maps CPM1 or QE resources, optionally loads Soft-QMC firmware for QE, parses channel child nodes, allocates DMA-coherent BD and interrupt rings, initializes QMC global parameters and TSA tables, initializes all channel parameter areas and BDs, initializes SCC/UCC, requests IRQ, enables global interrupts, force-stops channels, enables SCC/UCC Tx/Rx, stores drvdata, then populates child devices.

Per-transfer control flow is ring-based. Submitters write DMA address/length and callbacks into the next BD, set ownership bits with a write barrier, optionally poll the Tx channel, and advance the free pointer. Interrupt completion walks done pointers while hardware ownership is clear, clears the software-owned `UB` marker, drops the lock around callbacks, then advances. Rx busy interrupts may reset receive state immediately if BDs are pending or mark the channel halted for restart on the next submit.

Start/stop is serialized by `ts_lock`, with direction-specific `rx_lock`/`tx_lock`. Stop sends CPM/QE channel commands, marks stopped, and disables TSA entries once both directions are stopped for shared 64-entry tables. Start enables TSA entries, sets transparent sync if needed, reloads receiver state or enables transmitter state, and rolls back the other direction on partial failure.

## State and Persistence
Persistent runtime state is in devm-managed `qmc`, channel objects, coherent BD/int tables, SCC PRAM, DPRAM, and hardware registers. Channel time-slot masks are mutable only while affected directions are stopped. `nb_tx_underrun`, `nb_rx_busy`, `rx_pending`, `is_rx_halted`, and stop flags survive until reset/remove. No file persistence exists. Firmware state may persist in QE firmware subsystem and is checked before upload.

## Dependencies and Integration Points
Depends on CPM/QE support, `soc/fsl/qe/qmc.h`, `ucc_slow.h`, QE commands/MURAM helpers, CPM commands, firmware loader, DT child nodes, and local `tsa.h`. QMC is tightly integrated with TSA: time-slot capacity comes from `tsa_serial_get_info()`, SCC/UCC connection comes through `tsa_serial_connect()`, and QE UCC numbers come from `tsa_serial_get_num()`. Child drivers bind below QMC via `devm_of_platform_populate()` and use exported QMC channel handles.

## Risks
- Register programming is endian-sensitive and hardware-specific; wrong compatible data or resource layout can corrupt PRAM/DPRAM.
- `qmc_remove()` and some error labels call `qmc_setbits32(..., 0)` when disabling Tx/Rx, which is a no-op; intended clearing would need `qmc_clrbits32()`. This is a behavioral risk if remove/error cleanup depends on disabling the controller.
- Callbacks run from IRQ context after locks are dropped, so consumers must not sleep and must tolerate reentrancy.
- `qmc_chan_set_ts_info()` correctly requires stopped directions for changed masks; callers that race start/stop paths must respect the exported API locking contract.
- Firmware loading validates size/header but still depends on platform-supplied firmware identity and QE global firmware state.
- BD ring capacity is fixed at 8 Tx and 8 Rx descriptors per channel; high-latency consumers can hit `-EBUSY`.

## Test Signals
Useful tests are DT probe with both CPM1 and QE compatibles, phandle lookup deferral, invalid channel id/mode/timeslot masks, 32+32 versus 64 shared TSA tables, HDLC parameter validation, Tx/Rx ring wrap and callback ordering, stop/start rollback paths, Soft-QMC firmware load failure paths, IRQ queue overflow and Rx busy recovery, and remove/error cleanup confirming controller disable behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/qmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/tsa.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/tsa.c

## Purpose
Provides the CPM1/QE Time Slot Assigner platform driver and exported serial-handle API. It maps SI registers and SI RAM, parses TDM routing from device tree, programs CPM1 or QE SI RAM entries and mode registers, manages TDM clocks, and lets QMC/other clients connect serial endpoints to TSA and query per-serial rates/time-slot counts.

## Important APIs, Types, and Functions
- Internal types: `struct tsa`, `struct tsa_tdm`, `struct tsa_entries_area`, and embedded `struct tsa_serial`.
- Exported APIs: `tsa_serial_get_num()`, `tsa_serial_connect()`, `tsa_serial_disconnect()`, `tsa_serial_get_info()`, `tsa_serial_get_byphandle()`, `tsa_serial_put()`, and `devm_tsa_serial_get_byphandle()`.
- Key setup helpers: CPM/QE endian accessors, `tsa_*_serial_connect()`, SI RAM area initializers, `tsa_*_add_entry()`, `tsa_of_parse_tdm_route()`, `tsa_of_parse_tdms()`, `tsa_init_si_ram()`, `tsa_cpm1_setup()`, and `tsa_qe_setup()`.

## Control Flow
Probe allocates `struct tsa`, determines CPM1 versus QE from match data, initializes serial ids, maps `si_regs` and `si_ram`, fills SI RAM with terminal entries, parses all TDM child nodes, and writes final SI mode/global enable registers. Parsing first validates all child `reg` ids, then for each TDM reads signal timing flags, gets/enables required clocks, assigns QE start address fields, parses Rx and Tx route arrays, appends SI RAM entries, and accumulates serial info.

The exported phandle getter resolves a fixed-args phandle with one serial id, verifies the provider node matches the TSA driver, obtains the platform device/drvdata, bounds-checks the serial index, and returns a pointer to the embedded serial while holding the platform device reference until `tsa_serial_put()`.

## State and Persistence
The driver persists TDM enable flags, clock handles, programmed SI RAM entries, serial rates, bit rates, and number of assigned Rx/Tx time slots for the life of the platform device. It has no disk persistence. Register read/modify/write sequences for connection state are protected by `tsa->lock`.

## Dependencies and Integration Points
Depends on CPM/QE DT binding constants, Linux common clock framework, OF/platform APIs, `soc/fsl/qe/ucc.h` for QE muxing, and consumers such as QMC. Device tree must supply `si_regs`, `si_ram`, TDM children, clock names (`l1*` on CPM1, short names on QE), and `fsl,{rx,tx}-ts-routes` arrays.

## Risks
- The error and remove paths for `l1tsync_clk`/`l1tclk_clk` call `clk_disable_unprepare()` and `clk_put()` on the Rx clock members instead of the Tx members, which can leak or double-release clock references.
- Route arrays are accepted as count/serial pairs; malformed counts can exhaust SI RAM and fail probe, while zero counts are not explicitly special-cased.
- QE/CPM1 entry layout differs, making version match data critical.
- The API returns embedded serial pointers with provider device references; consumers must always call the matching put or devm helper.

## Test Signals
Probe with CPM1 and QE compatible data, invalid TDM ids, missing clocks, shared/common pin cases, SI RAM exhaustion, unsupported serial ids, route arrays with odd length, phandle deferral before provider drvdata, connect/disconnect register changes, and clock cleanup on parse failure/remove are the main signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/tsa.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/tsa.h -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/tsa.h

## Purpose
Private/local TSA management header for QE/CPM SoC drivers. It declares the opaque TSA serial handle, serial information shape, and exported helper prototypes used by consumers such as QMC.

## Important APIs, Types, and Functions
- Opaque `struct tsa_serial`.
- `struct tsa_serial_info` exposes Rx/Tx frame-sync rates, bit rates, and assigned time-slot counts.
- Lookup/lifetime helpers: `tsa_serial_get_byphandle()`, `tsa_serial_put()`, `devm_tsa_serial_get_byphandle()`.
- Control/query helpers: `tsa_serial_connect()`, `tsa_serial_disconnect()`, `tsa_serial_get_info()`, and `tsa_serial_get_num()`.

## Control Flow
There is no executable control flow. The header defines the contract implemented by `tsa.c`: consumers acquire a serial from a DT phandle, connect it to TSA, query timing/capacity information, optionally get a QE UCC number, and release it.

## State and Persistence
No state is stored here. State lives in `tsa.c` provider objects and consumer-held serial pointers.

## Dependencies and Integration Points
Includes `linux/types.h` and forward declares `struct device_node` and `struct device` to keep consumers lightweight. It is included by `qmc.c` and likely intended only for this local driver family rather than a public UAPI.

## Risks
Because `struct tsa_serial` is opaque, all consumers must respect provider lifetime helpers. Misusing non-devm lookup without `tsa_serial_put()` leaks the platform device reference.

## Test Signals
Compile coverage for all prototypes, consumer use of devm and non-devm lookup paths, and ABI consistency between this header and exported symbols in `tsa.c`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/tsa.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc.c

## Purpose
Provides shared QUICC Engine UCC mux and clock routing helper APIs used by UCC fast/slow drivers, TSA/QMC users, Ethernet, serial, and TDM clients. It programs QE mux registers for MII management, UCC speed type, grant/breakpoint/TSA selection, UCC Rx/Tx clocks, and TDM clock/sync sources.

## Important APIs, Types, and Functions
- Exported APIs: `ucc_set_qe_mux_mii_mng()`, `ucc_set_type()`, `ucc_mux_set_grant_tsa_bkpt()` via macros in headers, `ucc_set_qe_mux_rxtx()`, `ucc_set_tdm_rxtx_clk()`, and `ucc_set_tdm_rxtx_sync()`.
- Internal mapping helpers translate UCC number to CMXUCR register/shift and TDM number/direction/clock to mux bit values.

## Control Flow
Each exported setter validates UCC/TDM number and direction, translates enum clock values to hardware bit fields, and updates QE mux registers with `qe_clrsetbits_be32()` or bit set/clear helpers. MII management and GUEMR updates use `cmxgcr_lock` or direct 8-bit GUEMR access where appropriate.

## State and Persistence
State is hardware register state in global `qe_immr->qmx` and UCC GUEMR registers. No private heap state exists. Changes persist until another driver or firmware rewrites the mux.

## Dependencies and Integration Points
Depends on global QE IMMR mapping, QE register helpers, `cmxgcr_lock`, and UCC/QE clock enum definitions. Fast/slow UCC init and TSA connection code call these helpers.

## Risks
- Invalid clock/UCC combinations return `-ENOENT` or `-EINVAL`; callers must handle these as configuration errors.
- Most mux updates outside `cmxgcr_lock` are not locally serialized, so cross-driver concurrent configuration of the same mux fields could race.
- Hardware clock mapping tables are dense and easy to regress when adding SoC variants.

## Test Signals
Unit-style tests can exercise table mappings for all UCC/TDM/clock/direction combinations through mocked registers. Integration tests should boot QE devices using NMSI and TSA modes, reject invalid clock combinations, and verify mux register fields.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc_fast.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc_fast.c

## Purpose
Implements the QE UCC Fast support library for clients such as Ethernet. It validates caller-supplied fast UCC configuration, maps UCC registers, allocates QE MURAM virtual FIFOs, programs GUMR/FIFO/interrupt/mux registers, and exports enable/disable/dump/on-demand/free helpers.

## Important APIs, Types, and Functions
- Exported: `ucc_fast_dump_regs()`, `ucc_fast_get_qe_cr_subblock()`, `ucc_fast_transmit_on_demand()`, `ucc_fast_enable()`, `ucc_fast_disable()`, `ucc_fast_init()`, and `ucc_fast_free()`.
- Uses `struct ucc_fast_info` as caller-provided configuration and returns `struct ucc_fast_private`.

## Control Flow
`ucc_fast_init()` validates UCC number, MRBLR alignment, and FIFO thresholds/alignment; allocates private state; ioremaps registers; sets fast type; builds GUMR from flags; allocates Tx/Rx virtual FIFO blocks from MURAM; writes FIFO registers; configures grant/breakpoint/TSA and clock/sync muxing; writes interrupt mask; clears pending events; and returns the initialized private object. Failure paths call `ucc_fast_free()`.

## State and Persistence
State is split between allocated `struct ucc_fast_private`, ioremapped UCC registers, MURAM FIFO offsets, and enabled flags. `ucc_fast_free()` releases MURAM and unmaps registers. Hardware configuration persists until changed or reset.

## Dependencies and Integration Points
Depends on QE MURAM allocation, shared UCC mux helpers, QE register layout, and caller-owned `ucc_fast_info`. TSA mode branches into TDM clock/sync configuration; NMSI mode uses direct UCC Rx/Tx clock muxing.

## Risks
- The caller owns `ucc_fast_info`; it must outlive the private object.
- Register/MURAM allocation order makes cleanup correctness important; partial failures rely on sentinel offsets initialized to `-1`.
- Invalid clock mappings are detected late, after register and MURAM work, but cleanup handles them.

## Test Signals
Alignment/threshold validation, allocation failure at each step, NMSI and TSA clock paths, enable/disable register bit changes, transmit-on-demand write, dump coverage, and leak checks around repeated init/free are useful.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc_fast.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc_slow.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc_slow.c

## Purpose
Implements the QE UCC Slow support library for UART/serial-like clients. It sets UCC slow mode, allocates PRAM and BD rings in QE MURAM, initializes GUMR and function-code registers, configures muxing/clocks, issues QE init commands, and exports Tx control and enable/disable helpers.

## Important APIs, Types, and Functions
- Exported: `ucc_slow_get_qe_cr_subblock()`, `ucc_slow_graceful_stop_tx()`, `ucc_slow_stop_tx()`, `ucc_slow_restart_tx()`, `ucc_slow_enable()`, `ucc_slow_disable()`, `ucc_slow_init()`, and `ucc_slow_free()`.
- Caller input is `struct ucc_slow_info`; output is `struct ucc_slow_private`.

## Control Flow
`ucc_slow_init()` validates input, maps registers, allocates PRAM and BD rings, assigns PRAM page to device with `qe_issue_cmd()`, switches UCC type to slow, initializes Rx/Tx BDs with wrap bits, programs GUMR_H/L, BMR/rbase/tbase, configures grant/breakpoint/TSA and NMSI clocks, writes interrupt masks, clears events, issues the requested QE init command, and returns private state. Free releases MURAM and unmaps registers.

## State and Persistence
Private state tracks PRAM, BD base offsets, register pointers, lists, and enabled flags. Hardware state persists in UCC registers and MURAM until reset/free. There is no file persistence.

## Dependencies and Integration Points
Depends on QE command engine, MURAM allocator, UCC mux helpers, and UCC slow register definitions. Clients typically own buffer management above the initialized BD rings.

## Risks
- Caller-owned configuration lifetime is required.
- `qe_issue_cmd()` return values are not checked in all control helpers, so command failures may be silent.
- NMSI clock configuration has hard failure if either clock is invalid; TSA mode expects an external TSA configuration.
- Ring lengths are caller supplied and should be validated by callers beyond allocation success.

## Test Signals
Valid and invalid UCC numbers, MRBLR alignment with/without `rfw`, MURAM allocation failure, Tx/Rx init mode combinations, NMSI clock validation, graceful/stop/restart command issuance, and repeated init/free leak checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/ucc_slow.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/usb.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/usb.c

## Purpose
Small QE helper that selects the QE USB clock source and optionally programs a BRG clock rate. It exports `qe_usb_clock_set()` for USB-related QE drivers.

## Important APIs, Types, and Functions
- `qe_usb_clock_set(enum qe_clock clk, int rate)` maps supported QE clocks/BRGs to `QE_CMXGCR_USBCS_*` values, calls `qe_setbrg()` for BRG clocks, and updates `cmxgcr` under `cmxgcr_lock`.

## Control Flow
The function switches on the requested clock, rejects unsupported values with `-EINVAL`, configures BRG rate when relevant, takes `cmxgcr_lock`, replaces the USB clock select field, releases the lock, and returns success.

## State and Persistence
Only global QE mux register state is changed. There is no private state.

## Dependencies and Integration Points
Depends on global QE IMMR mapping, QE clock definitions, `qe_clock_is_brg()`, `qe_setbrg()`, and `cmxgcr_lock`. It is intended for QE USB controller setup.

## Risks
Unsupported clock values are rejected, but invalid rates for BRGs depend on `qe_setbrg()` behavior. The function assumes QE global registers are already mapped.

## Test Signals
Test every supported clock enum, unsupported enum rejection, BRG rate programming, and cmxgcr field preservation outside `QE_CMXGCR_USBCS`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/qe/usb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/rcpm.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fsl/rcpm.c

## Purpose
Implements the Freescale/NXP QorIQ RCPM wakeup controller platform driver. During PM prepare it scans registered wakeup sources and ORs device-provided `fsl,rcpm-wakeup` bits into IPPDEXPCR wakeup registers, with DT and ACPI support.

## Important APIs, Types, and Functions
- `struct rcpm` stores wakeup cell count, IPPDEXPCR base, and endianness.
- `rcpm_pm_prepare()` is the key PM hook.
- `copy_ippdexpcr1_setting()` implements LS1021A erratum A-008646 workaround through SCFG spare register.
- `rcpm_probe()` maps registers, reads `little-endian` and `#fsl,rcpm-wakeup-cells`, and stores drvdata.

## Control Flow
On suspend prepare, the driver locks wakeup-source iteration, visits each wakeup source with a parent device, reads `fsl,rcpm-wakeup`, filters by phandle in DT mode, ORs all wakeup cells into a local setting array, unlocks, then writes nonzero settings to consecutive IPPDEXPCR registers using the configured endianness. For LS1021A register 1, it mirrors the written bits to SCFG spare register.

## State and Persistence
Runtime state is devm-managed mapping/configuration. Hardware wakeup register bits are OR-only by this driver and persist across suspend preparation until hardware/firmware clears or rewrites them.

## Dependencies and Integration Points
Depends on wakeup source core, OF/ACPI property APIs, platform resources, and optional LS1021A SCFG syscon node. Devices integrate by exposing `fsl,rcpm-wakeup` on their parent.

## Risks
- The driver only ORs bits and does not clear stale wakeup bits; platform firmware or other paths must manage clearing.
- `RCPM_WAKEUP_CELL_MAX_SIZE` bounds the stack arrays; larger DT values would overflow reads if not constrained by bindings.
- ACPI mode assumes only one RCPM controller.
- Missing or malformed wakeup properties are silently skipped.

## Test Signals
Suspend prepare with multiple wakeup sources, DT phandle filtering, little/big endian register writes, LS1021A erratum mirroring, malformed property lengths, ACPI probe, and large cell-count validation are important.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fsl/rcpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fujitsu/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/fujitsu/Kconfig

## Purpose
Defines the Fujitsu SoC driver menu and the `A64FX_DIAG` build option.

## Important APIs, Types, and Functions
No runtime APIs. `config A64FX_DIAG` is a bool option requiring `ARM64` and `ACPI`, with help text describing diagnostic interrupt support for kernel dumps via BMC requests.

## Control Flow
Kconfig selection controls whether `a64fx-diag.o` is built by the Makefile.

## State and Persistence
No runtime state. Build configuration persists in the kernel config.

## Dependencies and Integration Points
Integrates with `drivers/soc/fujitsu/Makefile` through `CONFIG_A64FX_DIAG`.

## Risks
The option is bool-only, so it cannot be built as a module unless changed. It enables a driver whose interrupt handler intentionally panics/NMIs the kernel.

## Test Signals
Kconfig visibility on ARM64+ACPI, hidden state when dependencies are absent, and successful build of `a64fx-diag.o` when enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fujitsu/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fujitsu/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/fujitsu/Makefile

## Purpose
Builds the Fujitsu A64FX diagnostic driver according to Kconfig.

## Important APIs, Types, and Functions
No code APIs. The single rule is `obj-$(CONFIG_A64FX_DIAG) += a64fx-diag.o`.

## Control Flow
Kernel build includes `a64fx-diag.c` only when `CONFIG_A64FX_DIAG=y`.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes the `A64FX_DIAG` Kconfig symbol from the same directory.

## Risks
Low build-system risk; mismatch with Kconfig symbol would omit the driver.

## Test Signals
Compile with `CONFIG_A64FX_DIAG=y` and verify `a64fx-diag.o` is linked.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fujitsu/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fujitsu/a64fx-diag.c -->
# sources/distributed-fs/ceph-client/drivers/soc/fujitsu/a64fx-diag.c

## Purpose
ACPI platform driver for Fujitsu A64FX diagnostic interrupts. It enables a BMC diagnostic interrupt bit and registers an NMI or IRQ handler that intentionally triggers a panic for crash dump collection.

## Important APIs, Types, and Functions
- `struct a64fx_diag_priv` stores MMSC register base, IRQ, and NMI mode.
- `a64fx_diag_probe()` maps registers, obtains IRQ index 1, requests NMI first and IRQ fallback, enables interrupt delivery, clears stale status, and enables BMC diagnostic interrupt.
- `a64fx_diag_remove()` disables/clears hardware and frees NMI/IRQ.
- Handlers are `a64fx_diag_handler_nmi()` and `a64fx_diag_handler_irq()`.

## Control Flow
Probe uses ACPI match `FUJI2007`, maps BAR 0, fetches platform IRQ 1, requests the interrupt with per-CPU/no-balance/no-thread/no-auto-enable flags, enables NMI or IRQ, clears any pending diagnostic status, and sets the enable bit. When triggered, the handler panics through `nmi_panic()` or `panic()`.

## State and Persistence
State is devm-managed private data plus hardware enable/status bits. The diagnostic enable bit persists while the driver is bound and is cleared on remove.

## Dependencies and Integration Points
Requires ACPI platform enumeration, interrupt/NMI APIs, and an MMSC register resource. BMC tooling triggers the hardware diagnostic request.

## Risks
- Interrupt delivery is deliberately fatal; accidental BMC requests panic the system.
- IRQ index is hard-coded to 1.
- `request_nmi()` fallback to normal IRQ changes panic path semantics.
- Uses non-devm `request_nmi()`/`request_irq()` and must free correctly on remove.

## Test Signals
ACPI match/probe, register status clear/enable/disable, NMI success path, IRQ fallback path, remove cleanup, and deliberate diagnostic interrupt causing expected panic path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/fujitsu/a64fx-diag.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/gemini/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/gemini/Makefile

## Purpose
Always builds the Gemini SoC initialization object in this directory.

## Important APIs, Types, and Functions
No runtime APIs. The rule is `obj-y += soc-gemini.o`.

## Control Flow
The object participates in built-in kernel linking whenever the directory is included by the parent build.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates with the Gemini SoC init code in `soc-gemini.c`.

## Risks
The object is unconditional at this directory level; runtime machine compatibility guard in the C file prevents action on non-Gemini systems.

## Test Signals
Build inclusion and no-op boot behavior on non-Gemini machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/gemini/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/gemini/soc-gemini.c -->
# sources/distributed-fs/ceph-client/drivers/soc/gemini/soc-gemini.c

## Purpose
Early Gemini SoC setup that identifies Cortina Gemini hardware and configures BUS2 backplane arbitration defaults through a syscon regmap.

## Important APIs, Types, and Functions
- `gemini_soc_init()` is registered with `subsys_initcall()`.
- Register constants define global ID and arbitration control fields, default burst size, and default high-priority GMAC bits.

## Control Flow
At subsys init, the function returns immediately unless the root compatible is `cortina,gemini`. It looks up `cortina,gemini-syscon`, reads the global word ID, builds the default arbitration value, updates burst/priority fields in `GEMINI_GLOBAL_ARB1_CTRL`, logs SoC/revision/arbitration, and returns.

## State and Persistence
State is only syscon register configuration. It persists until hardware reset or another driver changes it.

## Dependencies and Integration Points
Depends on OF machine compatible, MFD syscon/regmap, and Gemini syscon DT node.

## Risks
Missing syscon returns an initcall error. Arbitration policy is hard-coded to GMAC priority and burst size, so platform-specific tuning requires code or DT changes.

## Test Signals
Boot on Gemini and non-Gemini systems, syscon lookup failure, regmap read/update failure, and verification of final arbitration register bits.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/gemini/soc-gemini.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/hisilicon/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/hisilicon/Kconfig

## Purpose
Defines Hisilicon SoC driver menu and the Kunpeng HCCS driver option.

## Important APIs, Types, and Functions
No runtime APIs. `config KUNPENG_HCCS` is tristate, depends on ACPI, PCC, and ARM64 or compile testing, and describes HCCS health/port/lane power features.

## Control Flow
The symbol gates compilation of `kunpeng_hccs.o`.

## State and Persistence
No runtime state; configuration state is stored in kernel config.

## Dependencies and Integration Points
Requires `ARCH_HISI || COMPILE_TEST` for the menu and integrates with ACPI PCC infrastructure.

## Risks
Correct runtime operation depends on ACPI/PCC firmware support despite compile-test availability.

## Test Signals
Kconfig visibility with dependencies, module and built-in builds, and compile-test on non-HISI architectures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/hisilicon/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/hisilicon/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/hisilicon/Makefile

## Purpose
Builds the Kunpeng HCCS driver when selected.

## Important APIs, Types, and Functions
No runtime APIs. The rule is `obj-$(CONFIG_KUNPENG_HCCS) += kunpeng_hccs.o`.

## Control Flow
Kernel build includes the HCCS object for built-in or module builds according to the tristate symbol.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes `CONFIG_KUNPENG_HCCS` from Kconfig.

## Risks
Low build-rule risk; symbol mismatch would omit the driver.

## Test Signals
Build with `CONFIG_KUNPENG_HCCS=m/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/hisilicon/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/hisilicon/kunpeng_hccs.c -->
# sources/distributed-fs/ceph-client/drivers/soc/hisilicon/kunpeng_hccs.c

## Purpose
ACPI platform driver for Huawei Kunpeng HCCS. It communicates with platform firmware over ACPI PCC mailboxes to discover chip/die/port topology, expose health/status counters through sysfs, and perform supported HCCS lane increase/decrease power-management operations.

## Important APIs, Types, and Functions
- PCC setup: `hccs_get_pcc_chan_id()`, `hccs_register_pcc_channel()`, `hccs_pcc_cmd_send()`, poll/IRQ wait helpers, and version-specific shared-memory fillers.
- Discovery: `hccs_get_dev_caps()`, chip/die/port query helpers, `hccs_get_hw_info()`, and `hccs_init_type_name_maps()`.
- Sysfs: kobject types for port/die/chip, show methods for type, lane mode, enable, current lane, FSM, lane mask, CRC counts, aggregate linked/full-lane status, and misc device attributes.
- PM lane control: `dec_lane_of_type_store()`, `inc_lane_of_type_store()`, idle/full-lane checks, and firmware commands for dec/inc/adapt/retraining.
- Probe/remove: `hccs_probe()` and `hccs_remove()`.

## Control Flow
Probe requires ACPI, obtains match-specific data for `HISI04B1` or `HISI04B2`, initializes a mutex, reads PCC channel id from `_CRS` generic register access size, registers the mailbox channel, verifies PCCT txdone mode and shared memory size, gets capabilities, discovers platform topology through firmware commands, builds type-name maps, and creates a sysfs topology tree under the device.

Every firmware command initializes a request descriptor, writes PCC header and command payload into shared memory, rings the mailbox doorbell, waits by polling or completion IRQ depending on ACPI ID, copies response back, and checks firmware `retStatus`. Sysfs show/store handlers take `hdev->lock` before issuing PCC commands. Lane decrease first verifies all matching ports are idle; lane increase skips work if all matching ports are already full lane and otherwise runs prepare/adapt/retraining sequence.

## State and Persistence
State lives in `struct hccs_dev`: capabilities, chip/die/port arrays, type-name maps, PCC channel, deadline, completion, and mutex. Topology is discovered at probe and exposed via kobjects until remove. Firmware counters and lane state are queried live through PCC. Lane changes persist in hardware/firmware state beyond a sysfs write.

## Dependencies and Integration Points
Depends on ACPI companion/match data, ACPI PCC mailbox, PCCT shared-memory layouts, sysfs/kobject APIs, mailbox completion semantics, and platform firmware implementing the HCCS command protocol described in `kunpeng_hccs.h`.

## Risks
- Firmware protocol, shared-memory size, and PCCT txdone mode must match ACPI ID; mismatches fail probe.
- Sysfs topology uses manual kobject lifetime; partial creation errors must unwind correctly.
- `used_types_show()` assumes `used_type_num > 0`; discovery currently rejects no-port/no-die cases before this, but future changes should preserve that invariant.
- Multi-BD/next-id logic rejects non-increasing `next_id`; malformed firmware can fail discovery.
- Lane decrease/increase sysfs writes can alter interconnect power/performance and rely on firmware idle/adaptation accuracy.

## Test Signals
ACPI-disabled probe rejection, missing `_CRS`, invalid PCC space id, PCCT txdone mismatch for both ACPI IDs, shared memory size mismatch, command timeout, firmware error retStatus, topology with multiple chips/dies/ports, sysfs read coverage, lane PM with unsupported type/busy ports/full-lane ports, and remove after partial sysfs creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/hisilicon/kunpeng_hccs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/hisilicon/kunpeng_hccs.h -->
# sources/distributed-fs/ceph-client/drivers/soc/hisilicon/kunpeng_hccs.h

## Purpose
Defines Kunpeng HCCS driver data models, firmware command IDs, request/response payload structures, PCC descriptor layout, capabilities, and topology objects shared by `kunpeng_hccs.c`.

## Important APIs, Types, and Functions
- Topology/state structures: `hccs_dev`, `hccs_chip_info`, `hccs_die_info`, `hccs_port_info`, `hccs_type_name_map`, and `hccs_mbox_client_info`.
- Version-specific operations: `struct hccs_verspecific_data`.
- Firmware protocol definitions: `enum hccs_subcmd_type`, request parameter structs, `hccs_link_status`, request/response heads, `hccs_fw_inner_head`, `hccs_req_desc`, `hccs_rsp_desc`, and union `hccs_desc`.

## Control Flow
No executable flow. The header establishes the memory layout consumed by PCC command send/receive paths and sysfs topology code.

## State and Persistence
No state is stored in the header. The structs describe in-memory driver state and firmware message layout.

## Dependencies and Integration Points
Assumes Linux kernel types, kobjects, mailbox/PCC types included by the C file, and a 64-byte PCC communication region. It is private to the driver directory.

## Risks
Packed layout is not explicitly requested; the current small integer fields and `u32` data arrays depend on normal kernel ABI alignment matching firmware expectations. `HCCS_DIE_MAX_PORT_ID` avoids 255 because `next_id` loop termination relies on a greater-than check.

## Test Signals
Compile-time size/layout checks for descriptor structures, maximum response/request data calculations, command enum stability, and firmware compatibility for bitfield layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/hisilicon/kunpeng_hccs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/imx/Kconfig

## Purpose
Defines i.MX SoC driver options for i.MX8M and i.MX9 family support.

## Important APIs, Types, and Functions
No runtime APIs. `SOC_IMX8M` and `SOC_IMX9` are tristate options depending on `ARCH_MXC || COMPILE_TEST`, defaulting on ARM64 i.MX builds, and selecting `SOC_BUS`. `SOC_IMX8M` also selects `ARM_GIC_V3` in an ARM multi-v7 condition.

## Control Flow
These symbols gate objects in the Makefile.

## State and Persistence
Kernel configuration only.

## Dependencies and Integration Points
Integrates with `soc-imx8m.o`, `imx93-src.o`, and `soc-imx9.o` build rules. Runtime drivers register SoC bus devices.

## Risks
Tristate SoC identity drivers may need to be available early enough for consumers; defaults target built-in on normal ARCH_MXC ARM64 builds.

## Test Signals
Kconfig dependency visibility, default selection on ARCH_MXC ARM64, compile-test, and object inclusion for each symbol.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/imx/Makefile

## Purpose
Builds legacy ARM i.MX SoC ID code and selected i.MX8M/i.MX9 drivers.

## Important APIs, Types, and Functions
No runtime APIs. Rules: on ARM, `CONFIG_ARCH_MXC` builds `soc-imx.o`; `CONFIG_SOC_IMX8M` builds `soc-imx8m.o`; `CONFIG_SOC_IMX9` builds `imx93-src.o soc-imx9.o`.

## Control Flow
Build inclusion depends on architecture and Kconfig symbols.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes symbols from the directory Kconfig and parent architecture config.

## Risks
The legacy `soc-imx.o` is ARM-only by Makefile guard; ARM64 i.MX identity goes through i.MX8M/i.MX9 paths.

## Test Signals
Build matrix for ARM ARCH_MXC, ARM64 i.MX8M, and ARM64 i.MX9 configurations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/imx93-src.c -->
# sources/distributed-fs/ceph-client/drivers/soc/imx/imx93-src.c

## Purpose
Minimal i.MX93 SRC platform driver that populates child devices under the SRC node.

## Important APIs, Types, and Functions
- `imx93_src_probe()` calls `devm_of_platform_populate()`.
- OF match table contains `fsl,imx93-src`.

## Control Flow
On matching platform probe, children of the SRC node are populated with devm cleanup.

## State and Persistence
No private state. Child platform devices persist while the parent device is bound.

## Dependencies and Integration Points
Depends on OF platform population and DT child nodes for SRC-controlled subdevices.

## Risks
Failure to populate children blocks downstream devices. The driver has no remove hook because devm handles child cleanup.

## Test Signals
Probe with matching DT, child device creation, missing/invalid children no-op behavior, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/imx93-src.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx.c -->
# sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx.c

## Purpose
Legacy/32-bit i.MX SoC bus registration. It identifies the current i.MX/VF SoC from `__mxc_cpu_type`, reads machine model and optional OCOTP/IIM unique ID, formats revision, and registers a `soc_device`.

## Important APIs, Types, and Functions
- `imx_soc_device_init()` is a `device_initcall()`.
- Uses CPU type constants from `soc/imx/cpu.h`, revision from `imx_get_soc_revision()`, syscon regmap lookups for OCOTP/IIM, and `soc_device_register()`.

## Control Flow
The initcall exits if not running on an i.MX CPU. It allocates `soc_device_attribute`, reads root model, maps CPU type to `soc_id` and OCOTP compatible, reads UID in SoC-specific layouts if a regmap is found, formats revision and serial number, registers the SoC device, and frees allocated strings on errors.

## State and Persistence
Registers one SoC bus device and allocated attribute strings. No file persistence. UID/revision are read from hardware fuses/global state.

## Dependencies and Integration Points
Depends on architecture-provided `__mxc_cpu_type`, OF root model, syscon OCOTP/IIM nodes, and SoC bus core.

## Risks
- Missing root `model` fails registration.
- OCOTP lookup failure logs but still registers with serial zero.
- No unregister path for the initcall-created SoC device, which is normal for built-in early SoC identity code.

## Test Signals
CPU-type mapping coverage, UID paths for i.MX7ULP, MX51/MX53, and OCOTP variants, missing OCOTP fallback, allocation failure paths, and expected `/sys/devices/soc0` attributes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx8m.c -->
# sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx8m.c

## Purpose
i.MX8M SoC identity driver. It detects i.MX8MQ/MM/MN/MP machines, reads revision and UID from ATF, OCOTP, or anatop depending on variant, registers a SoC bus device, and optionally creates an `imx-cpufreq-dt` platform device.

## Important APIs, Types, and Functions
- `struct imx8_soc_data` describes per-SoC name, OCOTP compatible, revision callback, and UID callback.
- Revision/UID helpers include `imx8mq_soc_revision_from_atf()`, `imx8mq_soc_revision()`, `imx8mm_soc_revision()`, `imx8m_soc_uid()`, and `imx8mp_soc_uid()`.
- `imx8m_soc_probe()` registers SoC attributes and cpufreq device.
- `imx8_soc_init()` registers the platform driver/device at `device_initcall()`.

## Control Flow
The initcall checks OF machine compatibility and self-registers a platform driver plus simple platform device. Probe allocates attributes/drvdata, reads machine, obtains match data, maps/enables OCOTP clock through `imx8m_soc_prepare()`, reads revision and UID, unprepares OCOTP, formats revision/serial, registers `soc_device`, registers devm cleanup, logs SoC revision, and optionally registers cpufreq platform device with devm unregister.

## State and Persistence
State is devm-managed probe data and registered SoC/cpufreq platform devices. Hardware fuse data is read-only. No file persistence.

## Dependencies and Integration Points
Depends on OF machine matching, SMCCC for i.MX8MQ ATF revision if enabled, OCOTP/anatop syscon mappings, clocks, SoC bus core, and optional `CONFIG_ARM_IMX_CPUFREQ_DT`.

## Risks
- OCOTP clock/map failures fail probe even when partial identity might be possible.
- i.MX8MP serial combines two 64-bit halves; formatting depends on nonzero high half.
- The driver unregisters the platform driver if device registration fails, but a successful simple platform device has no explicit unregister in init path.
- Revision can be `"unknown"` if hardware/ATF provides zero.

## Test Signals
Machine matching for each i.MX8M compatible, ATF supported/unsupported paths, OCOTP/anatop map failures, clock enable failure, UID formatting for i.MX8MP, cpufreq device registration, and `/sys/devices/soc0` attribute verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx8m.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx9.c -->
# sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx9.c

## Purpose
i.MX9 SoC identity driver. It uses an ARM SMCCC call to firmware to retrieve SoC id, revision, and 128-bit UID, then registers a SoC bus device for i.MX93/i.MX94/i.MX95/i.MX952 machines.

## Important APIs, Types, and Functions
- `imx9_soc_probe()` performs SMCCC query and SoC registration.
- `imx9_soc_init()` registers a platform driver and simple platform device at `device_initcall()`.
- Macros decode SoC ID and revision from `res.a1`.

## Control Flow
Init returns unless the OF machine is a supported i.MX9 compatible. It registers the driver and simple platform device. Probe reads root machine, sets family, calls `arm_smccc_smc(IMX_SIP_GET_SOC_INFO)`, checks success, decodes id/revision, formats serial from `a2/a3`, and registers the SoC device.

## State and Persistence
Registers a SoC device with devm-allocated strings. No private long-lived state beyond the registered SoC bus object. UID/revision are firmware-provided.

## Dependencies and Integration Points
Requires ARM SMCCC firmware service, OF machine compatible, platform bus, and SoC bus core.

## Risks
- Failure or absence of the SMCCC service fails probe.
- Revision macro subtracts `0x9` from encoded major; unexpected firmware encodings can produce surprising values.
- No remove/unregister hook is present for registered SoC device.

## Test Signals
Supported compatible matching, SMCCC success/failure, SoC ID decoding for each supported family, UID formatting, missing model property failure, and SoC bus attribute verification.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/imx/soc-imx9.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/Kconfig

## Purpose
Defines IXP4xx SoC driver options for the queue manager and network processor engines.

## Important APIs, Types, and Functions
No runtime APIs. `IXP4XX_QMGR` is a tristate queue manager option. `IXP4XX_NPE` is a tristate NPE option selecting firmware loader and MFD syscon.

## Control Flow
Options are visible when `ARCH_IXP4XX || COMPILE_TEST` and gate corresponding Makefile objects.

## State and Persistence
Kernel configuration only.

## Dependencies and Integration Points
Ethernet and HSS drivers select/use these hardware services. NPE depends on firmware loading and syscon.

## Risks
Queue/NPE are low-level shared services; disabling them breaks dependent network/HSS drivers.

## Test Signals
Kconfig visibility, compile-test builds, module/built-in builds, and dependency selection of `FW_LOADER`/`MFD_SYSCON`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/Makefile

## Purpose
Builds IXP4xx queue manager and NPE drivers according to Kconfig.

## Important APIs, Types, and Functions
No runtime APIs. Rules build `ixp4xx-qmgr.o` for `CONFIG_IXP4XX_QMGR` and `ixp4xx-npe.o` for `CONFIG_IXP4XX_NPE`.

## Control Flow
Kernel build links objects as built-in or modules according to tristate symbols.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes directory Kconfig symbols used by dependent IXP4xx networking/HSS drivers.

## Risks
Low build-rule risk; symbol/object mismatch would break shared services.

## Test Signals
Build matrix for each symbol as `m/y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/ixp4xx-npe.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/ixp4xx-npe.c

## Purpose
Intel IXP4xx Network Processor Engine driver. It discovers/reset-registers up to three NPE coprocessors, exports request/release/running/messaging/firmware-load APIs, and spawns optional DT child devices.

## Important APIs, Types, and Functions
- Global `npe_tab[3]` stores NPE ids, register mappings, syscon regmap, and validity.
- Exported APIs: `npe_names`, `npe_running()`, `npe_request()`, `npe_release()`, `npe_load_firmware()`, `npe_send_message()`, `npe_recv_message()`, and `npe_send_recv_message()`.
- Core internals: command read/write helpers, `npe_debug_instr()`, logical register writers, `npe_reset()`, `npe_start()`, and `npe_stop()`.

## Control Flow
Probe gets the global syscon, iterates three memory resources, checks CPU feature/reset bits for availability, maps each NPE register range, performs a deep reset sequence, marks successful NPEs valid, and populates child devices if using DT. Remove resets mapped NPEs.

Firmware loading requests firmware by name, validates image size/magic/ID/endian, rejects mismatched NPE/device IDs, rejects running NPEs, locates the EOF block, validates instruction/data block ranges against CPU-specific memory sizes, writes each word via execution commands, starts the NPE, and releases firmware. Messaging APIs poll FIFO status to send/receive two-word messages.

## State and Persistence
Driver state is global/static and persists while the module is loaded. Firmware loaded into NPE instruction/data memory and NPE run state persist until reset/reload. Module references are held by `npe_request()` and dropped by `npe_release()`.

## Dependencies and Integration Points
Depends on IXP4xx CPU feature helpers, syscon regmap, platform resources for NPE registers, firmware loader, and consumers from network/crypto/HSS drivers.

## Risks
- Firmware parsing mutates the firmware buffer when byte-swapped; firmware memory is treated as writable.
- Reset/debug instruction path has busy loops/timeouts and deep hardware assumptions.
- `npe_request()` returns global objects with module refs but no per-NPE exclusive ownership; consumers must coordinate.
- Messaging expects exactly two-word protocol messages and can timeout on firmware stalls.

## Test Signals
Probe with absent/present NPE feature bits, reset timeout, firmware bad magic/size/id/EOF/range, swapped firmware, running-NPE `-EBUSY`, message FIFO timeout, request/release module ref behavior, and child population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/ixp4xx-npe.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/ixp4xx-qmgr.c -->
# sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/ixp4xx-qmgr.c

## Purpose
Intel IXP4xx Queue Manager driver. It initializes hardware queue SRAM/IRQ registers and exports low-level queue entry, status, IRQ, allocation, and release APIs for dependent IXP4xx drivers.

## Important APIs, Types, and Functions
- Global state includes `qmgr_regs`, two IRQ numbers, `qmgr_lock`, `used_sram_bitmap`, and per-queue IRQ handler/context arrays.
- Exported APIs: `qmgr_put_entry()`, `qmgr_get_entry()`, status helpers, `qmgr_set_irq()`, `qmgr_enable_irq()`, `qmgr_disable_irq()`, `__qmgr_request_queue()` or debug `qmgr_request_queue()`, and `qmgr_release_queue()`.
- IRQ handlers include A0-specific split handlers and generic `qmgr_irq()`.

## Control Flow
Probe maps queue manager registers, gets two IRQs, resets status/IRQ/source/SRAM registers, chooses A0 or generic IRQ handlers based on CPU revision, requests IRQs, reserves initial SRAM pages, initializes the spinlock, and logs readiness.

Queue request validates queue number, queue size, and watermarks, takes a module reference, scans the 128-page SRAM bitmap for contiguous free pages, writes queue SRAM config, records debug description if enabled, and returns. Release drains remaining entries while logging, clears SRAM config and bitmap, nulls IRQ handler, and drops the module reference. IRQ dispatch ACKs status bits and invokes registered handlers.

## State and Persistence
State is global hardware register mapping, queue SRAM allocation bitmap, IRQ callbacks, and module reference counts. Queue contents reside in hardware SRAM and are drained on release. No file persistence.

## Dependencies and Integration Points
Depends on IXP4xx queue register definitions, CPU revision helpers, platform IRQ/resources, and exported consumer APIs under `linux/soc/ixp4xx/qmgr.h`.

## Risks
- Many APIs use `BUG_ON()` for invalid queue or release state, so bad consumers can crash the kernel.
- Queue allocation uses a global bitmap and no owner identity beyond module refs; double release or forgotten release leaks hardware SRAM.
- IRQ callbacks are raw function pointers invoked in IRQ context and must be registered before enabling.
- A0 workaround handlers infer source bits and can differ from newer silicon behavior.

## Test Signals
Queue request size/watermark validation, SRAM exhaustion, release of nonempty queues, IRQ source programming for low/high queues, enable/disable ACK behavior, A0 versus generic IRQ dispatch, and module reference balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/ixp4xx/ixp4xx-qmgr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/lantiq/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/lantiq/Makefile

## Purpose
Always builds the Lantiq FPI bus driver object for this directory.

## Important APIs, Types, and Functions
No runtime APIs. Rule: `obj-y += fpi-bus.o`.

## Control Flow
Build includes the FPI bus driver whenever the directory is part of the kernel build.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Integrates with `fpi-bus.c`, which has OF compatible gating.

## Risks
Unconditional object inclusion relies on runtime compatible matching to avoid action on other platforms.

## Test Signals
Build inclusion and nonmatching platform no-op behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/lantiq/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/lantiq/fpi-bus.c -->
# sources/distributed-fs/ceph-client/drivers/soc/lantiq/fpi-bus.c

## Purpose
Lantiq XRX200 FPI bus driver. It configures RCU AHB endianness, disables FPI burst on the xbar, and populates child devices under the FPI bus node.

## Important APIs, Types, and Functions
- `ltq_fpi_probe()` performs all runtime work.
- OF match is `lantiq,xrx200-fpi`.
- Register constants cover xbar burst control and RCU big-endian AHB bit.

## Control Flow
Probe maps xbar resource 0, obtains RCU regmap from `lantiq,rcu` phandle, reads `lantiq,offset-endianness`, sets `RCU_VR9_BE_AHB1S`, disables FPI burst with `ltq_w32_mask()`, and calls `of_platform_populate()` for child nodes.

## State and Persistence
No private state. RCU/xbar register changes persist until reset or reconfiguration. Child platform devices persist while parent remains.

## Dependencies and Integration Points
Depends on Lantiq SoC accessors, syscon/regmap, OF properties, platform resources, and child devices on the FPI bus.

## Risks
Comment says RCU configuration is optional, but `syscon_regmap_lookup_by_phandle()` errors are returned, making it required in practice. Endianness and burst settings are platform-global and can affect all bus children.

## Test Signals
Probe with valid DT, missing RCU phandle, missing offset property, regmap update failure, xbar register write verification, and child population.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/lantiq/fpi-bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/litex/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/litex/Kconfig

## Purpose
Defines LiteX SoC Builder driver options.

## Important APIs, Types, and Functions
No runtime APIs. `LITEX` is a bool selected by `LITEX_SOC_CONTROLLER`; `LITEX_SOC_CONTROLLER` is tristate, depends on OF and HAS_IOMEM, and enables CSR access verification and common LiteX accessors.

## Control Flow
The controller symbol gates `litex_soc_ctrl.o`.

## State and Persistence
Kernel configuration only.

## Dependencies and Integration Points
Drivers using `linux/litex.h` accessors should depend on `LITEX`.

## Risks
The SPDX tag uses `SPDX-License_Identifier` rather than the standard `SPDX-License-Identifier`, which may not be recognized by tooling.

## Test Signals
Kconfig visibility, selection of `LITEX`, and license tooling checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/litex/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/litex/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/litex/Makefile

## Purpose
Builds the LiteX SoC controller driver when selected.

## Important APIs, Types, and Functions
No runtime APIs. Rule: `obj-$(CONFIG_LITEX_SOC_CONTROLLER) += litex_soc_ctrl.o`.

## Control Flow
Kernel build includes the controller object according to the tristate symbol.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes `CONFIG_LITEX_SOC_CONTROLLER`.

## Risks
The SPDX tag uses `SPDX-License_Identifier`, matching the Kconfig typo.

## Test Signals
Build with controller enabled as module/built-in and license tooling checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/litex/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/litex/litex_soc_ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/soc/litex/litex_soc_ctrl.c

## Purpose
LiteX SoC controller platform driver. It verifies LiteX CSR access through a scratch register and registers a restart handler that writes the LiteX reset register.

## Important APIs, Types, and Functions
- `litex_check_csr_access()` reads/writes/restores scratch register and panics on mismatch.
- `struct litex_soc_ctrl_device` stores CSR base.
- `litex_reset_handler()` writes reset value.
- `litex_soc_ctrl_probe()` maps registers, checks CSR access, and registers restart handler.

## Control Flow
Probe allocates device state, maps resource 0, validates scratch read value, writes test value, validates it, restores original scratch value, logs initialization, and registers a devm restart handler. System restart calls the handler, which writes `1` to reset offset.

## State and Persistence
Private state is devm-managed base pointer. Scratch register is temporarily modified and restored. Reset register write causes system reset.

## Dependencies and Integration Points
Depends on OF compatible `litex,soc-controller`, `linux/litex.h` accessors, platform I/O resources, and sys-off restart handler framework.

## Risks
The driver intentionally panics if CSR access appears broken, which is appropriate for incorrect soft-SoC endianness/layout but fatal at boot. Restart registration failure is warning-only.

## Test Signals
Valid scratch read/write, intentional mismatch panic, restart handler write, missing resource failure, and compatible matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/litex/litex_soc_ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/loongson/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/soc/loongson/Kconfig

## Purpose
Defines Loongson-2 GUTS and power-management controller driver options.

## Important APIs, Types, and Functions
No runtime APIs. `LOONGSON2_GUTS` is tristate, depends on LoongArch or compile testing, and selects `SOC_BUS`. `LOONGSON2_PM` is bool, depends on LoongArch+OF and built-in input support.

## Control Flow
Symbols gate `loongson2_guts.o` and `loongson2_pm.o` in the Makefile.

## State and Persistence
Kernel configuration only.

## Dependencies and Integration Points
GUTS registers SoC identity. PM integrates with suspend and input power button handling.

## Risks
`LOONGSON2_PM` is bool and requires `INPUT=y`, so module-style deployments are not supported.

## Test Signals
Kconfig visibility, `SOC_BUS` selection, PM hidden when input is modular, and build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/loongson/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/loongson/Makefile -->
# sources/distributed-fs/ceph-client/drivers/soc/loongson/Makefile

## Purpose
Builds Loongson-2 GUTS and PM drivers according to Kconfig.

## Important APIs, Types, and Functions
No runtime APIs. Rules build `loongson2_guts.o` for `CONFIG_LOONGSON2_GUTS` and `loongson2_pm.o` for `CONFIG_LOONGSON2_PM`.

## Control Flow
Build includes objects according to selected symbols.

## State and Persistence
No runtime state.

## Dependencies and Integration Points
Consumes Loongson Kconfig symbols.

## Risks
Low build-rule risk; GUTS and PM functions are independent but both target Loongson-2 platforms.

## Test Signals
Build matrix for GUTS module/built-in and PM built-in.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/loongson/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/loongson/loongson2_guts.c -->
# sources/distributed-fs/ceph-client/drivers/soc/loongson/loongson2_guts.c

## Purpose
Loongson-2 Global Utilities (GUTS) register-block driver. It maps chip ID registers, reads SVR, matches known die IDs, and registers SoC bus identity attributes.

## Important APIs, Types, and Functions
- `struct scfg_guts` models selected global utility registers.
- Static global `guts` stores register base and endianness.
- `loongson2_guts_get_svr()` reads SVR with configured endianness.
- `loongson2_guts_probe()` maps registers and registers `soc_device`.
- `loongson2_guts_init()` registers the platform driver at `core_initcall()`.

## Control Flow
Probe allocates global guts state, reads `little-endian`, maps resource 0, reads root model or compatible as machine, reads SVR, matches die table, formats family/soc_id/revision strings, registers the SoC device, and logs identity. Remove unregisters the global SoC device.

## State and Persistence
Global static `soc_dev_attr`, `soc_dev`, and `guts` persist while bound. Hardware SVR is read-only identity state. No file persistence.

## Dependencies and Integration Points
Depends on OF platform resources, root DT model/compatible, SoC bus core, and compatible `loongson,ls2k-chipid`.

## Risks
- Global singleton state assumes one device instance.
- If root node lookup fails, dereferencing/using `machine` assumptions could be fragile; normal DT has root.
- Only one die match is currently known; unknown chips register generic Loongson family.

## Test Signals
Probe with little/big endian SVR, known and unknown die values, missing root model fallback to compatible, SoC bus registration failure, and remove unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/loongson/loongson2_guts.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/loongson/loongson2_pm.c -->
# sources/distributed-fs/ceph-client/drivers/soc/loongson/loongson2_pm.c

## Purpose
Loongson-2 power-management controller driver. It handles PM wake/status registers, registers a power-button input device, services PM IRQs, configures suspend-to-RAM entry when firmware address is provided, and populates PM child devices.

## Important APIs, Types, and Functions
- Global `struct loongson2_pm` stores register base, input device, and suspended flag.
- Helpers clear status and enable PM IRQ bits.
- Suspend hooks: `loongson2_suspend_begin()`, `loongson2_suspend_enter()`, and valid-state check.
- `loongson2_power_button_init()` creates input device and wake IRQ.
- `loongson2_pm_irq_handler()` reports KEY_POWER unless suspended.
- `loongson2_pm_probe()` maps registers, configures suspend address, requests IRQ, enables status, sets suspend ops, and populates children.

## Control Flow
Probe maps resource 0, obtains IRQ 0, optionally reads `loongson,suspend-address` into `loongson_sysconf.suspend_addr`, initializes/registers a power button input device, requests shared IRQ, enables PM1 interrupt and power-button enable bits, clears status, registers suspend ops if suspend address exists, and populates child nodes. IRQ handler reads PM1 status, reports press/release when not suspended and power-button status is set, then clears PM/GPE status. Suspend entry clears status, calls architecture suspend/resume hooks, re-enables PM IRQ, and marks resume via firmware.

## State and Persistence
Global singleton state persists for the driver lifetime. Hardware PM status/enable registers persist until reset/rewrite. Input device and wake IRQ persist after probe. The firmware suspend address is stored globally in `loongson_sysconf`.

## Dependencies and Integration Points
Depends on LoongArch suspend hooks, input subsystem, wake IRQ helpers, OF platform, PM core suspend ops, and compatible `loongson,ls2k0500-pmc`.

## Risks
- `loongson2_power_button_init()` checks `if (!dev)` after `input_allocate_device()` instead of checking `button`, so allocation failure would dereference NULL.
- Global singleton state assumes one PM controller.
- If suspend address is missing, S3 is unavailable but probe continues.
- The input device parent is set to NULL, which may affect device hierarchy/power management expectations.

## Test Signals
Probe with/without suspend address, input allocation failure, IRQ request failure, power-button event reporting, suspended IRQ suppression, wake IRQ setup, suspend/resume path, child population, and PM status clear behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/soc/loongson/loongson2_pm.c -->
