# subset-b-005590 Research

Grouped source research for Linux one-wire netlink connector support and watchdog driver configuration/build files plus selected platform watchdog implementations. Each section is marker-delimited for deterministic reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.c -->
# sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.c` implements the kernel side of the 1-Wire connector/netlink API when `CONFIG_W1_CON` and connector support are available. It accepts userspace connector messages, dispatches master and slave commands to the 1-Wire core, formats replies and command status records, sends asynchronous notifications for master/slave events, and provides empty stubs when the connector path is not built. The complete 740-line source was read for this report.

## Important APIs, Types, and Functions

The public entry points are `w1_netlink_send()`, `w1_init_netlink()`, and `w1_fini_netlink()`. `w1_init_netlink()` registers `w1_cn_callback()` with connector id `CN_W1_IDX/CN_W1_VAL`; `w1_fini_netlink()` unregisters it. Internal state is centered on `struct w1_cb_block`, a single allocation containing a copied request, async nodes, and a reply buffer, and `struct w1_cb_node`, which embeds `struct w1_async_cmd` for the master worker thread. Important helpers include `w1_reply_len()`, `w1_reply_make_space()`, `w1_netlink_setup_msg()`, `w1_netlink_queue_cmd()`, `w1_netlink_queue_status()`, `w1_netlink_send_error()`, `w1_process_command_master()`, `w1_process_command_slave()`, `w1_process_cb()`, `w1_list_count_cmds()`, and `w1_process_command_root()`.

## Control Flow

Kernel notifications use `w1_netlink_send()` to wrap a `struct w1_netlink_msg` inside a connector message and broadcast it. Userspace requests enter `w1_cn_callback()`, which validates connector flags, scans all embedded `w1_netlink_msg` records to count async work nodes and estimate reply space, allocates a `w1_cb_block`, and then walks the message stream again. `W1_LIST_MASTERS` is handled synchronously by `w1_process_command_root()`. `W1_MASTER_CMD` and `W1_SLAVE_CMD` resolve a master or slave, take the relevant references, enqueue a `w1_async_cmd` on the master's `async_list`, and wake the master thread. The worker invokes `w1_process_cb()`, locks `bus_mutex`, optionally resets/selects the slave, iterates embedded `w1_netlink_cmd` records, executes I/O, reset, search, list, add, or remove operations, and queues both data replies and status replies. When the block reference count drops to zero, `w1_unref_block()` sends any pending bundled reply and frees the allocation.

## State and Persistence Behavior

All persistent kernel state belongs to the 1-Wire core: master lists, slave lists, slave references, master reference counts, and the master's async queue. This file owns only transient request/reply state in `w1_cb_block`. `block->request_cn` preserves the original connector message while `block->first_cn`, `block->cn`, `block->msg`, and `block->cmd` advance through an in-place reply buffer. `block->refcnt` protects the reply buffer across async nodes; the initial callback and each queued node hold references. No state is written to disk. Replies may be bundled when `W1_CN_BUNDLE` is set, or flushed early after each command when bundling is not requested.

## Dependencies and Integration Points

The file depends on connector/netlink (`cn_add_callback`, `cn_del_callback`, `cn_netlink_send`, `cn_netlink_send_mult`), skbuff netlink metadata for `portid`, the 1-Wire core structures and helpers from `w1_internal.h`, and message definitions from `w1_netlink.h`. Integration points include `w1_masters`, `w1_mlock`, `w1_search_master_id()`, `w1_search_slave()`, `w1_unref_slave()`, `w1_slave_found()`, `w1_search_process_cb()`, `w1_reset_bus()`, `w1_reset_select_slave()`, block read/write/touch helpers, and slave attach/detach helpers.

## Risks and Edge Cases

The code parses variable-length nested messages and relies on careful length checks before advancing pointers; malformed `len` fields are rejected with `-E2BIG` or `-EPROTO`. `w1_netlink_msg.status` is an 8-bit field populated with `(u8)-error`, so consumers must interpret status as the protocol expects. Reply construction is in-place and split by `CONNECTOR_MAX_MSG_SIZE`; incorrect size estimates could fragment replies or force early sends. `dev->priv` is temporarily used as a back pointer during processing under `bus_mutex`, so any future users of that field would conflict. The async enqueue path can send direct errors after other async work is live because the shared reply block is not locked in the callback. Stub builds silently discard notifications and report successful init.

## Test Signals

Useful checks include compiling with connector enabled and disabled; userspace tests for `W1_LIST_MASTERS`, master commands, slave commands, search/list-slave replies, add/remove error cases, and unknown flags; malformed nested length fuzzing; bundled and unbundled reply-size boundary tests; and concurrency tests where multiple master/slave command messages share one connector request while slaves appear or disappear.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.h -->
# sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.h` defines the 1-Wire netlink connector wire protocol shared by the kernel implementation and in-kernel callers. It names connector flags, top-level 1-Wire message types, command opcodes, flexible-array message layouts, and kernel-only function prototypes. The complete 135-line header was read for this report.

## Important APIs, Types, and Functions

`enum w1_cn_msg_flags` currently exposes `W1_CN_BUNDLE`, allowing a userspace request to ask for bundled replies. `enum w1_netlink_message_types` defines notifications and requests such as `W1_SLAVE_ADD`, `W1_SLAVE_REMOVE`, `W1_MASTER_ADD`, `W1_MASTER_REMOVE`, `W1_MASTER_CMD`, `W1_SLAVE_CMD`, and `W1_LIST_MASTERS`. `struct w1_netlink_msg` contains `type`, `status`, payload `len`, a union of 8-byte slave id and master id, and flexible `data[]`. `enum w1_commands` defines `W1_CMD_READ`, `W1_CMD_WRITE`, `W1_CMD_SEARCH`, `W1_CMD_ALARM_SEARCH`, `W1_CMD_TOUCH`, `W1_CMD_RESET`, `W1_CMD_SLAVE_ADD`, `W1_CMD_SLAVE_REMOVE`, and `W1_CMD_LIST_SLAVES`. `struct w1_netlink_cmd` contains a command byte, reserved byte, payload length, and flexible data. Kernel builds see prototypes for `w1_netlink_send()`, `w1_init_netlink()`, and `w1_fini_netlink()`.

## Control Flow

The header has no executable control flow. It documents the nesting used by the source implementation: `nlmsghdr`, then `cn_msg`, then one or more `w1_netlink_msg` records, each optionally containing one or more `w1_netlink_cmd` records.

## State and Persistence Behavior

No storage is owned by the header. The structures are ABI layouts for transient connector messages. The `status` and `len` fields carry per-message or per-command result state across one request/reply exchange, and master/slave identifiers connect the message to state owned by the 1-Wire core.

## Dependencies and Integration Points

The header includes `<asm/types.h>`, `<linux/connector.h>`, and `w1_internal.h`. It integrates the 1-Wire subsystem with Linux connector by using connector messages as a transport and with userspace daemons/tools that know this exact binary layout.

## Risks and Edge Cases

This file is a protocol ABI: reordering enum values, changing field sizes, or altering structure packing would break existing userspace. The protocol uses flexible arrays and 16-bit lengths, so callers must validate nested lengths before dereferencing. Comments mention typo-level documentation issues, but the functional risk is ABI drift and inconsistent status interpretation.

## Test Signals

