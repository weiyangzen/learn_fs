# subset-b-003849 Research

Grouped research for Linux I2C bus adapter sources under `sources/distributed-fs/ceph-client/drivers/i2c/busses`. Each section preserves the source path for deterministic reconciliation into per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cpm.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cpm.c

## Purpose
Freescale CPM1/CPM2 I2C controller adapter. It exposes a CPM communication processor I2C engine as a Linux `i2c_adapter`, using CPM parameter RAM, buffer descriptors, coherent DMA buffers, and OF platform resources.

## Important APIs, Types, And Functions
Key private state is `struct cpm_i2c`, holding the adapter, mapped I2C registers, CPM parameter RAM, DPRAM buffer descriptors, coherent TX/RX buffers, IRQ, command word, frequency, and CPM version. `struct i2c_ram` and `struct i2c_reg` model CPM parameter RAM and controller registers. The adapter algorithm is `cpm_i2c_algo` with `cpm_i2c_xfer()` and `cpm_i2c_func()`. Probe/remove are `cpm_i2c_probe()` and `cpm_i2c_remove()`. Hardware setup/teardown are `cpm_i2c_setup()` and `cpm_i2c_shutdown()`.

## Control Flow
Probe allocates `struct cpm_i2c`, binds OF data, copies `cpm_ops`, initializes hardware, then registers a numbered adapter using optional `linux,i2c-index`. Setup maps parameter RAM and registers, resolves CPM1 versus CPM2, allocates DPRAM BDs and coherent buffers, initializes parameter RAM, issues `CPM_CR_INIT_TRX`, programs address, baud, mode, and IRQ masks. Transfers reset BD pointers, prepare each message in `cpm_i2c_parse_message()`, enable interrupts, start the controller, wait for each TX/RX BD completion, then validate status in `cpm_i2c_check_message()`.

## State And Persistence
State is in RAM and hardware registers only. Persistent kernel-visible state is the registered adapter. The transfer path mutates CPM BD status bits, parameter RAM pointers, and coherent buffers. Error paths call `cpm_i2c_force_close()` and may clear enable for errata builds.

## Dependencies And Integration Points
Depends on CPM/MURAM APIs, OF address/IRQ parsing, DMA coherent allocation, IRQs, and Linux I2C core. Compatible strings are `fsl,cpm1-i2c` and `fsl,cpm2-i2c`.

## Risks
BD and DMA buffer alignment are delicate, especially read buffer alignment and CPM1 relocation handling. Timeout is fixed at one second per message. The code supports only four messages and read/write lengths up to `CPM_MAX_READ`. Hardware errata behavior is compile-time disabled by default. Failure cleanup spans IRQ, I/O maps, MURAM, and coherent memory, so partial allocation paths are risk-heavy.

## Test Signals
Useful checks include OF probe on CPM1/CPM2, successful adapter registration, basic read/write/repeated-start transactions, NACK mapping to `-ENXIO`, timeout recovery via force-close, max message/length quirk enforcement, and removal without leaked IRQ/DMA/MURAM resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cros-ec-tunnel.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cros-ec-tunnel.c

## Purpose
ChromeOS EC I2C tunnel adapter. It presents a local Linux `i2c_adapter` whose transfers are serialized into `EC_CMD_I2C_PASSTHRU` commands and executed by a parent ChromeOS embedded controller on a remote I2C bus.

## Important APIs, Types, And Functions
`struct ec_i2c_device` stores the device, adapter, parent `cros_ec_device`, remote bus number, and fixed request/response scratch buffers. Message sizing and marshaling are handled by `ec_i2c_count_message()`, `ec_i2c_construct_message()`, `ec_i2c_count_response()`, and `ec_i2c_parse_response()`. The adapter algorithm uses `ec_i2c_xfer()` and `ec_i2c_functionality()`. Probe/remove are `ec_i2c_probe()` and `ec_i2c_remove()`.

## Control Flow
Probe fetches the parent EC from the parent device, validates `cmd_xfer`, reads `google,remote-bus`, initializes adapter fields and ACPI companion data, then calls `i2c_add_adapter()`. A transfer computes request and response lengths, allocates a `struct cros_ec_command` plus payload, packs Linux `i2c_msg` entries into EC passthrough structures, sends via `cros_ec_cmd_xfer_status()`, parses EC status flags, and copies read data back into the original messages.

## State And Persistence
No hardware state is owned locally beyond adapter registration. Per-transfer state lives in the allocated EC command buffer. The configured `remote_bus` is read once at probe and retained in `struct ec_i2c_device`.

## Dependencies And Integration Points
Depends on ChromeOS EC protocol headers, `cros_ec_cmd_xfer_status()`, platform device binding, ACPI/OF matching, and the Linux I2C core. Match points are OF `google,cros-ec-i2c-tunnel`, ACPI `GOOG0012`, and platform alias `cros-ec-i2c-tunnel`.

## Risks
Ten-bit addresses are rejected. Request/response lengths are dynamically allocated but constructed from fixed EC protocol structure sizes; malformed EC responses can produce `-EPROTO`. Status mapping collapses EC timeout, NAK, and generic errors into standard Linux errors. Remote bus behavior and locking are delegated to EC firmware.

## Test Signals
Test probe deferral when parent EC is absent, missing `google,remote-bus`, normal write/read passthrough, readback copying for combined transactions, EC NAK to `-ENXIO`, EC timeout to `-ETIMEDOUT`, ten-bit rejection, and ACPI/OF adapter discovery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-cros-ec-tunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-davinci.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-davinci.c