Signals include uapi-style binary layout checks, compile coverage in kernel and non-kernel include contexts, userspace request/reply compatibility tests against older tools, and negative parser tests for unsupported flags and malformed nested command lengths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/w1/w1_netlink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/watchdog/Kconfig

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/Kconfig` is the configuration registry for Linux watchdog support. It defines the top-level `WATCHDOG` menu, core framework and policy options, pretimeout governors, and a large catalog of hardware/software watchdog driver symbols grouped by architecture or bus type. The complete 2357-line file was read for this report.

## Important APIs, Types, and Functions

This is Kconfig data rather than C code. Key symbols include `WATCHDOG`, `WATCHDOG_CORE`, `WATCHDOG_NOWAYOUT`, `WATCHDOG_HANDLE_BOOT_ENABLED`, `WATCHDOG_OPEN_TIMEOUT`, `WATCHDOG_SYSFS`, `WATCHDOG_HRTIMER_PRETIMEOUT`, `WATCHDOG_PRETIMEOUT_GOV`, `WATCHDOG_PRETIMEOUT_GOV_NOOP`, and `WATCHDOG_PRETIMEOUT_GOV_PANIC`. Driver symbols relevant to this work item include `ACQUIRE_WDT`, `ADVANTECH_WDT`, `ADVANTECH_EC_WDT`, `AIROHA_WATCHDOG`, `ALIM1535_WDT`, `ALIM7101_WDT`, `APPLE_WATCHDOG`, `ARM_SMC_WATCHDOG`, `ARMADA_37XX_WATCHDOG`, `ASM9260_WATCHDOG`, `ASPEED_WATCHDOG`, `AT91RM9200_WATCHDOG`, `AT91SAM9X_WATCHDOG`, `ATH79_WDT`, `BCM2835_WDT`, `BCM47XX_WDT`, `BCM7038_WDT`, and `BCM_KONA_WDT`. The file also declares dependencies such as `HAS_IOPORT`, `PCI`, `OF`, `HAS_IOMEM`, architecture symbols, `COMPILE_TEST`, and selects such as `WATCHDOG_CORE`, `MFD_SYSCON`, `ISA_BUS_API`, `RESET_CONTROLLER`, or `REGMAP`.

## Control Flow

Kconfig evaluation flows from `menuconfig WATCHDOG`; all subordinate options are only visible inside `if WATCHDOG`. Core options and pretimeout choices come first, followed by architecture-independent drivers, ARM, x86, MIPS, PowerPC, and other architecture groups, then ISA/PCI/USB card drivers. `choice` selects the default pretimeout governor when governor support is enabled. Driver `depends on`, `select`, and `default` lines determine whether the corresponding object can be built and whether helper subsystems are pulled in.

## State and Persistence Behavior

The file contributes build-time state to `.config`. Some options also influence runtime behavior through defaults used by drivers or the watchdog core, especially `WATCHDOG_NOWAYOUT`, `WATCHDOG_HANDLE_BOOT_ENABLED`, and `WATCHDOG_OPEN_TIMEOUT`. No runtime storage is owned here.

## Dependencies and Integration Points

The main integration is with `drivers/watchdog/Makefile`, which maps each `CONFIG_*` symbol to an object file. It also integrates with driver source assumptions: symbols that do not select `WATCHDOG_CORE` generally provide their own legacy miscdevice interface, while modern watchdog-core drivers select `WATCHDOG_CORE`. Architecture and bus dependencies prevent drivers from appearing where required register access, platform discovery, or firmware interfaces are absent.

## Risks and Edge Cases

Over-broad `COMPILE_TEST` paths can expose missing includes or unguarded architecture assumptions. Missing `select WATCHDOG_CORE` for a core-based driver would cause link failures; selecting too much can force unintended dependencies. Legacy drivers that do not use `WATCHDOG_CORE` still share `/dev/watchdog` semantics and may conflict with core drivers at runtime. Dependency changes affect whether users can build critical reset paths such as Apple or Aspeed watchdogs.

## Test Signals

Run Kconfig and allmodconfig/allnoconfig/allyesconfig build coverage across representative architectures; verify each enabled symbol builds the object listed in `Makefile`; check `COMPILE_TEST` combinations; and validate visible prompts/help text for new or changed watchdog entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/Makefile -->
# sources/distributed-fs/ceph-client/drivers/watchdog/Makefile

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/Makefile` maps watchdog Kconfig symbols to compiled objects. It builds the watchdog core, optional pretimeout infrastructure and governors, and every enabled hardware/software watchdog driver object in an order chosen to favor physical ISA/PCI/USB devices before architecture-specific and software fallbacks. The complete 243-line file was read for this report.

## Important APIs, Types, and Functions

This is kbuild data. Key assignments include `obj-$(CONFIG_WATCHDOG_CORE) += watchdog.o`, `watchdog-objs += watchdog_core.o watchdog_dev.o`, optional core additions for `watchdog_pretimeout.o` and `watchdog_hrtimer_pretimeout.o`, and governor objects `pretimeout_noop.o` and `pretimeout_panic.o`. Relevant object mappings include `acquirewdt.o`, `advantechwdt.o`, `advantech_ec_wdt.o`, `airoha_wdt.o`, `alim1535_wdt.o`, `alim7101_wdt.o`, `apple_wdt.o`, `arm_smc_wdt.o`, `armada_37xx_wdt.o`, `asm9260_wdt.o`, `aspeed_wdt.o`, `at91rm9200_wdt.o`, `at91sam9_wdt.o`, `ath79_wdt.o`, `bcm2835_wdt.o`, `bcm47xx_wdt.o`, `bcm7038_wdt.o`, and `bcm_kona_wdt.o`.

## Control Flow

Kbuild includes objects conditionally based on `CONFIG_*` values from Kconfig. Composite object `watchdog.o` is assembled from core pieces plus optional pretimeout components. The file is organized by hardware/bus or architecture, with comments explaining that ISA/PCI/USB cards are probed first, then architecture-specific watchdogs, then the software watchdog fallback.

## State and Persistence Behavior

No runtime state is owned. The Makefile determines which object files become built-in or modules, and therefore which init/probe paths can exist in a kernel image.

## Dependencies and Integration Points

The file must remain consistent with Kconfig symbol names and source filenames. It integrates with kernel build ordering, module naming, and composite object rules. Multi-object examples such as `watchdog-y` and `octeon-wdt-y` show where one logical module contains multiple translation units.

## Risks and Edge Cases

Typos between Kconfig symbol names and object mappings silently omit drivers or cause build failures. Ordering changes can matter when multiple watchdogs compete for `/dev/watchdog` or restart priority. Adding a driver without matching Kconfig dependency coverage can expose architecture-specific code to unsupported builds.

## Test Signals

Build tests with the listed symbols set to `y` and `m`, module-install checks for expected module names, and diff checks that every watchdog driver symbol in Kconfig has a corresponding object when applicable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/acquirewdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/acquirewdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/acquirewdt.c` is a legacy `/dev/watchdog` miscdevice driver for Acquire single-board computer watchdog hardware controlled by two x86 I/O ports. It starts or pings the timer by reading one port and stops it by reading another. The complete 328-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `wdt_stop`, `wdt_start`, and `nowayout`. Runtime helpers are `acq_keepalive()` and `acq_stop()`. File operations are `acq_write()`, `acq_ioctl()`, `acq_open()`, and `acq_close()` with `compat_ptr_ioctl`. Platform lifecycle functions are `acq_probe()`, `acq_remove()`, `acq_shutdown()`, `acq_init()`, and `acq_exit()`. State variables include `acq_platform_device`, `acq_is_open`, and `expect_close`.

## Control Flow

Module init creates a synthetic platform device and probes `acquirewdt_driver`. Probe reserves the stop and start I/O regions and registers a miscdevice on `WATCHDOG_MINOR`. Opening `/dev/watchdog` enforces single-open via `test_and_set_bit()`, optionally pins the module for nowayout, and starts the hardware with `acq_keepalive()`. Writes scan for magic close character `V` when nowayout is false and always ping on nonzero writes. Ioctls expose support, status, enable/disable, keepalive, and a fixed unknown timeout value of `0`. Release stops only after a magic close; otherwise it logs a critical warning and pings again. Shutdown stops the watchdog on soft shutdown.

## State and Persistence Behavior

The driver stores only process-open state and the magic-close flag. Hardware state persists in the board watchdog until refreshed, stopped, or timeout reset occurs. The actual timeout is jumper-selected and not discoverable by the driver.

## Dependencies and Integration Points

It depends on `HAS_IOPORT` style x86 port access (`inb_p()`), platform device/driver plumbing, miscdevice registration, watchdog ioctl constants, and userspace `/dev/watchdog` ABI expectations. It is selected by `CONFIG_ACQUIRE_WDT` and built as `acquirewdt.o`.

## Risks and Edge Cases

The hardware cannot be probed safely, so wrong module parameters can read unrelated I/O ports. `WATCHDOG_HEARTBEAT` is reported as zero because the hardware timeout is jumper-defined. The legacy miscdevice path lacks watchdog-core conveniences such as automatic device-managed registration, sysfs reporting, and framework-managed boot-running handling. Unexpected close deliberately leaves the watchdog armed.

## Test Signals

Check I/O region reservation failure handling, single-open behavior, magic close and nowayout behavior, `WDIOC_SETOPTIONS`, `WDIOC_KEEPALIVE`, reported timeout, platform remove cleanup, and shutdown stop behavior on target hardware or an I/O-port emulator.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/acquirewdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/advantech_ec_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/advantech_ec_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/advantech_ec_wdt.c` is a watchdog-core driver for Advantech systems with an ITE-based embedded controller. It probes the EC at fixed I/O ports, programs enable and reset delays through EC command/data registers, and registers a `watchdog_device`. The complete 205-line source was read for this report.