## Purpose
TI DaVinci/Keystone I2C master adapter. It programs SoC I2C registers, exposes standard and SMBus-emulated transfers, handles runtime PM, CPU frequency changes, and optional GPIO-style SCL bus recovery through the controller pin function registers.

## Important APIs, Types, And Functions
`struct davinci_i2c_dev` holds MMIO base, completion, clock, active buffer, IRQ, adapter, bus frequency, CPU frequency notifier, and `has_pfunc`. Core functions include `i2c_davinci_calc_clk_dividers()`, `i2c_davinci_init()`, `i2c_davinci_xfer_msg()`, `i2c_davinci_xfer()`, and `i2c_davinci_isr()`. Recovery is via `davinci_i2c_scl_recovery_info`. Probe/remove are `davinci_i2c_probe()` and `davinci_i2c_remove()`.

## Control Flow
Probe gets IRQ, clock, MMIO, bus frequency, enables runtime PM, initializes hardware, requests IRQ, registers CPU frequency notifier, configures the adapter, optionally attaches recovery info, and registers a numbered adapter. Transfers resume runtime PM, wait for bus idle, perform each message, and autosuspend. Each message programs SAR, buffer state, count, mode bits, first transmit byte when needed, starts transfer, and waits on a completion signaled by the ISR. The ISR loops through IVR events for arbitration lost, NACK, register ready, RX ready, TX ready, and stop.

## State And Persistence
Runtime state includes `buf`, `buf_len`, `cmd_err`, `stop`, and `terminate`, all consumed by the IRQ handler. Hardware state is reinitialized after arbitration loss, recovery, CPU frequency transitions, suspend/resume, and probe. There is no disk persistence.

## Dependencies And Integration Points
Integrates with platform/OF IDs `ti,davinci-i2c` and `ti,keystone-i2c`, clocks, runtime PM, interrupt handling, cpufreq notifiers, device properties, and I2C generic SCL recovery.

## Risks
The reserved own address `0x08` cannot be targeted. Transfer completion relies on IRQ ordering and completion state; abnormal leftover `buf_len` triggers termination. CPU frequency updates lock the root adapter and reprogram dividers. Recovery requires `ti,has-pfunc`. Runtime PM errors must avoid leaving clocks or autosuspend state inconsistent.

## Test Signals
Exercise standard and fast-mode divider calculation, read/write/zero-length transfers, NACK with and without `I2C_M_IGNORE_NAK`, arbitration loss reset, bus-busy recovery, CPU frequency transition handling, runtime suspend/resume, and probe cleanup on IRQ/notifier/adapter registration failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-davinci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-amdisp.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-amdisp.c

## Purpose
AMD ISP DesignWare I2C platform glue. It instantiates a Synopsys DesignWare controller in AMD ISP hardware where transfers run in polling mode because no IRQ is connected.

## Important APIs, Types, And Functions
The driver uses shared `struct dw_i2c_dev` from `i2c-designware-core.h`. Local helpers are `amd_isp_dw_i2c_get_clk_rate()` and PM callbacks. Probe is `amd_isp_dw_i2c_plat_probe()`, removal is `amd_isp_dw_i2c_plat_remove()`, and shared setup is delegated to `i2c_dw_fw_parse_and_configure()`, `i2c_dw_configure()`, `i2c_dw_probe()`, `i2c_dw_disable()`, `i2c_dw_prepare_clk()`, and `i2c_dw_init()`.

## Control Flow
Probe allocates `dw_i2c_dev`, sets `ACCESS_POLLING`, maps MMIO, installs a fixed 100 MHz clock-rate callback in kHz units, parses firmware timings, configures DesignWare master/slave capability, initializes adapter metadata using `AMDISP_I2C_ADAP_NAME`, sets PM driver flags, resumes the generic PM domain, probes the shared DesignWare core, then suspends the PM domain and enables runtime PM. Transfers are handled entirely by shared DesignWare code in polling mode.

## State And Persistence
State lives in `dw_i2c_dev`, runtime PM state, and controller registers. Probe starts with the PM domain resumed for initialization, then marks the device suspended and runtime-PM managed. No persistent storage is used.

## Dependencies And Integration Points
Depends on AMD ISP misc definitions, generic PM domains, runtime PM, platform MMIO resources, ACPI/OF device nodes, and DesignWare core/master modules under namespaces `I2C_DW` and `I2C_DW_COMMON`.

## Risks
Clock rate is hard-coded; wrong hardware assumptions would break timing. Polling mode increases CPU work and shifts timeout behavior into shared code. PM-domain ordering is important: failures after `i2c_dw_probe()` must disable runtime PM cleanly. Suspend callbacks mark adapters suspended and reinitialize hardware on resume.

## Test Signals
Validate no-IRQ probe path, firmware timing parsing, adapter naming, runtime suspend disables the controller, runtime resume reinitializes it, system suspend marks the adapter suspended, and polling transfers complete without IRQ registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-amdisp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-amdpsp.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-amdpsp.c

## Purpose
AMD PSP arbitration support for DesignWare I2C buses shared with the Platform Security Processor. It installs lock operations and internal acquire/release hooks so x86 asks PSP for temporary bus ownership before I2C activity.

## Important APIs, Types, And Functions
`enum psp_i2c_req_type` and `struct psp_i2c_req` model PSP acquire/release commands. Global state includes `psp_i2c_access_mutex`, `psp_i2c_sem_acquired`, `psp_i2c_access_count`, `psp_i2c_mbox_fail`, `psp_i2c_dev`, and `_psp_send_i2c_req`. Key functions are `psp_send_i2c_req()`, `psp_acquire_i2c_bus()`, `psp_release_i2c_bus()`, and `i2c_dw_amdpsp_probe_lock_support()`.

## Control Flow
Probe support checks CCP reachability, DesignWare `ARBITRATION_SEMAPHORE`, singleton binding, root PCI device ID to choose Cezanne platform mailbox versus doorbell, PSP platform access readiness, then installs adapter `lock_ops` and DesignWare internal lock callbacks. Acquire increments access count, skips PSP if mailbox failed or reservation remains valid, otherwise polls PSP acquire. Release decrements access count and either leaves reservation for delayed work or sends release when the reservation window elapsed.

## State And Persistence
Arbitration state is process-global, not per-controller, enforcing one bound bus. Reservation time is tracked in jiffies and released by delayed work after `PSP_I2C_RESERVATION_TIME_MS` when no users remain. Mailbox failure permanently degrades to host-exclusive behavior for the module lifetime.

## Dependencies And Integration Points
Depends on AMD PSP/CCP platform access APIs, PCI root-device detection, workqueues, mutexes, DesignWare platform probing, and I2C adapter lock operations.

## Risks
The singleton global design rejects additional PSP-managed buses. `trylock_bus()` appears to return immediately when `rt_mutex_trylock()` succeeds, so its PSP acquire path warrants scrutiny against lock API expectations. PSP communication failure intentionally falls back to success, which preserves host function but risks real PSP contention. Doorbell/mailbox status interpretation is hardware-specific.

## Test Signals
Test `-EPROBE_DEFER` when PSP is unavailable, Cezanne versus doorbell selection, nested lock/unlock count behavior, delayed release after idle, mailbox failure fallback, duplicate instance rejection, and transfers that span write-wait-read sequences under adapter lock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-amdpsp.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-baytrail.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-baytrail.c

## Purpose
Intel Bay Trail DesignWare I2C semaphore support. It detects ACPI-declared sharing with PUNIT firmware and installs IOSF mailbox callbacks to block/unblock PUNIT I2C access around host transfers.

## Important APIs, Types, And Functions
The single exported function is `i2c_dw_baytrail_probe_lock_support(struct dw_i2c_dev *dev)`. It uses `ACPI_HANDLE()`, ACPI method `_SEM`, `iosf_mbi_available()`, `iosf_mbi_block_punit_i2c_access`, and `iosf_mbi_unblock_punit_i2c_access`.

## Control Flow
DesignWare platform probing calls this helper through the semaphore callback table. The helper validates `dev`, requires an ACPI handle, evaluates `_SEM`, ignores controllers where `_SEM` is absent or false, defers if IOSF MBI is unavailable, then marks the controller shared with PUNIT and installs acquire/release lock hooks.

## State And Persistence
Only `dw_i2c_dev` fields are changed: `acquire_lock`, `release_lock`, and `shared_with_punit`. The shared flag changes common runtime PM behavior by skipping clock disable/enable in common PM paths.

## Dependencies And Integration Points
Depends on ACPI firmware, x86 IOSF MBI, the DesignWare platform driver semaphore callback table, and common DesignWare lock hooks.

## Risks
ACPI `_SEM` must correctly describe ownership sharing. If IOSF MBI appears late, probe defers. Incorrect `shared_with_punit` PM handling could leave hardware in an unexpected power state. The helper is intentionally no-op on nonmatching platforms by returning `-ENODEV`.

## Test Signals
Validate `_SEM` absent/false paths, IOSF deferral, successful lock callback installation, runtime PM skip behavior for shared buses, and actual transfer serialization against PUNIT-controlled PMIC access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-baytrail.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-common.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-common.c

## Purpose
Shared Synopsys DesignWare I2C core. It abstracts register access, parses firmware timing, initializes hardware, controls clocks/locks, handles common errors and PM, dispatches master/slave IRQs, and registers the Linux adapter for platform-specific front ends.

## Important APIs, Types, And Functions
This file implements exported APIs declared in `i2c-designware-core.h`: `i2c_dw_init()`, `i2c_dw_fw_parse_and_configure()`, `i2c_dw_scl_hcnt()`, `i2c_dw_scl_lcnt()`, `i2c_dw_prepare_clk()`, `i2c_dw_acquire_lock()`, `i2c_dw_release_lock()`, `i2c_dw_wait_bus_not_busy()`, `i2c_dw_handle_tx_abort()`, `i2c_dw_func()`, `i2c_dw_disable()`, `i2c_dw_probe()`, and `i2c_dw_dev_pm_ops`. Internal pieces include regmap detection, ACPI/OF configuration, FIFO-depth detection, and SDA hold setup.

## Control Flow
`i2c_dw_probe()` binds adapter fwnode, initializes regmap by detecting native/swapped/word register layout, sets SDA hold, detects FIFOs, runs master probe, initializes hardware, fills adapter algorithm and quirks, requests IRQ unless polling, masks interrupts, and registers a numbered adapter under a temporary runtime-PM usage hold. `i2c_dw_init()` acquires optional hardware lock, disables the controller, masks SMBus interrupts, writes timing registers, applies SDA hold, selects master/slave mode, and releases the lock. PM callbacks disable/reinitialize hardware and mark adapter suspend state.

## State And Persistence
All state lives in `struct dw_i2c_dev`, regmap-backed registers, runtime PM, and adapter registration. `sw_mask` mirrors interrupt masks for polling mode. `status` tracks active mode. No persistent storage is involved.