## Important APIs, Types, and Functions

Module parameter `timeout` selects the default timeout from `MIN_TIME` to `MAX_TIME`. EC access is serialized by timing helpers `adv_ec_wdt_timing_gate()`, `adv_ec_wdt_outb()`, and `adv_ec_wdt_inb()` to enforce at least `EC_MIN_DELAY` milliseconds between I/O accesses. Watchdog operations are `adv_ec_wdt_ping()`, `adv_ec_wdt_set_timeout()`, `adv_ec_wdt_start()`, and `adv_ec_wdt_stop()`. The global `adv_ec_wdt_dev` contains info, ops, min/max/default timeout. Probe and registration flow through `adv_ec_wdt_init()`, `adv_ec_wdt_probe()`, and `adv_ec_wdt_exit()` using `struct isa_driver`.

## Control Flow

Module init temporarily reserves the EC I/O range, sends `EC_CMD_EC_PROBE`, reads a magic value, releases the range, and only registers the ISA driver if the EC responds with `EC_MAGIC`. Probe then reserves the ports with devm, initializes timeout, arranges stop-on-reboot and stop-on-unregister, and registers the watchdog. Starting sets the timeout then writes `EC_CMD_WDT_START`; ping writes `EC_CMD_WDT_RESET`; stop writes `EC_CMD_WDT_STOP`.

## State and Persistence Behavior

Driver state is mostly in the singleton `watchdog_device` and `ec_timestamp` timing gate. Hardware timeout state is stored in EC registers with a 100 ms base. The driver clears BIOS-provided enable delay before writing reset delay, so probe/start normalizes EC timing state.

## Dependencies and Integration Points

It depends on ISA bus API, fixed I/O ports `0x299/0x29a`, watchdog core, module parameters, and `devm_watchdog_register_device()`. Kconfig selects `ISA_BUS_API` and `WATCHDOG_CORE`; Makefile builds `advantech_ec_wdt.o`.

## Risks and Edge Cases

The driver is for a specific EC family; fixed-port probing could conflict if another device decodes the range. EC access requires the timing gate; bypassing it risks missed commands. There is no explicit nowayout module parameter in this file, so policy follows watchdog core defaults and configuration rather than a local parameter. The singleton `watchdog_device` assumes one device instance.

## Test Signals

Useful tests include EC probe success/failure, timeout min/max validation, command ordering on start/stop/ping, delay enforcement between I/O accesses, stop-on-reboot behavior, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/advantech_ec_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/advantechwdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/advantechwdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/advantechwdt.c` is a legacy miscdevice watchdog driver for Advantech single-board computers. It controls a watchdog by writing a 1-63 second timeout value to a start I/O port and disabling by reading a stop I/O port. The complete 337-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `wdt_stop`, `wdt_start`, `timeout`, and `nowayout`. Core helpers are `advwdt_ping()`, `advwdt_disable()`, and `advwdt_set_heartbeat()`. File operations are `advwdt_write()`, `advwdt_ioctl()`, `advwdt_open()`, and `advwdt_close()`. Platform lifecycle functions are `advwdt_probe()`, `advwdt_remove()`, `advwdt_shutdown()`, `advwdt_init()`, and `advwdt_exit()`.

## Control Flow

Module init creates a synthetic platform device and probes it. Probe reserves start/stop I/O ports, validates or resets the timeout, and registers `/dev/watchdog`. Open enforces single access and immediately pings. Writes scan for magic close `V` when stoppable and ping the hardware. Ioctls expose support/status, enable/disable, keepalive, set timeout, and get timeout. Close disables only when the magic close flag was set; otherwise it pings and leaves the device armed. Shutdown disables on soft shutdown.

## State and Persistence Behavior

State is held in `timeout`, `advwdt_is_open`, and `adv_expect_close`. Hardware state persists in the board watchdog until the port write refreshes it, the stop port disables it, or a timeout resets the machine.

## Dependencies and Integration Points

It depends on x86 I/O port access, platform driver helpers, miscdevice registration on `WATCHDOG_MINOR`, watchdog ioctl constants, and user-space watchdog daemon conventions. Kconfig symbol `ADVANTECH_WDT` maps to `advantechwdt.o`.

## Risks and Edge Cases

The board is not safely probeable, so incorrect ports can affect unrelated hardware. The timeout range is narrow and driver-enforced; out-of-range module parameters silently fall back to default. Legacy miscdevice code does not participate in watchdog core boot-running management or sysfs. Unexpected close intentionally keeps the watchdog active.

## Test Signals

Check port reservation and cleanup, timeout validation at 0/1/63/64 seconds, `WDIOC_SETTIMEOUT` fallthrough to get timeout, magic close behavior, nowayout behavior, and shutdown disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/advantechwdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/airoha_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/airoha_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/airoha_wdt.c` is a watchdog-core platform driver for the Airoha EN7581 SoC watchdog timer, implemented using timer3 registers. It maps MMIO registers, derives the watchdog tick rate from the bus clock, and exposes start/stop/ping/timeout/timeleft operations. The complete 216-line source was read for this report.

## Important APIs, Types, and Functions

`struct airoha_wdt_desc` stores the embedded `watchdog_device`, computed `wdt_freq`, and MMIO base. Module parameters are `heartbeat` and `nowayout`. Operations are `airoha_wdt_start()`, `airoha_wdt_stop()`, `airoha_wdt_ping()`, `airoha_wdt_set_timeout()`, and `airoha_wdt_get_timeleft()`. Probe is `airoha_wdt_probe()`, and PM hooks are `airoha_wdt_suspend()` and `airoha_wdt_resume()`.

## Control Flow

Probe allocates state, maps resource 0, enables the `bus` clock, computes watchdog frequency as half the bus clock, initializes the watchdog device, sets max timeout from the 32-bit timer field, applies nowayout and stop-on-unregister, then registers the device. Start enables the watchdog timer, watchdog reset, and timer interrupt bits, then writes load value as timeout times watchdog frequency. Ping writes the reload bit. Setting timeout restarts the hardware when active. Suspend stops active watchdogs; resume restarts and pings active watchdogs.

## State and Persistence Behavior

Runtime state is in watchdog-core fields and MMIO timer registers. The driver does not persist configuration beyond the active device. During suspend it stops hardware if active, then restores on resume based on watchdog-core active state.

## Dependencies and Integration Points

It depends on platform device resources, OF compatible `airoha,en7581-wdt`, clock framework, MMIO accessors, bitfield helpers, and watchdog core. Kconfig `AIROHA_WATCHDOG` selects `WATCHDOG_CORE`; Makefile maps it to `airoha_wdt.o`.