## Dependencies And Integration Points
Integrates with Linux regmap, ACPI timing methods (`SSCN`, `FMCN`, `FPCN`, `HSCN`), OF properties, DMI quirks, runtime PM, clocks, I2C bus recovery, DesignWare master/slave modules, and platform/PCI/AMD glue.

## Risks
Register layout autodetection is critical; wrong `COMP_TYPE` handling rejects hardware. Timing validation only allows 100 kHz, 400 kHz, 1 MHz, and 3.4 MHz. PM behavior differs for PUNIT-shared controllers. Disable must handle master-on-hold aborts without leaving SCL low. FIFO depth quirks and SDA hold workarounds are hardware-sensitive.

## Test Signals
Test native/swapped/word register maps, ACPI and OF timing sources, unsupported speed rejection, FIFO-depth detection and Wangxun override, interrupt versus polling registration, abort-source error mapping, bus-not-busy recovery, runtime/system PM, and master/slave IRQ dispatch.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-core.h -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-core.h

## Purpose
Shared definitions for the DesignWare I2C driver family. It provides register offsets, bit definitions, abort codes, model/access flags, the `dw_i2c_dev` state object, exported function prototypes, and small inline helpers used by common, master, slave, PCI, platform, and arbitration glue.

## Important APIs, Types, And Functions
`struct dw_i2c_dev` is the central type, carrying device/regmap/MMIO pointers, clocks, reset, master/slave state, transfer pointers and counters, errors, IRQ, flags, adapter, timing values, FIFO depths, lock callbacks, recovery info, and model quirks. Important macros include `DW_IC_*` register offsets, interrupt masks, abort bits, `STATUS_*`, `ACCESS_*`, `MODEL_*`, `DW_IC_MASTER`, and `DW_IC_SLAVE`. Inline helpers include `__i2c_dw_enable()`, `__i2c_dw_disable_nowait()`, interrupt mask read/write wrappers, and `i2c_dw_configure()`.

## Control Flow
The header defines the contract among the family: front-end drivers allocate/fill `dw_i2c_dev`, call `i2c_dw_fw_parse_and_configure()`, `i2c_dw_configure()`, and `i2c_dw_probe()`, while common code calls master/slave hooks for mode-specific behavior. Compile-time conditionals provide slave and BayTrail/AMD PSP hooks only when enabled.

## State And Persistence
The header itself has no runtime state, but it defines all persistent in-memory state used by DesignWare adapters across probe, transfer, PM, and removal. `sw_mask` and `status` are software mirrors for hardware state.

## Dependencies And Integration Points
Includes Linux I2C, completion, regmap, PM, IRQ, and type headers. It is the integration point between generic DesignWare common code and platform-specific modules, including AMD UCSI, Wangxun, BayTrail, AMD PSP, and optional slave support.

## Risks
Any change to `dw_i2c_dev` or bit definitions can affect all front ends. `ACCESS_POLLING` changes interrupt mask semantics. Conditional prototypes must match Kconfig combinations. Hardware constants encode assumptions from the DesignWare databook and platform quirks.

## Test Signals
Compile coverage across platform, PCI, polling, slave-enabled, BayTrail, AMD PSP, AMD Navi GPU, and Wangxun configurations is the primary signal. Runtime tests should confirm interrupt mask behavior is identical in polling and IRQ modes where intended.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-core.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-master.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-master.c

## Purpose
DesignWare I2C master-mode implementation. It calculates master timings, drives FIFO-based transfers, handles master interrupts or polling, supports protocol mangling and SMBus block reads, performs recovery, and exposes master configuration/probe helpers.

## Important APIs, Types, And Functions
Exports `i2c_dw_xfer()`, `i2c_dw_configure_master()`, `i2c_dw_isr_master()`, and `i2c_dw_probe_master()`. Core internals are `i2c_dw_set_timings_master()`, `i2c_dw_xfer_init()`, `i2c_dw_xfer_msg()`, `i2c_dw_read()`, `i2c_dw_read_clear_intrbits()`, `i2c_dw_process_transfer()`, `__i2c_dw_xfer_one_part()`, `i2c_dw_xfer_common()`, and `i2c_dw_init_recovery_info()`. AMD Navi GPU has `amd_i2c_dw_xfer_quirk()`.

## Control Flow
Probe initializes completion, computes SCL high/low counts for standard/fast/fast-plus/high-speed modes, preserves BIOS bus-clear support, and attaches optional GPIO recovery. A normal transfer resumes PM, acquires any hardware lock, splits messages at `I2C_M_STOP`, validates same-address and restart limitations, initializes registers and target address, fills TX FIFO with write data or read commands, then waits for completion. IRQ or polling clears precise interrupt bits, drains RX FIFO, refills TX FIFO, handles aborts and spurious stops, and completes on STOP/abort with no outstanding reads.

## State And Persistence
Transfer state is stored in `dw_i2c_dev`: message indexes, TX/RX buffers, outstanding read commands, `cmd_err`, `msg_err`, `abort_source`, and `status`. Hardware is disabled after each transfer and may return to slave mode if a slave is registered.

## Dependencies And Integration Points
Relies on common DesignWare register/PM/lock helpers, regmap, GPIO descriptors, pinctrl, reset control, runtime PM, and Linux I2C recovery. It feeds the common adapter algorithm via `i2c_dw_xfer()`.

## Risks
FIFO and interrupt latency can terminate transfers early when TX FIFO empties. Restart support differs when `emptyfifo_hold_master` is false. SMBus block-read length correction is subtle. AMD Navi polling quirk has separate behavior and lacks protocol mangling. Abort-source mapping must preserve `TX_ABRT_SOURCE` before clearing.

## Test Signals
Test write, read, combined read/write, SMBus block read, `I2C_M_STOP` splitting, invalid address changes, no-restart hardware, TX abort/noack/arbitration loss, polling mode, GPIO recovery, AMD Navi quirk, and suspend/resume around active adapters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-master.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-pcidrv.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-pcidrv.c

## Purpose
PCI front end for DesignWare I2C controllers on Intel Medfield/Merrifield/BayTrail/Haswell/CherryTrail/Elkhart Lake and AMD Navi GPUs. It maps PCI resources, applies platform timing quirks, and delegates controller operation to the shared DesignWare core.

## Important APIs, Types, And Functions
`struct dw_scl_sda_cfg` holds legacy timing constants. `struct dw_pci_controller` describes bus numbering, flags, setup callback, and clock-rate callback. Setup helpers include `mfld_setup()`, `mrfld_setup()`, `navi_amd_setup()`, and clock callbacks. Probe/remove are `i2c_dw_pci_probe()` and `i2c_dw_pci_remove()`.

## Control Flow
PCI probe enables the device, maps BAR0, allocates `dw_i2c_dev`, allocates IRQ vectors, fills clock/base/device/IRQ/flag fields, runs optional controller setup, parses firmware timing, configures DesignWare mode, applies legacy timing constants, initializes adapter metadata, and calls `i2c_dw_probe()`. For AMD Navi GPUs it also creates a CCGX UCSI I2C client. Runtime PM autosuspend is enabled after registration. Remove disables the controller, forbids runtime PM, gets the device, and unregisters the adapter.

## State And Persistence
Controller selection and timing constants are static tables. Per-device state is `dw_i2c_dev` in PCI driver data plus optional UCSI client stored in `dev->slave`. Runtime PM state persists while bound.

## Dependencies And Integration Points
Depends on PCI core, IRQ vectors, power-supply software node for dGPU scope, `i2c-ccgx-ucsi.h`, runtime PM, and shared DesignWare namespaces. PCI IDs are the primary binding mechanism.

## Risks
Some legacy controllers use hard-coded bus numbers and HCNT/LCNT values. AMD Navi runs polling mode and uses a special transfer quirk. UCSI client creation failure must unregister the adapter. PCI IRQ allocation and BAR mapping failures need clean devm/pcim rollback.

## Test Signals
Test all PCI ID groups for bus numbering, IRQ vector setup, adapter registration, timing constants, AMD Navi UCSI creation and polling transfers, runtime autosuspend, and remove after active PM.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-pcidrv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-platdrv.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-platdrv.c

## Purpose
Platform/ACPI/OF front end for DesignWare I2C controllers. It gathers platform resources, firmware timing, semaphore support, clocks, reset, and PM policy, then delegates to the shared DesignWare core.

## Important APIs, Types, And Functions
Core routines are `dw_i2c_plat_probe()`, `dw_i2c_plat_remove()`, `dw_i2c_plat_request_regs()`, `dw_i2c_get_parent_regmap()`, `i2c_dw_probe_lock_support()`, and `dw_i2c_plat_pm_cleanup()`. Match tables include OF `mobileye,eyeq6lplus-i2c`, `mscc,ocelot-i2c`, `snps,designware-i2c`, many ACPI IDs, and platform ID `i2c_designware`.

## Control Flow
Probe derives flags from match data or `wx,i2c-snps-model`, treats missing IRQ as polling mode, allocates `dw_i2c_dev`, maps MMIO or gets parent regmap for Intel Xe/Wangxun, acquires optional reset, parses firmware configuration, probes BayTrail/AMD PSP semaphores, configures DesignWare mode, enables optional `pclk` and main clock, computes SDA hold from timing properties, initializes adapter class/number, sets PM flags and autosuspend, then calls `i2c_dw_probe()`.

## State And Persistence
All state is in `dw_i2c_dev` and runtime PM. `shared_with_punit` holds an extra runtime PM usage count and alters cleanup. DMI may select `I2C_CLASS_HWMON` for known hardware.

## Dependencies And Integration Points
Uses platform resources, MFD syscon/parent regmaps, clocks, resets, DMI, ACPI, OF, runtime PM, semaphore helper modules, and DesignWare common/master/slave code.

## Risks
Resource path differs by model: MMIO, parent regmap, polling, and semaphore variants must all initialize the common core correctly. Missing IRQ intentionally means polling only for `-ENXIO`, but other IRQ errors abort. Runtime PM must be disabled before cleanup and clocks must be balanced on probe failure.

## Test Signals
Test ACPI/OF/platform matching, IRQ and no-IRQ paths, parent regmap models, semaphore callbacks, clock prepare failure cleanup, DMI adapter class, autosuspend behavior, and remove with PUNIT-shared devices.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-platdrv.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-slave.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-slave.c

## Purpose
Optional DesignWare I2C slave-mode implementation. It registers/unregisters an I2C slave client, configures the controller for slave operation, and translates slave interrupts into Linux `i2c_slave_event()` callbacks.

## Important APIs, Types, And Functions
Exports `i2c_dw_reg_slave()`, `i2c_dw_unreg_slave()`, `i2c_dw_isr_slave()`, and `i2c_dw_configure_slave()`. Internal helper `i2c_dw_read_clear_intrbits_slave()` acknowledges slave-relevant interrupts using individual clear registers.