## Risks and Edge Cases

The stop path uses `val &= (~WDT_ENABLE & ~WDT_TIMER_ENABLE)`, which relies on bitwise combination behavior and deserves review if flags change. `wdt_freq` depends on a nonzero clock rate, but the code does not explicitly reject zero. Restarting on timeout change leaves a short stop/start window. Suspend stops the watchdog even under nowayout policy if watchdog core calls suspend.

## Test Signals

Test DT matching, bus clock enable failure, max-timeout calculation, start register bits, reload writes, get-timeleft conversion, timeout change while inactive and active, and suspend/resume restoration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/airoha_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/alim1535_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/alim1535_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/alim1535_wdt.c` is a legacy miscdevice watchdog driver for the ALi M1535 PMU watchdog associated with the ALi 7101 PMU. It scans PCI devices, programs watchdog bits in PCI config register `0xCC`, and exposes `/dev/watchdog` ioctls. The complete 450-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `timeout` and `nowayout`. Hardware helpers are `ali_start()`, `ali_stop()`, `ali_keepalive()`, and `ali_settimer()`. Userspace interface functions are `ali_write()`, `ali_ioctl()`, `ali_open()`, and `ali_release()`. System and module lifecycle functions are `ali_notify_sys()`, `ali_find_watchdog()`, `watchdog_init()`, and `watchdog_exit()`. State includes `ali_is_open`, `ali_expect_release`, `ali_pci`, `ali_timeout_bits`, and `ali_lock`.

## Control Flow

Init scans for an ALi bridge and 7101 PMU, enables the PMU PCI device, clears/reset watchdog monitor bits, validates timeout, computes encoded timeout bits, registers a reboot notifier, and registers `/dev/watchdog`. Open starts the watchdog. Writes optionally set magic close and restart the timer. Ioctls expose status, enable/disable, keepalive, set/get timeout. The reboot notifier stops on `SYS_DOWN` or `SYS_HALT`. Exit stops hardware, deregisters miscdevice/notifier, and releases the PCI device reference.

## State and Persistence Behavior

The encoded timeout is cached in `ali_timeout_bits`; hardware state lives in PCI config space register `0xCC`. `ali_lock` serializes config-space updates. There is no disk persistence. The driver keeps the watchdog running after unexpected close.

## Dependencies and Integration Points

It depends on PCI config access, legacy miscdevice watchdog ABI, reboot notifier API, and watchdog ioctl definitions. Kconfig `ALIM1535_WDT` depends on x86/PCI and maps to `alim1535_wdt.o`.

## Risks and Edge Cases

The driver does not register a real `pci_driver`; it scans devices manually and exports a PCI table only for module metadata. Timeout encoding has multiple ranges and rejects negative or >=18000 seconds. `nowayout` is declared but not used to pin the module on open, unlike some legacy drivers. Failure paths after `pci_enable_device()` rely on later `pci_dev_put()` but do not disable the device.

## Test Signals

Test PCI detection absence, timeout encoding boundaries, config register bit masking, spinlock-covered start/stop races, magic close and unexpected close behavior, reboot notifier stop, and module unload cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/alim1535_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/alim7101_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/alim7101_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/alim7101_wdt.c` is a legacy miscdevice driver for the ALi M7101 PMU watchdog. Because the hardware watchdog timeout is very short, the driver maintains its own kernel timer to ping hardware about every quarter second while requiring userspace to refresh a longer software heartbeat. The complete 450-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `timeout`, `use_gpio`, and `nowayout`. Important state includes `timer`, `next_heartbeat`, `wdt_is_open`, `wdt_expect_close`, and `alim7101_pmu`. Hardware functions are `wdt_timer_ping()`, `wdt_change()`, `wdt_startup()`, `wdt_turnoff()`, and `wdt_keepalive()`. File operations are `fop_write()`, `fop_open()`, `fop_close()`, and `fop_ioctl()`. Lifecycle and system paths are `alim7101_wdt_init()`, `alim7101_wdt_unload()`, `wdt_notify_sys()`, and `wdt_restart_handle()`.

## Control Flow

Init finds the M7101 PMU and compatible M1533 south bridge, configures the PMU watchdog to a one-second timeout, handles old revision GPIO mode requirements, validates timeout, registers reboot and restart handlers, and registers `/dev/watchdog`. Open starts the watchdog and schedules the ping timer. Userspace writes extend `next_heartbeat` and optionally set magic close. The timer periodically re-arms the PMU only while `jiffies` is before `next_heartbeat`; otherwise it logs that the heartbeat was lost and stops pinging so hardware can reset. The restart handler enables the watchdog and spins until reset.

## State and Persistence Behavior

The driver maintains two layers of state: hardware is kept alive by the kernel timer, while userspace health is represented by `next_heartbeat`. Optional GPIO toggling supports old Cobalt hardware. Hardware configuration persists in PCI config bytes until changed or reset.

## Dependencies and Integration Points

It depends on PCI config access, timer APIs, reboot and restart notifier APIs, miscdevice `/dev/watchdog`, and watchdog ioctls. Kconfig `ALIM7101_WDT` depends on PCI and maps to `alim7101_wdt.o`.

## Risks and Edge Cases

The close path has a comment questioning whether the timer should be deleted on unexpected close; leaving it alive means hardware will continue to be serviced until the software heartbeat expires. Old revision detection can force `nowayout`. The restart handler busy-loops forever by design. Manual PCI probing and config writes are sensitive to revision checks and `use_gpio`.

## Test Signals

Check timer-driven ping cadence, heartbeat expiration reset path, magic close stop, nowayout on old hardware, timeout boundaries, GPIO mode transitions, reboot notifier shutdown, restart handler behavior, and failure unwind for notifier/misc registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/alim7101_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/apple_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/apple_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/apple_wdt.c` is a watchdog-core platform driver for Apple SoC watchdog hardware. It uses watchdog channel WD1 for normal machine reset, provides restart support, and restores active watchdog state across suspend/resume. The complete 238-line source was read for this report.

## Important APIs, Types, and Functions

`struct apple_wdt` stores an embedded `watchdog_device`, MMIO base, and clock rate. Operations are `apple_wdt_start()`, `apple_wdt_stop()`, `apple_wdt_ping()`, `apple_wdt_set_timeout()`, `apple_wdt_get_timeleft()`, and `apple_wdt_restart()`. Probe is `apple_wdt_probe()`, with PM hooks `apple_wdt_suspend()` and `apple_wdt_resume()`. The OF match is `apple,wdt`.

## Control Flow

Probe allocates state, maps registers, enables and reads the clock, computes maximum hardware heartbeat from a 32-bit counter, detects whether WD1 reset is already enabled and marks `WDOG_HW_RUNNING`, initializes timeout, writes the bite time, arranges stop-on-unregister, sets restart priority, and registers the device. Start clears WD1 current time and enables reset. Ping resets current time. Timeout writes WD1 bite time, clamping the hardware interval to `max_hw_heartbeat_ms` while preserving userspace timeout in `wdd->timeout`. Restart enables WD1 reset, sets bite and current time to zero, flushes writes, and waits about 150 ms.

## State and Persistence Behavior

Runtime state is in `watchdog_device` and WD1 MMIO registers. Existing bootloader-enabled WD1 state is detected. Suspend stops if active or hardware-running; resume restarts under the same condition. No nonvolatile state is stored.

## Dependencies and Integration Points

The driver depends on OF platform binding `apple,wdt`, clock framework, MMIO access, watchdog core, and restart priority integration. It is selected by `APPLE_WATCHDOG` and built as `apple_wdt.o`.

## Risks and Edge Cases

Only WD1 is used; WD0 interrupt/pretimeout capability is documented but not implemented. `get_timeleft()` subtracts current from reset time and assumes no wrap or current greater than reset. Large requested timeouts rely on watchdog core max-hw-heartbeat management. Restart timing is based on observed reset latency.

## Test Signals

Test clock-rate zero failure, boot-running detection, timeout clamping, ping/start/stop register writes, restart reset timing, suspend/resume for active and inactive devices, and watchdog core handling of timeouts longer than hardware max.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/apple_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/arm_smc_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/arm_smc_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/arm_smc_wdt.c` is a watchdog-core platform driver for watchdogs implemented by ARM EL3 firmware and accessed through Secure Monitor Calls. It abstracts firmware operations such as init, set timeout, enable, pet, and get timeleft into watchdog-core callbacks. The complete 199-line source was read for this report.

## Important APIs, Types, and Functions

`enum smcwd_call` defines firmware subcommands `SMCWD_INIT`, `SMCWD_SET_TIMEOUT`, `SMCWD_ENABLE`, `SMCWD_PET`, and `SMCWD_GET_TIMELEFT`. `smcwd_call()` performs `arm_smccc_smc()` using the SMC function id stored in watchdog driver data and maps PSCI-style return codes to Linux errors. Watchdog operations include `smcwd_ping()`, `smcwd_get_timeleft()`, `smcwd_set_timeout()`, `smcwd_stop()`, and `smcwd_start()`. Probe is `smcwd_probe()`.

## Control Flow

Probe allocates a watchdog device, reads optional DT property `arm,smc-id` or defaults to `0x82003D06`, calls firmware init, chooses ops with or without `get_timeleft` based on firmware support, initializes min/max/default timeout from firmware return registers, applies nowayout and optional module timeout, programs the selected timeout, and registers the watchdog. Start/stop/ping/set/get callbacks are thin SMC wrappers.

## State and Persistence Behavior

The driver stores the SMC function id as watchdog driver data and stores timeout limits in `watchdog_device`. Actual watchdog state lives in secure firmware. Existing running state can be inferred when `SMCWD_GET_TIMELEFT` succeeds during probe.

## Dependencies and Integration Points

It depends on ARM SMCCC, PSCI return-code definitions, OF binding `arm,smc-wdt`, platform devices, and watchdog core. Kconfig requires ARM/ARM64, OF, and `HAVE_ARM_SMCCC`.

## Risks and Edge Cases

The contract with firmware is not self-describing beyond return codes; mismatched argument conventions or non-PSCI error semantics would produce incorrect Linux errors. `get_timeleft` support is optional and probe uses return values to select ops. The `watchdog_ops` structures lack `.owner`, unlike most drivers, which can matter for module reference expectations. Stop-on-reboot/unregister assumes firmware supports disable.

## Test Signals

Test firmware return-code mapping, default and DT-provided SMC ids, missing optional get-timeleft, min/max timeout propagation, timeout module parameter, nowayout behavior, and stop-on-reboot/unregister calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/arm_smc_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/armada_37xx_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/armada_37xx_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/armada_37xx_wdt.c` is a watchdog-core driver for Marvell Armada 37xx SoC timer counters. It uses counter 1 as the watchdog and counter 0 as a retrigger source to ping counter 1 without disabling it. The complete 359-line source was read for this report.

## Important APIs, Types, and Functions

`struct armada_37xx_watchdog` stores `watchdog_device`, CPU misc syscon regmap, MMIO counter registers, computed timeout ticks, clock rate, and clock handle. Helpers include `get_counter_value()`, `set_counter_value()`, `counter_enable()`, `counter_disable()`, `init_counter()`, and `armada_37xx_wdt_is_running()`. Watchdog operations are `armada_37xx_wdt_ping()`, `armada_37xx_wdt_get_timeleft()`, `armada_37xx_wdt_set_timeout()`, `armada_37xx_wdt_start()`, and `armada_37xx_wdt_stop()`. Probe and PM hooks are `armada_37xx_wdt_probe()`, `armada_37xx_wdt_suspend()`, and `armada_37xx_wdt_resume()`.

## Control Flow

Probe obtains the system controller phandle, maps timer registers, enables the clock, initializes min/max/default timeout, computes the counter value, checks if hardware is already running, applies nowayout and stop-on-reboot, then registers the watchdog. Start selects counter 1 as the watchdog in CPU misc registers, initializes counter 0 as one-shot retrigger, initializes counter 1 in hardware-signal mode triggered by the previous counter, loads timeout, enables counter 1, and fires counter 0. Ping disables/enables counter 0 to force a retrigger. Stop disables both counters and clears watchdog selection.

## State and Persistence Behavior

Timeout state is stored both in `wdd->timeout` and `dev->timeout` in clock ticks. Hardware state lives in the counters and CPU misc watchdog selection register. Running hardware from a bootloader is detected and represented as `WDOG_HW_RUNNING`.

## Dependencies and Integration Points

It depends on OF compatible `marvell,armada-3700-wdt`, a `marvell,system-controller` syscon phandle, clock framework, regmap, MMIO access, and watchdog core.

## Risks and Edge Cases

The design deliberately avoids counters 2 and 3 because firmware may enable them before U-Boot. Suspend unconditionally stops the watchdog and resumes only if watchdog core marks it active, so boot-running-but-not-open scenarios need framework coverage. Timeout calculation uses 64-bit counters and `do_div`; clock rate zero is rejected.

## Test Signals

Test syscon lookup, clock failures, boot-running detection, timeout conversion, counter low/high consistency, ping without disabling counter 1, suspend/resume active-state handling, and DT binding coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/armada_37xx_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/asm9260_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/asm9260_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/asm9260_wdt.c` is a watchdog-core driver for Alphascale ASM9260 watchdog hardware. It supports hardware reset, software-reset-via-interrupt, and debug modes, manages module and AHB clocks, and provides restart support. The complete 376-line source was read for this report.

## Important APIs, Types, and Functions

`struct asm9260_wdt_priv` stores device, watchdog, clocks, reset control, MMIO base, IRQ, watchdog frequency, and selected mode. Operations are `asm9260_wdt_feed()`, `asm9260_wdt_gettimeleft()`, `asm9260_wdt_enable()`, `asm9260_wdt_disable()`, `asm9260_wdt_settimeout()`, and `asm9260_restart()`. Other important functions are `asm9260_wdt_sys_reset()`, `asm9260_wdt_irq()`, `asm9260_wdt_get_dt_clks()`, `asm9260_wdt_get_dt_mode()`, and `asm9260_wdt_probe()`.

## Control Flow

Probe allocates state, maps registers, obtains reset control, enables/configures clocks, initializes watchdog min/max/default, parses `alphascale,mode`, optionally requests an IRQ for software/debug modes, sets restart priority, arranges stop-on-reboot/unregister, and registers the device. Start writes mode bits, updates timeout register, and feeds with the required `0xaa`/`0x55` sequence. Stop asserts/deasserts reset because hardware has no direct disable. Software reset modes use an IRQ handler to call `asm9260_wdt_sys_reset()` unless in debug mode. Restart forces a fast watchdog reset by writing a minimal timeout and bad feed value.

## State and Persistence Behavior

Runtime state includes selected mode, watchdog frequency, and timeout in `watchdog_device`. Hardware state is in WDMOD, WDTC, WDFEED, and WDTV registers. Clock enable state is devm-managed through cleanup actions. No disk persistence exists.

## Dependencies and Integration Points

The driver depends on OF compatible `alphascale,asm9260-wdt`, clock framework, reset controller, optional IRQ, MMIO access, and watchdog core. Kconfig selects both `WATCHDOG_CORE` and `RESET_CONTROLLER`.

## Risks and Edge Cases

Disabling by reset control assumes exclusive reset line access and safe reset semantics. Software/debug modes depend on an optional IRQ; missing IRQ changes behavior. `alphascale,mode` strings outside `hw`, `sw`, and `debug` fall back to hardware reset. The restart path intentionally writes an invalid feed pattern.

## Test Signals