## Control Flow
Register checks adapter slave functionality, rejects an existing slave and ten-bit clients, acquires the hardware lock, runtime-resumes the device, disables the controller, stores `dev->slave`, and switches to slave mode. ISR validates enabled/raw status and slave presence, handles RX_FULL as master-write-to-slave, RD_REQ as master-read-from-slave, writes outbound data, and sends STOP events. Unregister masks interrupts, disables the controller, synchronizes IRQ, clears `dev->slave`, switches to master mode, and runtime-suspends.

## State And Persistence
Slave state is `dev->slave`, `dev->status`, and controller registers including SAR and interrupt mask. No persistent storage exists; slave registration persists only while the client is bound.

## Dependencies And Integration Points
Depends on shared DesignWare common code, regmap, runtime PM, IRQ synchronization, Linux I2C slave callbacks, and Kconfig `CONFIG_I2C_SLAVE`.

## Risks
Polling-mode controllers do not advertise slave support. Slave and master mode switching shares the same `status` flags, so mode transitions must happen with hardware disabled. Event ordering for write-request/write-received/read-request/read-processed depends on FIFO and RD_REQ behavior. Unregister must avoid use-after-free via `synchronize_irq()`.

## Test Signals
Test slave registration rejection cases, master write to slave, master read from slave, repeated reads, STOP delivery, unregister during idle and after IRQ activity, runtime PM balancing, and configurations without `CONFIG_I2C_SLAVE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-designware-slave.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-digicolor.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-digicolor.c

## Purpose
Conexant Digicolor SoC I2C adapter. It implements an interrupt-driven state machine around byte-wide controller command/data registers and exposes I2C plus SMBus emulation and `I2C_FUNC_NOSTART`.

## Important APIs, Types, And Functions
`struct dc_i2c` stores adapter, device, MMIO registers, clock, frequency, active message pointer, buffer position, last-message flag, spinlock, completion, state, and error. Core functions are `dc_i2c_irq()`, `dc_i2c_xfer_msg()`, `dc_i2c_xfer()`, `dc_i2c_start_msg()`, `dc_i2c_init_hw()`, and small command/data helpers.

## Control Flow
Probe reads optional `clock-frequency`, gets clock, maps MMIO, requests IRQ, initializes adapter fields, initializes hardware clock timing, enables the clock, and registers the adapter. Each message is started under lock with interrupts enabled. The IRQ clears the flag, checks command completion status for ACK/abort failures, advances through START, ADDR, WRITE, READ, and STOP states, filling or draining one byte at a time, and completes when the message or stop is done.

## State And Persistence
The transfer state machine is stored in `dc_i2c` fields and protected by a spinlock. The clock divider is programmed at probe. No persistent storage is used.

## Dependencies And Integration Points
Depends on OF compatible `cnxt,cx92755-i2c`, platform MMIO/IRQ resources, clocks, completions, spinlocks, and Linux I2C core.

## Risks
Timeout is fixed at 100 ms per message. Command status maps bad ACK and abort to `-EIO` rather than distinct NACK errors. Clock timing must fit an 8-bit register. IRQ-driven state must correctly handle `I2C_M_NOSTART` and repeated-start cases.

## Test Signals
Test adapter probe, clock-frequency limits, write/read/repeated-start/no-start transfers, ACK-bad and abort status handling, timeout reset to idle, IRQ disable after transfer, and remove clock cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-digicolor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-diolan-u2c.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-diolan-u2c.c

## Purpose
USB I2C adapter driver for Diolan U2C-12. It converts Linux I2C messages into the device firmware command protocol over USB bulk endpoints.

## Important APIs, Types, And Functions
`struct i2c_diolan_u2c` stores output/input command buffers, endpoint addresses, USB device/interface, adapter, and queued command counts. USB command helpers include `diolan_usb_transfer()`, `diolan_usb_cmd*()`, `diolan_i2c_start()`, `diolan_i2c_stop()`, byte ACK helpers, and speed/clock-sync configuration. I2C operations are `diolan_usb_xfer()` and `diolan_usb_func()`. USB binding uses `diolan_u2c_probe()` and `diolan_u2c_disconnect()`.

## Control Flow
Probe validates interface zero with at least two endpoints, allocates state, stores endpoints, initializes adapter data, runs `diolan_init()` to flush stale input, log firmware/serial, set speed, and configure clock stretching, then registers the adapter. Transfer queues a START, repeated starts for subsequent messages, sends address with ACK check, then writes bytes or reads bytes with ACK/NACK handling. It always attempts STOP on abort.

## State And Persistence
State is per USB interface. `frequency` is a module parameter and may be normalized during initialization. Command output buffering batches firmware commands until flush thresholds or explicit flush. No durable persistence exists.

## Dependencies And Integration Points
Depends on USB bulk messaging, Diolan firmware command IDs/responses, Linux I2C core, module parameter handling, and HWMON adapter class.

## Risks
Endpoint ordering is assumed from descriptors. Response handling maps address-phase NACK differently from later NACKs based on command index. SMBus block reads mutate `pmsg->len` after receiving a length byte. USB timeouts and stale device input can desynchronize command/response streams.

## Test Signals
Test USB probe/disconnect, firmware init, frequency parameter normalization, simple writes/reads, repeated-start combined messages, SMBus block reads, address NACK to `-ENXIO`, later NACK to `-EIO`, USB timeout, STOP-on-error, and input flush behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-diolan-u2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-dln2.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-dln2.c

## Purpose
I2C interface driver for the Diolan DLN-2 MFD USB device. It exposes each DLN2 I2C port as a Linux adapter and delegates actual transport to the parent DLN2 command layer.

## Important APIs, Types, And Functions
`struct dln2_i2c` stores platform device, adapter, port number, and a shared transfer buffer. Commands are built with `DLN2_I2C_CMD()`. Core helpers are `dln2_i2c_enable()`, `dln2_i2c_write()`, `dln2_i2c_read()`, `dln2_i2c_xfer()`, and `dln2_i2c_func()`. Probe/remove are `dln2_i2c_probe()` and `dln2_i2c_remove()`.

## Control Flow
Probe allocates state and a transfer buffer, reads the port from platform data, initializes adapter fields and ACPI/OF linkage, enables the DLN2 I2C port via parent command, and registers the adapter. Transfers iterate messages independently; read messages issue `DLN2_I2C_READ` and validate returned lengths, while writes issue `DLN2_I2C_WRITE` and require the full length to be accepted.

## State And Persistence
Per-adapter state is small and device-managed. The shared buffer is safe because I2C core serializes adapter transfers. The hardware port is enabled on probe and disabled on remove.

## Dependencies And Integration Points
Depends on the DLN2 MFD API (`dln2_transfer()` and `dln2_transfer_tx()`), platform data, ACPI companion propagation, and Linux I2C quirks for maximum transfer size.

## Risks
The driver does not combine messages into one firmware transaction, so repeated-start semantics depend on DLN2 command capabilities and may be limited. Buffer size is capped at 256 bytes. Strict protocol length checks can surface firmware inconsistencies as `-EPROTO`.

## Test Signals
Test enable/disable commands, read/write at boundary sizes, protocol length mismatch, adapter quirk enforcement, multiple port naming, ACPI companion linkage, and cleanup when `i2c_add_adapter()` fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-dln2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-eg20t.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-eg20t.c

## Purpose
PCI I2C adapter for Intel EG20T PCH and LAPIS/ROHM ML7213, ML7223, and ML7831 IOH controllers. It supports one or two channels, normal-mode interrupt-driven transfers, 7-bit and 10-bit addresses, and suspend/resume.

## Important APIs, Types, And Functions
`struct i2c_algo_pch_data` represents each channel with adapter, base address, event flag, and transfer-in-progress state. `struct adapter_info` owns channel array and suspend flag. Core functions are `pch_i2c_init()`, `pch_i2c_wait_for_bus_idle()`, `pch_i2c_wait_for_check_xfer()`, `pch_i2c_writebytes()`, `pch_i2c_readbytes()`, `pch_i2c_handler()`, `pch_i2c_xfer()`, `pch_i2c_probe()`, and `pch_i2c_remove()`.

## Control Flow
PCI probe allocates adapter info, enables PCI, requests BARs, maps BAR1, sets channel count from PCI ID driver data, initializes per-channel adapters and MMIO offsets, requests a shared IRQ, initializes each channel, and registers numbered adapters. Transfers take a global mutex, reject suspended controllers, mark in-progress, then dispatch each message to read/write helpers. IRQ scans all channels in normal mode, records event bits, clears status, and wakes the wait queue.

## State And Persistence
Global module parameters `pch_i2c_speed` and `pch_clk` affect initialization. A global wait queue and mutex serialize activity. Per-channel event flags capture interrupt results until consumed. Suspend marks all channels suspended and waits for in-progress transfers.

## Dependencies And Integration Points
Depends on PCI IDs, MMIO, shared IRQs, wait queues, Linux I2C core, and SIMPLE_DEV_PM_OPS. Adapter class is HWMON.

## Risks
Global mutex serializes all channels. Event and wait queue are global, so cross-channel IRQ behavior relies on event flags. Buffer and EEPROM modes are declared but normal mode is the only supported mode in the handler. The code mutates `pmsg->flags` by ORing `pch_buff_mode_en`, which is risky if flags are reused. Suspend waits with polling sleeps.

## Test Signals
Test one- and two-channel PCI devices, 7-bit/10-bit reads and writes, repeated starts, arbitration lost retry, NACK to `-ENXIO`, timeout reinitialization, shared IRQ dispatch per channel, suspend during idle and active transfer, and module speed/clock parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-eg20t.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-elektor.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-elektor.c

## Purpose
Legacy ISA/optional memory-mapped PCF8584 adapter driver for Elektor-style hardware. It supplies low-level PCF register callbacks to the generic `i2c-algo-pcf` algorithm.

## Important APIs, Types, And Functions
Global module parameters define `base`, `irq`, `clock`, `own`, and `mmapped`. `pcf_isa_data` provides callbacks `pcf_isa_setbyte()`, `pcf_isa_getbyte()`, `pcf_isa_getown()`, `pcf_isa_getclock()`, and `pcf_isa_waitforpin()`. ISA binding uses `elektor_match()`, `elektor_probe()`, and `elektor_remove()`. `pcf_isa_handler()` wakes waiters when IRQ mode is used.

## Control Flow
Match optionally autodetects Alpha UP2000 memory-mapped PCF8584 hardware, validates base settings, and supplies a default I/O base. Probe initializes the wait queue, maps I/O or memory region, requests IRQ if configured, assigns device parent, and calls `i2c_pcf_add_bus()`. The algorithm then uses callbacks to read/write data/control registers and wait for pin events either by IRQ wait or delay polling.

## State And Persistence
This driver supports a single global adapter instance. Register base mapping, pending IRQ flag, wait queue, and spinlock are global. Module parameters are the configuration interface.

## Dependencies And Integration Points
Depends on ISA driver core, PCF8584 algorithm support, I/O port or MMIO resource mapping, optional PCI probing on Alpha, IRQs, and HWMON adapter class.

## Risks
Single-instance global state limits scalability. IRQ request failure silently falls back to polling. Legacy hardware parameters are user supplied and can conflict with real resources. Alpha-specific double writes and autodetect paths are platform-sensitive.

## Test Signals
Test I/O-port and MMIO mapping, module parameter combinations, IRQ and polling wait paths, PCF algorithm adapter registration, resource cleanup on `i2c_pcf_add_bus()` failure, and remove after active registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-elektor.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-emev2.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-emev2.c

## Purpose
Renesas EMEV2 I2C adapter with both master and slave support. It drives an interrupt/completion master transfer path and translates addressed slave events into Linux I2C slave callbacks.

## Important APIs, Types, And Functions
`struct em_i2c_device` stores MMIO base, adapter, completion, registered slave, and IRQ. Core functions include `em_i2c_reset()`, `__em_i2c_xfer()`, `em_i2c_xfer()`, `em_i2c_slave_irq()`, `em_i2c_irq_handler()`, `em_i2c_reg_slave()`, `em_i2c_unreg_slave()`, and probe/remove.

## Control Flow
Probe maps MMIO, enables the `sclk`, initializes adapter fields, resets hardware, requests IRQ, and registers the adapter. Master transfer checks bus busy, then for each message sends START, address, waits for events, handles NACK/arbitration loss, reads or writes bytes, and optionally sends STOP. IRQ first gives slave handling a chance; if not handled as slave, it completes the master wait. Slave IRQ handling filters extension codes and stop events, handles addressed read/write directions, calls `i2c_slave_event()`, and writes or reads the shift register.

## State And Persistence
State is in MMIO registers, `msg_done` completion, and optional `slave` pointer. Adapter timeout and retries are configured at probe. No persistent storage exists.

## Dependencies And Integration Points
Depends on OF compatible `renesas,iic-emev2`, platform MMIO/IRQ, enabled clock `sclk`, Linux I2C master and slave APIs, completions, and IRQ synchronization.

## Risks
Master and slave share IRQ flow; stop detection may be ambiguous and can deliberately fall through to master completion. NACK is returned as `-ENXIO`; arbitration loss returns `-EAGAIN`. Slave unregister relies on clearing SVA and `synchronize_irq()` to avoid stale slave pointer use.

## Test Signals
Test master read/write/repeated messages, bus-busy `-EAGAIN`, NACK handling, arbitration-loss reset, slave write/read/stop events, slave unregister racing with IRQ, timeout reset, and adapter registration/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-emev2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-exynos5.c -->
# sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-exynos5.c

## Purpose
Samsung Exynos5/Exynos7/ExynosAutoV9/Exynos8895 high-speed I2C master adapter. It supports auto-mode FIFO transfers, variant timing formulas, bus recovery, atomic transfers by polling IRQ status, and noirq system PM.

## Important APIs, Types, And Functions
`struct exynos5_i2c` stores adapter, active message, completion, message pointer, IRQ, MMIO registers, clocks, device, state, spinlock, transfer-done latch, atomic flag, operating clock, and variant data. `struct exynos_hsi2c_variant` captures FIFO depth and hardware type. Core functions are `exynos5_i2c_set_timing()`, `exynos5_hsi2c_clock_setup()`, `exynos5_i2c_init()`, `exynos5_i2c_reset()`, `exynos5_i2c_irq()`, `exynos5_i2c_message_start()`, `exynos5_i2c_xfer_msg()`, `exynos5_i2c_xfer()`, and `exynos5_i2c_xfer_atomic()`.

## Control Flow
Probe reads `clock-frequency`, gets `hsi2c` and optional `hsi2c_pclk`, enables clocks, maps MMIO, clears stale interrupts, initializes lock/completion, requests IRQ, loads variant data, programs timings, resets/init hardware, registers the adapter, then disables clocks. Transfers enable clocks, process messages one by one, program address/FIFO/interrupt/auto-conf, wait for completion or poll IRQs in atomic mode, wait for bus idle on final stop, reset on errors, and disable clocks. IRQ handles variant-specific transfer status, drains RX FIFO or fills TX FIFO, disables interrupts, clears pending IRQs, and completes.

## State And Persistence
Transfer state is `msg`, `msg_ptr`, `state`, `trans_done`, and `atomic`. `trans_done` is latched because the hardware bit clears on read. Timings and controller mode are restored on reset/resume.

## Dependencies And Integration Points
Depends on OF compatible table for Samsung variants, clocks, MMIO, IRQs, spinlocks, I2C core, and noirq PM callbacks. Functionality excludes SMBus quick.

## Risks
Timing math differs by hardware variant and can fail on unsupported clock combinations. FIFO trigger levels depend on message length and FIFO depth. Bus recovery manually toggles auto/manual mode and emits read clocks/STOP for stuck SDA on newer variants. Atomic mode disables the IRQ and calls the IRQ handler manually, so locking and status polling must remain IRQ-safe.

## Test Signals
Test each OF variant, 100 kHz/400 kHz/1 MHz timing, read/write FIFO boundary lengths, transfer-done/error status mapping, timeout reset, bus recovery from stuck master state, atomic transfers, clock enable/disable balance, and noirq suspend/resume.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/i2c/busses/i2c-exynos5.c -->