Test clock setup and cleanup failure paths, reset-control disable, mode parsing, IRQ and no-IRQ modes, feed sequence, max-timeout calculation, restart behavior, and stop-on-reboot/unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/asm9260_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/aspeed_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/aspeed_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/aspeed_wdt.c` is a watchdog-core driver for Aspeed BMC watchdog blocks across AST2400, AST2500, AST2600, and AST2700. It supports reset-mode selection, external reset pulse configuration, boot status reporting, alternate-flash boot recovery sysfs, optional pretimeout interrupts, and restart. The complete 589-line source was read for this report.

## Important APIs, Types, and Functions

SoC data is described by `struct aspeed_wdt_config` and `struct aspeed_wdt_scu`; instance state is `struct aspeed_wdt`. Operations are `aspeed_wdt_start()`, `aspeed_wdt_stop()`, `aspeed_wdt_ping()`, `aspeed_wdt_set_timeout()`, `aspeed_wdt_set_pretimeout()`, and `aspeed_wdt_restart()`. Other important functions include `aspeed_wdt_enable()`, `aspeed_wdt_update_bootstatus()`, `access_cs0_show()`, `access_cs0_store()`, `aspeed_wdt_irq()`, `aspeed_wdt_probe()`, `aspeed_wdt_init()`, and `aspeed_wdt_exit()`.

## Control Flow

An `arch_initcall` registers the platform driver early. Probe matches OF compatible data, maps registers, optionally requests a pretimeout IRQ, initializes watchdog core fields, applies nowayout, builds a cached control word from DT properties such as `aspeed,reset-type`, `aspeed,external-signal`, and `aspeed,alt-boot`, normalizes already-running hardware, programs external pulse polarity/drive/duration and reset masks for newer SoCs, updates bootstatus via SCU regmap, conditionally exposes `access_cs0`, and registers the watchdog. Start writes reload, restart magic, and control. Ping writes restart magic. Pretimeout updates IRQ fields in control. Restart arms a short timeout and delays.

## State and Persistence Behavior

`wdt->ctrl` is the driver's cached hardware control policy. Boot reset cause is read and cleared through SCU reset-status registers. Alternate boot selection can persist in watchdog timeout status until userspace clears it through `access_cs0`. Hardware reload, timeout, reset mask, and external pulse configuration live in MMIO registers.

## Dependencies and Integration Points

It depends on OF compatible tables, syscon/regmap for SCU status, optional IRQs, sysfs attribute groups, watchdog pretimeout notifications, MMIO access, and watchdog core. It integrates with BMC boot media behavior through the alternate boot bits.

## Risks and Edge Cases

SoC-specific reset-status widths and shifts are subtle; incorrect config data can misreport or clear the wrong reset cause. External pulse write semantics require magic high-byte values on some SoCs. Pretimeout support depends on an IRQ and correct `irq_mask`. The driver normalizes already-enabled hardware, which may change bootloader choices. `access_cs0` is intentionally limited to older alternate-boot scenarios.

## Test Signals

Test all compatible strings, reset-type parsing, external-signal and pulse settings, reset-mask programming, bootstatus read/clear for each SoC generation, pretimeout IRQ notification, alternate-boot sysfs behavior, active bootloader watchdog normalization, and early init build coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/aspeed_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/at91rm9200_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/at91rm9200_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/at91rm9200_wdt.c` is a legacy miscdevice watchdog driver for the Atmel AT91RM9200 system timer watchdog. It accesses watchdog registers through a parent syscon regmap, exposes `/dev/watchdog`, and registers a restart handler. The complete 332-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `wdt_time` and conditionally `nowayout`. Hardware helpers are `at91_wdt_stop()`, `at91_wdt_start()`, `at91_wdt_reload()`, and `at91_wdt_settimeout()`. File operations include `at91_wdt_open()`, `at91_wdt_close()`, `at91_wdt_ioctl()`, and `at91_wdt_write()`. Platform and restart functions are `at91rm9200_restart()`, `at91wdt_probe()`, `at91wdt_remove()`, `at91wdt_shutdown()`, `at91wdt_suspend()`, `at91wdt_resume()`, `at91_wdt_init()`, and `at91_wdt_exit()`.

## Control Flow

Module init validates `wdt_time` and registers the platform driver. Probe ensures only one miscdevice parent, obtains the parent syscon regmap, registers `/dev/watchdog`, and registers a restart handler. Open starts the watchdog; writes reload; ioctls support enable/disable, keepalive, set/get timeout, and status. Close stops only if not nowayout. Shutdown and suspend stop the watchdog; resume restarts if the device was open. The restart handler writes mode and control registers to force a reset, delays, then logs failure if reset did not occur.

## State and Persistence Behavior

State is global: `wdt_time`, `nowayout`, `regmap_st`, and `at91wdt_busy`. Hardware mode is programmed into system timer registers and persists until changed or reset. The driver does not track magic close; close behavior is controlled directly by nowayout.

## Dependencies and Integration Points

It depends on MFD syscon for Atmel system timer registers, miscdevice watchdog ABI, reboot restart handler API, platform/OF binding `atmel,at91rm9200-wdt`, and watchdog ioctl constants.

## Risks and Edge Cases

The driver is legacy and not watchdog-core based, so behavior differs from newer AT91 watchdogs. Global singleton state prevents multiple instances. Timeout conversion assumes a 256 Hz watchdog clock and caps at 256 seconds. Suspend stops the watchdog even if userspace expects continuous monitoring.

## Test Signals

Test syscon lookup, single-instance guard, timeout boundaries, close under nowayout and stoppable modes, restart handler reset, suspend/resume open-state handling, and misc ioctl behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/at91rm9200_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.c` is a watchdog-core driver for Atmel AT91SAM9x and AT91CAP9 watchdog hardware. The hardware mode register can be written only once, and the hardware cannot really be stopped, so the driver uses a kernel timer to keep the hardware alive while watchdog-core active state represents userspace health. The complete 405-line source was read for this report.

## Important APIs, Types, and Functions

`struct at91wdt` stores watchdog device, MMIO base, next userspace heartbeat, kernel ping timer, desired/current mode bits, heartbeat interval, nowayout flag, IRQ, and slow clock. Helpers include `at91_wdt_reset()`, `at91_ping()`, `at91_wdt_start()`, `at91_wdt_stop()`, `at91_wdt_set_timeout()`, `at91_wdt_init()`, `of_at91wdt_init()`, `wdt_interrupt()`, `at91wdt_probe()`, and `at91wdt_remove()`.

## Control Flow

Probe builds default mode bits, maps registers, enables the slow clock, parses DT properties, and calls `at91_wdt_init()`. Init reads the hardware mode register, writes it only if still reset-default, rejects disabled hardware when Linux expects enabled watchdog, computes safe min/max ping intervals from watchdog value and delta window, optionally requests an IRQ for software watchdog mode, sets up a timer, starts periodic pinging quickly, initializes watchdog timeout from DT or module parameter, and registers the watchdog. `start()` updates `next_heartbeat`; `stop()` is a no-op because hardware cannot stop. The timer keeps pinging while userspace heartbeat is valid or watchdog is not active; otherwise it stops pinging and lets hardware reset.

## State and Persistence Behavior

The driver maintains a distinction between hardware liveness and userspace liveness. Hardware is continuously refreshed by `timer` unless userspace expires. `mr` and `mr_mask` record desired mode-register state, while the actual hardware register may already be fixed by boot firmware. Removal unregisters and deletes the timer but warns that hardware will probably reboot.

## Dependencies and Integration Points

It depends on `at91sam9_wdt.h` register definitions, OF properties such as `atmel,max-heartbeat-sec`, `atmel,min-heartbeat-sec`, `atmel,watchdog-type`, `atmel,reset-type`, `atmel,disable`, `atmel,idle-halt`, and `atmel,dbg-halt`, optional IRQ, slow clock, MMIO access, timers, and watchdog core.

## Risks and Edge Cases

Mode-register one-write semantics are high risk: bootloader configuration may be immutable and incompatible. Windowed watchdog timing can be too tight for Linux scheduling, producing warnings or rejection. `stop()` cannot stop hardware, so users may misunderstand close semantics. Software reset mode calls `emergency_restart()` from IRQ context.

## Test Signals

Test default and DT mode register construction, already-configured hardware warnings, disabled-watchdog rejection, min/max heartbeat calculations, IRQ software mode, timer ping cadence, userspace heartbeat expiration, remove behavior, and watchdog timeout initialization from DT/module parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.h -->
# sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.h

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.h` defines register offsets and bit fields for AT91 watchdog timer hardware used by the AT91SAM9 driver and related SAM9X60 support. The complete 61-line header was read for this report.

## Important APIs, Types, and Functions

The header defines control register `AT91_WDT_CR`, restart bit `AT91_WDT_WDRSTT`, and key `AT91_WDT_KEY`. It defines mode register `AT91_WDT_MR` and fields `AT91_WDT_WDV`, `AT91_WDT_SET_WDV()`, `AT91_WDT_WDFIEN`, `AT91_WDT_WDRSTEN`, `AT91_WDT_WDRPROC`, `AT91_WDT_WDDIS`, `AT91_WDT_WDD`, `AT91_WDT_SET_WDD()`, `AT91_WDT_WDDBGHLT`, and `AT91_WDT_WDIDLEHLT`. It also defines status register `AT91_WDT_SR` with underflow/error bits, plus SAM9X60-specific `AT91_SAM9X60_VR`, `AT91_SAM9X60_WLR`, period counter fields, and interrupt registers.

## Control Flow

No executable control flow exists. Consumers use these constants to read/write watchdog registers and construct mode values.

## State and Persistence Behavior

No storage is owned by the header. The constants describe hardware state fields that persist in MMIO registers, notably the mode register that may be write-once on AT91SAM9-class hardware.

## Dependencies and Integration Points

It includes `<linux/bits.h>` and integrates directly with `at91sam9_wdt.c`. The SAM9X60 definitions suggest shared hardware documentation for newer variants even though this source set only includes the SAM9x driver.

## Risks and Edge Cases

Incorrect bit definitions would cause irreversible watchdog mode programming mistakes. Several bits have variant-specific meanings, such as `AT91_WDT_WDFIEN` sharing bit position with `AT91_SAM9X60_WDDIS`, so users must apply the correct SoC variant semantics.

## Test Signals

Test signals are compile coverage with all AT91 watchdog users, hardware register programming review against datasheets, and runtime validation of restart, mode, status, and interrupt behavior on supported SoCs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/at91sam9_wdt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ath79_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/ath79_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/ath79_wdt.c` is a legacy miscdevice watchdog driver for Atheros AR71xx/AR724x/AR913x SoC watchdog hardware. It maps watchdog registers, derives maximum timeout from the watchdog clock, and exposes `/dev/watchdog` ioctls. The complete 322-line source was read for this report.

## Important APIs, Types, and Functions

Module parameters are `nowayout` and `timeout`. Global state includes `wdt_flags`, `wdt_clk`, `wdt_freq`, `boot_status`, `max_timeout`, and `wdt_base`. Hardware helpers are `ath79_wdt_wr()`, `ath79_wdt_rr()`, `ath79_wdt_keepalive()`, `ath79_wdt_enable()`, `ath79_wdt_disable()`, and `ath79_wdt_set_timeout()`. File operations are `ath79_wdt_open()`, `ath79_wdt_release()`, `ath79_wdt_write()`, and `ath79_wdt_ioctl()`. Platform lifecycle functions are `ath79_wdt_probe()`, `ath79_wdt_remove()`, and `ath79_wdt_shutdown()`.

## Control Flow

Probe maps registers, enables the `wdt` clock, computes timeout limits, clamps invalid module timeout to max, records boot status from the last-reset bit, and registers `/dev/watchdog`. Open sets busy state, clears magic-close expectation, and enables the hardware. Writes scan for `V` when nowayout is false and reload the timer. Ioctls return support/status/bootstatus, keepalive, and set/get timeout. Release disables only if magic close is set; otherwise it logs and refreshes. Shutdown disables the hardware.

## State and Persistence Behavior

Software state is global and singleton. Hardware state lives in the timer and control registers. Boot reset cause is latched in `boot_status` at probe from `WDOG_CTRL_LAST_RESET`.

## Dependencies and Integration Points

It depends on platform resources, OF compatible `qca,ar7130-wdt`, clock framework, MMIO, miscdevice, and watchdog ioctl ABI. Kconfig `ATH79_WDT` maps to `ath79_wdt.o`.

## Risks and Edge Cases

The driver is legacy and not watchdog-core based. Global state prevents multiple instances. Register writes are flushed by reads because hardware update ordering matters; removing flushes could break enable/disable. Enabling delays two microseconds to let the timer register update on AR934x.

## Test Signals

Test clock-rate zero, max-timeout calculation, bootstatus reporting, magic close, nowayout, timeout boundary handling, readback flush behavior, and shutdown disable.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/ath79_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bcm2835_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/bcm2835_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/bcm2835_wdt.c` is a watchdog-core driver for Broadcom BCM2835 power-management watchdog hardware used by Raspberry Pi-class systems. It also provides restart and a firmware-coordinated poweroff path using reset-status partition bits. The complete 247-line source was read for this report.

## Important APIs, Types, and Functions

`struct bcm2835_wdt` stores the PM base and spinlock. Important globals are singleton watchdog device `bcm2835_wdt_wdd` and optional `bcm2835_power_off_wdt`. Operations are `bcm2835_wdt_start()`, `bcm2835_wdt_stop()`, `bcm2835_wdt_get_timeleft()`, and `bcm2835_restart()`. Helper paths include `bcm2835_wdt_is_running()`, `__bcm2835_restart()`, `bcm2835_power_off()`, `bcm2835_wdt_probe()`, and `bcm2835_wdt_remove()`.

## Control Flow

Probe obtains PM state from the parent device, allocates driver state, initializes a spinlock, uses the parent PM base, initializes timeout/nowayout, marks `WDOG_HW_RUNNING` if the bootloader left full-reset watchdog enabled, sets restart priority, registers the watchdog, and optionally installs `pm_power_off` if the parent is the system power controller. Start writes password-protected timeout and reset-control bits under spinlock. Stop writes reset-control reset value. Restart sets a very short timeout and full-reset mode, then delays. Poweroff writes the Raspberry Pi halt partition marker into reset status before invoking restart.

## State and Persistence Behavior

Runtime state is mostly in watchdog core and password-protected PM registers. `pm_power_off` is a global kernel hook set on probe and cleared on remove if owned. The reset-status halt marker persists long enough for firmware to choose halt behavior after reset.

## Dependencies and Integration Points

It depends on the Broadcom PM MFD parent (`struct bcm2835_pm`), watchdog core, OF system-power-controller indication, global `pm_power_off`, MMIO access, and restart priority handling.

## Risks and Edge Cases

The singleton `bcm2835_wdt_wdd` assumes one hardware instance. Poweroff is implemented as reset plus firmware halt marker, so firmware interpretation is required. Stop uses a reset-control write rather than a separate disable bit. The `start()` timeout conversion is limited by a 20-bit watchdog field.

## Test Signals

Test boot-running detection, password-protected register writes, timeout conversion, restart, poweroff marker behavior, `pm_power_off` ownership cleanup, and watchdog core max-hardware-heartbeat handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bcm2835_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bcm47xx_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/bcm47xx_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/bcm47xx_wdt.c` is a watchdog-core wrapper for Broadcom BCM47xx platform watchdog operations supplied as platform data. It chooses direct hardware mode or a software extension timer when the hardware maximum interval is too short for requested timeouts. The complete 233-line source was read for this report.

## Important APIs, Types, and Functions

The driver consumes `struct bcm47xx_wdt` from platform data, which provides hardware callbacks such as `timer_set()` and `timer_set_ms()` plus fields like `max_timer_ms`, `soft_timer`, and `soft_ticks`. Hard-mode callbacks are `bcm47xx_wdt_hard_keepalive()`, `bcm47xx_wdt_hard_start()`, `bcm47xx_wdt_hard_stop()`, and `bcm47xx_wdt_hard_set_timeout()`. Soft-mode callbacks are `bcm47xx_wdt_soft_timer_tick()`, `bcm47xx_wdt_soft_keepalive()`, `bcm47xx_wdt_soft_start()`, `bcm47xx_wdt_soft_stop()`, and `bcm47xx_wdt_soft_set_timeout()`. Shared restart is `bcm47xx_wdt_restart()`, and probe is `bcm47xx_wdt_probe()`.

## Control Flow

Probe obtains platform data, selects soft mode if hardware max is below 60 seconds, installs the corresponding ops, validates module timeout, applies nowayout and restart priority, arranges stop-on-reboot, and registers the watchdog. Hard mode pings by programming the full timeout directly. Soft mode maintains `soft_ticks` in seconds and uses a kernel timer to refresh hardware each second until the software count expires; then it logs that hardware will fire soon. Restart programs a one-tick hardware timeout.

## State and Persistence Behavior

State is mostly owned by the platform-data structure supplied by lower BCM47xx code. Soft mode persists a countdown in `atomic_t soft_ticks` and a kernel timer. Hardware state is abstracted behind platform callbacks.

## Dependencies and Integration Points

It depends on `<linux/bcm47xx_wdt.h>` platform data, watchdog core, kernel timers, jiffies, and module parameters. Kconfig selects `WATCHDOG_CORE` for `BCM47XX_WDT`.

## Risks and Edge Cases

The driver is only as correct as platform-provided callbacks and `max_timer_ms`. Soft mode extends short hardware timeouts but depends on kernel scheduling each second. Timeout validation logs "using new_time" even while returning `-EINVAL`, which can be confusing. There is no OF discovery in this file; missing platform data returns `-ENXIO`.

## Test Signals

Test platform-data absence, hard/soft mode selection boundary, soft timer countdown and expiration, hardware callback invocation, restart programming, timeout validation, and stop-on-reboot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bcm47xx_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bcm7038_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/bcm7038_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/bcm7038_wdt.c` is a watchdog-core driver for Broadcom BCM63xx/BCM7038-style watchdog blocks. It programs timeout and command registers with required start/stop sequences and supports both OF and platform-device IDs. The complete 234-line source was read for this report.

## Important APIs, Types, and Functions

`struct bcm7038_watchdog` stores MMIO base, watchdog device, clock rate, and optional clock. Helper functions are `bcm7038_wdt_write()`, `bcm7038_wdt_read()`, `bcm7038_wdt_set_timeout_reg()`, and internal `bcm7038_wdt_ping()`. Watchdog operations wired into `watchdog_ops` are `bcm7038_wdt_start()`, `bcm7038_wdt_stop()`, `bcm7038_wdt_set_timeout()`, and `bcm7038_wdt_get_timeleft()`. Lifecycle and PM functions are `bcm7038_wdt_probe()`, `bcm7038_wdt_suspend()`, and `bcm7038_wdt_resume()`.

## Control Flow

Probe allocates state, maps registers, obtains an optional named clock from platform data, falls back to a 27 MHz default if no usable clock exists, initializes watchdog core limits, arranges stop-on-reboot/unregister, and registers the device. Start writes the timeout register and then pings with the two-word start sequence. Stop writes the two-word stop sequence. `set_timeout()` stops the watchdog, updates `wdd->timeout`, and restarts because hardware cannot modify timeout while running. Suspend stops active watchdogs; resume restarts active watchdogs.

## State and Persistence Behavior

Timeout state is stored in `wdd->timeout` and the hardware timeout register. Clock rate controls timeout conversion and max timeout. The hardware command register also reports time left. No persistent storage exists beyond active hardware registers.

## Dependencies and Integration Points

It depends on platform resources, optional `struct bcm7038_wdt_platform_data`, clock framework, OF compatibles `brcm,bcm6345-wdt` and `brcm,bcm7038-wdt`, platform id `bcm63xx-wdt`, MMIO, PM, and watchdog core.

## Risks and Edge Cases

Big-endian MIPS requires raw read/write access to match CPU-native peripheral byte order. If clock retrieval fails, the default rate may be wrong for a board, affecting timeout accuracy. Timeout changes stop and restart the watchdog, creating a transition window. The file declares a `nowayout` module parameter but never applies it with `watchdog_set_nowayout()`, so it appears ineffective in this version. The helper named `bcm7038_wdt_ping()` is used by start but is not exposed as the watchdog-core `.ping` callback.

## Test Signals

Test endian-specific register access, start/stop command sequences, clock fallback and zero-rate handling, timeout-change restart, get-timeleft conversion, suspend/resume active handling, and whether nowayout behavior matches expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bcm7038_wdt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bcm_kona_wdt.c -->
# sources/distributed-fs/ceph-client/drivers/watchdog/bcm_kona_wdt.c

## Purpose

`sources/distributed-fs/ceph-client/drivers/watchdog/bcm_kona_wdt.c` is a watchdog-core platform driver for Broadcom Kona secure watchdog hardware. It programs a secure watchdog control register with timeout, enable, reset-enable, and resolution fields, and optionally exposes debugfs diagnostics. The complete 339-line source was read for this report.

## Important APIs, Types, and Functions

`struct bcm_kona_wdt` stores MMIO base, resolution, spinlock, and optional debugfs state. Hardware helpers are `secure_register_read()`, `bcm_kona_wdt_ctrl_reg_modify()`, `bcm_kona_wdt_set_resolution_reg()`, and `bcm_kona_wdt_set_timeout_reg()`. Watchdog operations are `bcm_kona_wdt_set_timeout()`, `bcm_kona_wdt_get_timeleft()`, `bcm_kona_wdt_start()`, and `bcm_kona_wdt_stop()`. Debug helpers are `bcm_kona_show()`, `bcm_kona_wdt_debug_init()`, and `bcm_kona_wdt_debug_exit()`. Probe/remove functions are `bcm_kona_wdt_probe()` and `bcm_kona_wdt_remove()`.

## Control Flow

Probe allocates state, maps registers, sets default resolution, writes the resolution field, stores driver data, binds a singleton watchdog device to the instance, writes an initial timeout with the watchdog disabled, arranges stop-on-reboot/unregister, registers the watchdog, and creates debugfs if enabled. Start writes timeout plus enable and system-reset-enable bits. Stop clears enable and reset-enable bits. Set-timeout only updates the watchdog-core field; the new value is programmed on the next start. Get-timeleft reads the secure count register and converts ticks to seconds.

## State and Persistence Behavior

The resolution determines tick conversion and is programmed into hardware. The watchdog-core timeout is mirrored to hardware only through `bcm_kona_wdt_set_timeout_reg()`. `secure_register_read()` tracks debug busy count when debugfs is enabled. Hardware may temporarily set `SECWDOG_WD_LOAD_FLAG` while count fields are updating.

## Dependencies and Integration Points

It depends on OF compatible `brcm,kona-wdt`, platform MMIO resources, spinlocks, watchdog core, optional debugfs, and secure watchdog register semantics.

## Risks and Edge Cases

`secure_register_read()` can return `-ETIMEDOUT`; `bcm_kona_wdt_get_timeleft()` returns that negative value as an unsigned int, which can appear as a very large timeleft. The singleton `bcm_kona_wdt_wdd` assumes one instance. There is no nowayout module parameter. Set-timeout does not reprogram active hardware, so runtime timeout changes may not take effect until restart/start depending on watchdog core behavior.

## Test Signals

Test secure read timeout behavior, resolution programming, start/stop bit masking, active timeout changes, debugfs info output under `CONFIG_BCM_KONA_WDT_DEBUG`, singleton behavior, and stop-on-reboot/unregister cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/watchdog/bcm_kona_wdt.c -->
