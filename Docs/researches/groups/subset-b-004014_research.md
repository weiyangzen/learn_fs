# Research: subset-b-004014

Grouped research for Macintosh driver files under `sources/distributed-fs/ceph-client/drivers/macintosh`. Each section preserves the source path and is delimited for reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ans-lcd.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ans-lcd.c

Purpose: implements the `/dev/anslcd` misc driver for the front-panel LCD on Apple Network Server hardware. It probes for an Open Firmware node named `lcd` under parent `gc`, maps the fixed LCD MMIO window at `0xf301c000`, registers minor `LCD_MINOR`, initializes the controller, and writes an 80-character boot logo.

Important APIs and functions: `anslcd_write_byte_ctrl()` and `anslcd_write_byte_data()` write command/data bytes to offsets `ANSLCD_CTRL_IX` and `ANSLCD_DATA_IX` with controller-specific `udelay()` timing. `anslcd_write()` copies userspace bytes to the LCD data port and advances `*ppos`. `anslcd_ioctl()` implements `ANSLCD_CLEAR`, `ANSLCD_SENDCTRL`, `ANSLCD_SETSHORTDELAY`, and `ANSLCD_SETLONGDELAY`. `anslcd_fops` exposes `.write`, `.unlocked_ioctl`, `.open`, and `default_llseek`; `anslcd_init()` and `anslcd_exit()` own misc registration and `ioremap()` lifetime.

Control flow: module init verifies hardware via OF, maps MMIO, registers the misc device, then sends initialization commands and the logo under `anslcd_mutex`. Writes and ioctls serialize all controller access through the same mutex. Clear sends a fixed command sequence; send-control walks a NUL-terminated userspace command string.

State and persistence: global state is the MMIO pointer, short and long delay tunables, and the mutex. Delay changes persist only until module unload. No kernel-side display buffer is retained.

Dependencies and integration: depends on PowerPC OF discovery, `asm/io.h` 8-bit MMIO access, the misc-device subsystem, and ioctl constants from `ans-lcd.h`. Userspace ABI is `/dev/anslcd` plus private ioctls.

Risks: `ANSLCD_SENDCTRL` uses `__get_user()` without checking each fault result and relies on a userspace NUL terminator, so a bad pointer can produce partial/undefined command dispatch. Delay ioctls require `CAP_SYS_ADMIN` but accept unbounded values. The fixed physical address and ANS-specific OF check make this unsuitable for generic probing.

Test signals: on ANS hardware, expect `/dev/anslcd`, an initialized boot logo, correct clear/write behavior, and no oops on unload/reload. Negative tests should cover missing OF node, `misc_register()` failure, invalid ioctl numbers, non-admin delay writes, and userspace pointer faults.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ans-lcd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ans-lcd.h -->
# sources/distributed-fs/ceph-client/drivers/macintosh/ans-lcd.h

Purpose: provides the private ioctl command numbers used by the Apple Network Server LCD driver. It is intentionally small and only defines the ABI selectors consumed by `ans-lcd.c`.

Important APIs and types: defines `ANSLCD_CLEAR`, `ANSLCD_SENDCTRL`, `ANSLCD_SETSHORTDELAY`, and `ANSLCD_SETLONGDELAY` as integer command values `0x01` through `0x04`. The include guard is `_PPC_ANS_LCD_H`.

Control flow: none in this header. Consumers include it and switch on the constants in their file operation ioctl path.

State and persistence: no state. The constants are ABI-facing because userspace code can issue them to `/dev/anslcd`.

Dependencies and integration: integrated directly with `ans-lcd.c`. No kernel headers are included beyond the SPDX and guard.

Risks: these are not `_IO`, `_IOR`, or `_IOW` encoded ioctl numbers, so command typing, size validation, and namespace collision protection are absent. Changing any numeric value would break existing userspace tools for this device.

Test signals: build coverage should confirm the header is included by `ans-lcd.c`. ABI tests should verify each constant still triggers the expected behavior in the driver.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/ans-lcd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/apm_emu.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/apm_emu.c

Purpose: bridges PMU battery/AC state into the generic APM emulation layer on PMU-based PowerMac/PowerBook systems. It supplies `apm_get_power_status` so legacy APM userspace can read battery status even though the hardware is managed through the PMU driver.

Important APIs and functions: `pmu_apm_get_power_status()` fills `struct apm_power_info` from exported PMU globals: `pmu_power_flags`, `pmu_battery_count`, and `pmu_batteries[]`. `apm_emu_init()` installs the callback; `apm_emu_exit()` removes it if still installed.

Control flow: the callback initializes all fields to unknown/default values, reports AC online/offline from `PMU_PWR_AC_PRESENT`, aggregates present batteries, averages percentage by present battery count, sums charge and amperage, detects charging state, and computes approximate minutes remaining for discharging batteries. It maps percentage thresholds to critical, low, or high APM battery flags.

State and persistence: the module owns no persistent battery cache; all live state is read from PMU globals maintained by `via-pmu.c`. Its only persistent side effect is assigning the global APM callback pointer while loaded.

Dependencies and integration: depends on `linux/apm-emulation.h`, `linux/pmu.h`, and `linux/adb.h`. It assumes the PMU driver is present and updating battery records.

Risks: battery percentage divides by `max_charge`; malformed or zero PMU battery data would be hazardous. Time remaining uses legacy formulas that differ for smart and non-smart batteries and may be approximate. Concurrent reads of PMU globals are unsynchronized in this file.

Test signals: verify `/proc/apm` or equivalent APM consumers see AC status, charging, low, critical, and multi-battery average changes after PMU battery updates. Unload should clear `apm_get_power_status` only if no other provider replaced it.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/apm_emu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/mac_hid.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/mac_hid.c

Purpose: implements legacy Macintosh mouse button 2/3 emulation by converting configurable keyboard keycodes into middle/right mouse button input events. It exposes sysctls under `/proc/sys/dev/mac_hid`.

Important APIs and functions: `mac_hid_create_emumouse()` allocates/registers a synthetic `input_dev`; `mac_hid_emumouse_filter()` intercepts matching `EV_KEY` events and reports `BTN_MIDDLE` or `BTN_RIGHT`; `mac_hid_emumouse_connect()` attaches an `input_handle` to all key-capable devices except the synthetic device itself; `mac_hid_toggle_emumouse()` is the sysctl handler that starts/stops emulation atomically. `mac_hid_files` defines `mouse_button_emulation`, `mouse_button2_keycode`, and `mouse_button3_keycode`.

Control flow: module init registers the sysctl table. When userspace writes `1` to `mouse_button_emulation`, the driver creates the synthetic mouse and registers an input handler. The handler opens matching devices and filters configured keycodes into mouse events. Writing `0` unregisters the handler and synthetic device. Module exit unregisters sysctls and stops active emulation.

State and persistence: global sysctl-backed integers hold enable state and keycodes. Runtime state is `mac_hid_emumouse_dev`, protected by `mac_hid_emumouse_mutex` during enable/disable. Settings are not persistent across reboot.

Dependencies and integration: integrates with the input subsystem, sysctl/proc handlers, ADB bus identity for the synthetic device, and lockdep class annotation for the created device.

Risks: keycode sysctls can be changed while emulation is running without locking against event filtering. The filter consumes configured keys for all key-capable input devices. Error recovery in the toggle handler restores the old enable value, but partial input handler/device failures must remain paired.

Test signals: sysctl registration, enabling/disabling repeatedly, no self-binding loop, key-to-button event generation, invalid enable values returning `-EINVAL`, and module unload while enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/mac_hid.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/macio-adb.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/macio-adb.c

Purpose: provides an ADB controller driver for the Mac I/O Hydra ADB block. It implements the `struct adb_driver` operations used by the unified ADB core.

Important APIs and functions: `macio_probe()` detects OF compatible `chrp,adb0`; `macio_init()` maps controller registers, initializes active devices/autopoll, maps IRQ, and enables DFB/TAG interrupts. `macio_send_request()` queues ADB requests after stripping the leading `ADB_PACKET`. `macio_adb_interrupt()` handles transmit grants, replies, errors, and autopoll packets. `macio_adb_autopoll()`, `macio_adb_reset_bus()`, and `macio_adb_poll()` implement the remaining ADB driver callbacks.

Control flow: queued requests are protected by `macio_lock`. If idle, a new request asserts `TAR`; on `TAG`, the interrupt handler writes request bytes and either completes immediately or waits for `DFB`. On reply, it copies the controller data registers into `req->reply`, advances the queue, and calls the completion callback outside the lock. Unsolicited autopoll bytes are copied into a stack buffer and passed to `adb_input()`.

State and persistence: global controller MMIO pointer, current/last request queue, and spinlock. Autopoll device mask is held in hardware `active_hi/active_lo` registers. No persistent storage.

Dependencies and integration: relies on OF address/IRQ parsing, Hydra register layout, `linux/adb.h`, and the unified ADB core. Hardware access uses `in_8()`/`out_8()`.

Risks: synchronous requests spin in `macio_adb_poll()`. Request lifetime relies on callers keeping `struct adb_request` alive until completion. Error bits are cleared but not surfaced strongly to callers. Reset holds the spinlock with IRQs disabled for a long timeout loop.

Test signals: driver selection by ADB core, interrupt-driven and polled request completion, autopoll delivery to keyboards/mice, reset-bus behavior, IRQ request failure cleanup, and no queue corruption under multiple outstanding ADB requests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/macio-adb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/macio_asic.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/macio_asic.c

Purpose: implements the MacIO bus type and device enumeration/resource management for devices inside Apple MacIO ASICs. It adapts Open Firmware child nodes and PCI-attached MacIO chips into `struct macio_dev` devices with driver-model support.

Important APIs and functions: `macio_bus_type` provides match, uevent, probe/remove/shutdown/suspend/resume, and sysfs groups. Exported APIs include `macio_register_driver()`, `macio_unregister_driver()`, `macio_dev_get()`, `macio_dev_put()`, `macio_request_resource(s)()`, `macio_release_resource(s)()`, and `macio_enable_devres()`. Internal enumeration flows through `macio_pci_probe()`, `macio_pci_add_devices()`, and `macio_add_one_device()`.

Control flow: postcore init registers the bus; module init registers a broad Apple PCI driver. Probe filters real MacIO chips with `macio_find()`, handles two-ASIC ordering via `macio_on_hold`, then creates a root MacIO device, first-level children, media-bay children, and ESCC serial children. Each `macio_dev` receives OF node, DMA parameters, resources, interrupts, quirks, and a driver-model name before `of_device_register()`.

State and persistence: global state is the bus registration and optional held chip. Device state persists in allocated `macio_dev` objects until device release. Managed resource state is tracked with devres bitmasks.

Dependencies and integration: depends on PCI, OF address/IRQ helpers, `asm/macio.h`, `pmac_feature`, Linux device core, and sysfs attributes from `macio_sysfs.c`.

Risks: many resource quirks encode old device-tree bugs and are easy to regress. MacIO removal panics rather than hot-unplugging. The Gatwick IRQ fixup helper appears to populate IRQ resources only when `irq_create_mapping()` returns zero, so that path warrants careful validation. Media-bay dynamic behavior is only partly modeled.

Test signals: MacIO bus appears under sysfs, modalias uevents match OF IDs, child devices bind expected drivers, resource reservation/unwind works, media-bay and ESCC children are present, and old machines with Grand Central/OHare/Heathrow/KeyLargo/Gatwick retain expected resource shapes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/macio_asic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/macio_sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/macio_sysfs.c

Purpose: supplies default sysfs attribute groups for MacIO bus devices. The attributes expose OF identity needed by userspace matching, diagnostics, and modalias-based module loading.

Important APIs and functions: `compatible_show()` emits all NUL-separated strings from the OF `compatible` property as newline-separated text. `modalias_show()` calls `of_device_modalias()`. `devspec_show()` prints the OF full path with `%pOF`. `name_show()` prints `%pOFn`; `type_show()` prints `of_node_get_device_type()`. `macio_dev_groups` exports the attribute group consumed by `macio_bus_type`.

Control flow: the device core attaches `macio_dev_groups` to MacIO devices. Reads translate the `struct device` back to the OF/platform device and format current OF properties into the supplied sysfs buffer.

State and persistence: no mutable state. Output reflects device-tree properties attached to each MacIO device.

Dependencies and integration: depends on `asm/macio.h`, OF helpers, `DEVICE_ATTR_RO`, and `macio_asic.c`'s `extern const struct attribute_group *macio_dev_groups[]`.

Risks: `compatible_show()` updates `buf` by cumulative `length`, which can over-advance the pointer if multiple compatible strings exist; this path should be reviewed before modification. The functions assume `dev->of_node` is valid for all MacIO devices.

Test signals: sysfs files `name`, `type`, `compatible`, `modalias`, and `devspec` exist for MacIO devices; modalias strings trigger expected module autoload; multi-string compatible properties render correctly and within `PAGE_SIZE`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/macio_sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/mediabay.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/mediabay.c

Purpose: manages hot-swappable media bays on classic PowerBooks. It polls bay content, sequences power/reset/bus enable for floppy, ATA CD, PCI, and sound devices, and notifies MacIO child drivers when bay state changes.

Important APIs and functions: `struct media_bay_info` holds per-bay state; `struct mb_ops` abstracts Ohare, Heathrow, and KeyLargo register operations. Exported helpers are `check_media_bay()`, `lock_media_bay()`, and `unlock_media_bay()`. `media_bay_step()` is the state machine; `media_bay_task()` polls every `MB_POLL_DELAY`; `media_bay_attach()`, suspend, and resume are the MacIO driver callbacks.

Control flow: attach reserves MacIO resources, maps the ASIC register base, picks ops from OF match data, initializes hardware, forces an empty detect, then starts one polling kthread. The poller locks each bay, reads debounced content, powers up/down when stable content changes, steps through power-up, bus enable, reset release, optional IDE reset wait, and `mb_up`. Hotplug is modeled by calling child drivers' `mediabay_event()` callback.

State and persistence: static `media_bays[MAX_BAYS]`, `media_bay_count`, per-bay content/state/timers, cached GPIO, sleep flag, and user lock. State is runtime-only and reconstructed on boot/probe.

Dependencies and integration: depends on MacIO, PMac feature/register definitions for Ohare/Heathrow/KeyLargo, PMU/ADB headers, kthreads, and `asm/mediabay.h` content IDs.

Risks: global bay array has no explicit overflow guard if firmware exposes more than `MAX_BAYS`. Poll timing is hardware-sensitive. `check_media_bay()` intentionally returns unlocked fuzzy snapshots. The kthread handle is not stored for later stop in this file. Suspend/resume paths rely on content remaining unchanged.

Test signals: insertion/removal debouncing, state transitions with correct delays, ATA reset timing, child `mediabay_event()` callbacks, suspend/resume with unchanged and changed content, exported helper behavior under lock, and old-machine register programming for all three ops tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/mediabay.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/rack-meter.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/rack-meter.c

Purpose: drives the Xserve G5 front-panel CPU meter LEDs by streaming generated samples through I2S/DBDMA and updating LED bitmaps from CPU load measurements.

Important APIs and functions: `struct rackmeter` owns MacIO device, I2S/DBDMA mappings, coherent DMA buffers, sample buffer, IRQ, and per-CPU delayed work. `rackmeter_setup_i2s()` enables sound/I2S clocks; `rackmeter_setup_dbdma()` builds the four-command ring; `rackmeter_do_timer()` samples CPU idle time and updates 16 LED intensities; `rackmeter_irq()` refills the DMA buffer indicated by the DBDMA mark. Probe/remove/shutdown are MacIO callbacks.

Control flow: probe finds child `i2s-a` and a `lightshow` or virtual sound node, maps I2S and DBDMA resources, allocates sample and coherent DMA storage, initializes I2S, starts DMA, schedules per-CPU sampling, and requests the DMA IRQ. The IRQ alternates buffer refills. When both CPUs have zero load, delayed work pauses DMA; nonzero load restarts it.

State and persistence: runtime-only state includes DMA command ring, two sample buffers, LED byte buffer, delayed work per CPU, stale IRQ count, and pause flag. No userspace persistence.

Dependencies and integration: depends on MacIO, OF resources, KeyLargo feature bits, DBDMA, PCI DMA mapping via the MacIO parent PCI device, kernel CPU stats, and workqueues.

Risks: supports only CPU IDs 0 and 1 and does not handle CPU hotplug. It directly manipulates KeyLargo FCR/I2S state shared with sound drivers. IRQ is requested after DMA setup starts, so error unwind must stop DMA. Excess stale DMA marks reset the engine.

Test signals: Xserve G5 OF matching, visible LED activity under CPU load, DMA IRQs with marks 1/2, pause when idle, remove/shutdown stopping work and DMA, no interaction regression with sound/I2S, and SMP behavior with one or two online CPUs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/rack-meter.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/smu.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/smu.c

Purpose: implements the PowerMac G5 SMU system controller driver. It provides queued command transport, RTC/power operations, SMU-backed I2C commands, SMU SDB partition extraction, OF child exposure, and a `/dev/smu` misc userspace command interface.

Important APIs and functions: exported command APIs include `smu_queue_cmd()`, `smu_queue_simple()`, `smu_poll()`, `smu_done_complete()`, `smu_spinwait_cmd()`, `smu_present()`, `smu_get_sdb_partition()`, and `smu_get_ofdev()`. Power/RTC helpers are `smu_get_rtc_time()`, `smu_set_rtc_time()`, `smu_shutdown()`, and `smu_restart()`. Low-level transport uses `smu_start_cmd()` and `smu_db_intr()`. I2C support centers on `smu_queue_i2c()`, `smu_i2c_low_completion()`, and retry timer logic. File operations implement `/dev/smu`.

Control flow: early init locates the `smu` node, allocates a low-2GB command buffer via memblock, finds doorbell/message GPIO nodes, maps a doorbell pointer buffer, and marks SMU as system controller. Core init maps/requests IRQs and sets up the I2C retry timer. Commands are queued under `smu->lock`; `smu_start_cmd()` copies data to the shared buffer, flushes cache, writes the physical address, and rings the doorbell. Completion IRQ validates ack, copies replies, updates status, starts the next command, then invokes callbacks outside the lock.

State and persistence: single global `smu_device`, command queue/current command, I2C queue/current command, retry timer, OF platform device, SDB partition properties cached onto the SMU OF node, and per-open `/dev/smu` state.

Dependencies and integration: depends on PMac feature GPIO calls, OF/platform devices, memblock, cache flushes, miscdevice, completions, timers, wait queues, and `asm/smu.h`.

Risks: no general command timeout is implemented. Command buffer cache coherency and low-memory address assumptions are hardware-critical. I2C retry code is complex and queue manipulation should be reviewed carefully. `/dev/smu` exposes raw commands to userspace; event mode is stubbed. SDB partition reads add OF properties dynamically.

Test signals: boot on SMU G5, command completion by IRQ and early poll fallback, RTC get/set, shutdown/restart command issue, SMU I2C read/write retries, SDB partition property creation, `/dev/smu` blocking/nonblocking reads, poll readiness, and child `smu-sensors` platform device creation without device-model deadlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/smu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/therm_adt746x.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/therm_adt746x.c

Purpose: controls ADT7460/ADT7467 thermal chips in iBook G4 and aluminum PowerBook G4 systems. It reads sensors, sets thermal limits, manages fan speed manually or automatically, and exposes legacy temperature attributes.

Important APIs and functions: `struct thermostat` stores I2C client, cached temperatures/limits, fan state, chip type, kthread, and legacy platform device. `read_reg()`/`write_reg()` implement byte I2C register access. `write_fan_speed()` and `write_both_fan_speed()` program manual or automatic fan modes. `monitor_task()` periodically reads sensors and calls `update_fans_speed()`. `thermostat_create_files()` creates old ABI sysfs attributes on a generated platform device. Probe/remove are I2C driver callbacks.

Control flow: module init optionally loads `i2c-powermac` and registers an I2C driver. Probe requires OF sensor parameter version 1, reads locations, determines chip type, reads config, sets default fan speed if unset, initializes ADT7460 if needed, lowers chip limits while storing originals, records PWM invert bits, starts fans or automatic mode, launches `kfand`, and creates sysfs files. Remove deletes files, stops the thread, restores original limits, returns fans to automatic mode, and frees state.

State and persistence: module parameters `limit_adjust`, `fan_speed`, and `verbose`; global sensor location strings; per-device thermostat state. Settings persist while module is loaded.

Dependencies and integration: depends on I2C, OF sensor properties, platform device creation for old ABI paths, freezer-aware kthread handling, and Apple thermal device-tree conventions.

Risks: global `fan_speed` and locations are shared across devices. I2C helper return values are not always checked by callers. Thermal policy is empirical and hardware-specific. Sysfs store paths use `simple_strtol()` and update global limits/fan speed without a thermostat-wide lock.

Test signals: probe on ADT7460 and ADT7467 nodes, sysfs attribute presence and values, fan speed transitions around limits with hysteresis, suspend/freezer behavior, removal restoring limits/automatic fans, module parameter effects, and I2C error handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/therm_adt746x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/therm_windtunnel.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/therm_windtunnel.c

Purpose: controls the fan in PowerMac3,6 "windtunnel" G4 systems using a DS1775 CPU thermostat and ADM1030 fan controller. The policy is tuned from observed Mac OS X behavior.

Important APIs and functions: global `x` stores clients, platform device, current temperatures, fan table indices, saved fan registers, and lock. `read_reg()`/`write_reg()` perform I2C register access. `setup_hardware()` saves registers, configures the thermostat/fan controller, lowers overheat thresholds if at defaults, and creates temperature sysfs files. `poll_temp()` reads CPU/case temperature and chooses fan settings from `fan_table`; `control_loop()` runs this every 8 seconds. I2C callbacks are `do_probe()` and `do_remove()`; platform callbacks are `therm_of_probe()`/`therm_of_remove()`.

Control flow: module init verifies `power-mgt` thermal-info design ID 3 and machine compatibility, creates a platform device for the fan OF node, and registers a platform driver. Probe waits for I2C adapter 0, registers the I2C driver, scans consecutive Uni-N I2C adapters for missing DS1775/ADM1030 nodes, and starts `g4fand` once both clients attach. The thread sets up hardware, repeatedly polls, and restores registers on stop.

State and persistence: all runtime state is in global `x`. Original ADM1030 registers are restored when the thread exits. No persistent configuration is stored.

Dependencies and integration: depends on OF machine identification, I2C scanning/driver APIs, platform device creation, sysfs device files, and PowerMac MacIO/I2C topology.

Risks: single global state means only one supported thermal design. Device scanning assumes consecutive Mac I2C bus numbers starting at 0. Thermal thresholds are empirical and narrow to tested hardware. `therm_of_probe()` can return after starting without putting the current adapter reference. Register restore depends on orderly remove.

Test signals: PowerMac3,6 detection, DS1775/ADM1030 attachment by OF or scan, `g4fand` lifecycle, sysfs CPU/case temperatures, fan level changes across table thresholds, overheat threshold lowering, and register restoration on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/therm_windtunnel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-cuda.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/via-cuda.c

Purpose: implements Cuda/Egret system controller transport over a 6522 VIA. These microcontrollers provide power/PRAM/RTC and ADB services on PowerMac and 68k Mac systems.

Important APIs and functions: `find_via_cuda()` locates/maps hardware and synchronizes the MCU. `via_cuda_driver` implements ADB callbacks through `cuda_probe()`, `cuda_send_request()`, `cuda_adb_autopoll()`, `cuda_reset_adb_bus()`, and `cuda_poll()`. `cuda_request()` is exported for CUDA packet users. `cuda_interrupt()` is the core state machine; `cuda_input()` dispatches unsolicited packets. RTC helpers are `cuda_get_time()` and `cuda_set_rtc_time()`.

Control flow: initialization maps VIA registers, configures the shift register, performs Cuda or Egret-specific sync, enables autopoll, then requests the IRQ at device init. Requests are queued under `cuda_lock`; `cuda_start()` begins output if no incoming byte is pending. The interrupt state machine handles collisions, byte sends, awaited replies, unsolicited reads, Egret quirks without final interrupts, queue advancement, and callback execution outside the lock.

State and persistence: global VIA pointer, queue pointers, `cuda_state`, reply buffer, current reply pointer, index flags, IRQ, OF node, and fully-inited flag. RTC persists in hardware; driver state does not.

Dependencies and integration: depends on PPC OF or m68k Macintosh config, VIA register layout, unified ADB, CUDA packet definitions, IRQ handling, XMON optional keyboard interception, and RTC conversion offset from 1904 to 1970.

Risks: protocol correctness is timing-sensitive and differs for Egret active levels/delays. Synchronous calls busy-poll. Reply buffers are bounded to 16 bytes with overflow discard. Request lifetime assumptions mirror ADB core expectations. Collision handling and lock break before `cuda_input()` are reentrancy-sensitive.

Test signals: Cuda and Egret detection, sync completion, ADB keyboard/mouse autopoll, CUDA request/reply, RTC get/set, unsolicited packet logging, IRQ and polling paths, collision recovery, and behavior on both PPC and m68k builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-cuda.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-macii.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/via-macii.c

Purpose: implements Mac II style ADB transport over VIA shift-register signaling for many m68k Mac II-class machines.

Important APIs and functions: `via_macii_driver` supplies unified ADB callbacks: `macii_probe()`, `macii_init()`, `macii_send_request()`, `macii_autopoll()`, `macii_poll()`, and `macii_reset_bus()`. `macii_start()` begins a transaction; `macii_interrupt()` is the byte-level ADB state machine; `macii_queue_poll()` prepends autopoll Talk Register 0 commands.

Control flow: probe selects machines with `MAC_ADB_II`. Init configures VIA direction/state and requests `IRQ_MAC_ADB`. Requests must be `ADB_PACKET` and are queued with interrupts disabled. The interrupt handler toggles VIA ADB state bits through command/even/odd phases, sends bytes, reads replies or unsolicited autopoll data, detects bus timeout and SRQ, completes current requests, and queues new autopolls when idle.

State and persistence: global VIA pointer, queue pointers, `macii_state`, reply buffer/pointer, reply length, status flags, last command/talk/poll commands, and autopoll device bitmask. No persistent storage.

Dependencies and integration: m68k Macintosh configuration, VIA registers from `asm/mac_via.h`, Mac interrupt numbers, unified ADB helpers/macros, and `adb_input()`.

Risks: it relies on precise VIA state-bit transitions and transceiver behavior. Autopoll assumes unprobed devices do not assert SRQ. Static poll request reuse is safe only because it is queued in a controlled idle path. Buffer length is limited to 16 bytes. Local IRQ disabling serializes queue/state but makes long protocol handling latency-sensitive.

Test signals: Mac II ADB detection, request completion with and without replies, bus reset low-time delay, autopoll device rotation, SRQ handling, timeout behavior, keyboard/mouse input delivery, and no corruption when a command collides with buffered autopoll data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-macii.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-backlight.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-backlight.c

Purpose: registers a platform backlight device that controls PowerBook/iBook display brightness through PMU commands.

Important APIs and functions: `pmu_backlight_init_curve()` builds a firmware brightness curve; `pmu_backlight_curve_lookup()` maps autosaved PMU values back to framebuffer levels; `pmu_backlight_get_level_brightness()` converts framebuffer backlight levels to PMU values. `pmu_backlight_update_status()` serializes updates and calls `__pmu_backlight_update_status()` to issue `PMU_BACKLIGHT_BRIGHT` and `PMU_POWER_CTRL` commands. `pmu_backlight_set_sleep()` suppresses updates during suspend. `pmu_backlight_init()` registers the backlight device.

Control flow: init checks supported machine/backlight types, registers `pmubl`, initializes the curve, optionally reads an autosaved brightness on older PowerBooks, sets max brightness as default, marks power on, and updates hardware. Runtime backlight changes call into PMU synchronously unless sleeping.

State and persistence: globals include `sleeping`, `uses_pmu_bl`, the PMU conversion curve, and a spinlock. Hardware brightness/power state persists in the PMU/display hardware; kernel state is rebuilt at boot.

Dependencies and integration: depends on PMU request APIs from `via-pmu.c`, generic backlight framework, PMac backlight globals/helpers, OF machine matching, and suspend hooks.

Risks: PMU requests are sent while holding `pmu_backlight_lock`, so interactions with PMU completion paths must remain non-recursive. Brightness curve constants are hardware-specific. Autosave command `0xd9` is magic and old-model-specific.

Test signals: backlight device registration only on supported machines, brightness level scaling, off/on power commands at zero/nonzero brightness, autosaved level restore on 3400/2400/3500 models, suspend turning backlight off, and resume restoring prior brightness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-backlight.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-event.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-event.c

Purpose: exposes selected PMU environment events as Linux input events. It currently reports power-button and lid-switch state for KeyLargo-based PMU models.

Important APIs and functions: `via_pmu_event_init()` allocates and registers an `input_dev` named `PMU` with `EV_KEY`, `EV_SW`, `KEY_POWER`, and `SW_LID` capabilities. `via_pmu_event()` is the callable bridge from the PMU interrupt handler; it maps `PMU_EVT_POWER` and `PMU_EVT_LID` to input reports and syncs the device.

Control flow: late init exits unless `pmu_get_model()` reports `PMU_KEYLARGO_BASED`. After registration, `via-pmu.c` calls `via_pmu_event()` from PMU environment interrupt handling when it sees the expected packet length.

State and persistence: one global `pmu_input_dev` pointer. No event queue beyond the input subsystem.

Dependencies and integration: depends on PMU model detection, `linux/input.h`, and constants from `via-pmu-event.h`. Integrated by direct call from `via-pmu.c`.

Risks: no module exit/unregister path is present because it is built as late init platform support. Event support is limited to models known to report these bits. Calls before input device registration are ignored.

Test signals: input device appears on KeyLargo PMU systems, power button emits `KEY_POWER`, lid changes emit `SW_LID`, unsupported PMU models return `-ENODEV`, and malformed/unrecognized event IDs are ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-event.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-event.h -->
# sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-event.h

Purpose: declares the tiny internal interface between the PMU interrupt driver and the PMU input-event bridge.

Important APIs and types: defines event IDs `PMU_EVT_POWER` and `PMU_EVT_LID`, and declares `extern void via_pmu_event(int key, int down);`.

Control flow: none. `via-pmu.c` includes this header and calls `via_pmu_event()` when decoding environment interrupt packets; `via-pmu-event.c` implements it.

State and persistence: no state. Event numbers are internal to this driver pair.

Dependencies and integration: guarded by `__VIA_PMU_EVENT_H`; no external headers required.

Risks: adding event IDs requires updating both the producer decode logic and the consumer switch. If `CONFIG_ADB_PMU_EVENT` is not enabled, call sites must be guarded as they are in `via-pmu.c`.

Test signals: compile coverage with and without PMU event input support, and runtime verification that the two defined IDs map to `KEY_POWER` and `SW_LID`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-event.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-led.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-led.c

Purpose: registers a LED class device for the PMU-controlled front LED on supported KeyLargo-based PowerBook, iBook, and PowerMac G5 systems.

Important APIs and functions: `pmu_led_set()` accepts `LED_OFF` or `LED_FULL`, coalesces desired state in `requested_change`, and sends PMU command `0xee` when no previous blink request is active. `pmu_req_done()` sends a deferred last requested change after asynchronous PMU completion. `via_pmu_led_init()` filters supported models and registers `pmu-led::front`.

Control flow: late init checks PMU model and root OF `model`, initializes the lock and request state, and registers the LED. Brightness changes update `requested_change` under `pmu_blink_lock`; if the previous request is complete and the system is not suspended, a PMU request is issued. Completion callback drains one deferred state.

State and persistence: `pmu_blink_req` is a reusable global `adb_request`; `requested_change` stores no-change/off/on; `pmu_blink_lock` serializes access. LED state is not persisted by the driver.

Dependencies and integration: depends on LED class framework, PMU request API, `pmu_sys_suspended` from `via-pmu.c`, OF model strings, and optional disk-activity trigger.

Risks: only full/off brightness is supported; intermediate brightness is ignored. Request coalescing keeps only the most recent pending state. The callback can issue another PMU request while holding the LED lock, so PMU callback behavior must remain compatible.

Test signals: LED device registration on allowed models only, disk trigger default when configured, full/off PMU command emission, coalesced rapid brightness changes, no command while suspended, and deferred update after request completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu-led.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu.c

Purpose: implements the PMU system controller driver for Apple PowerBooks and some PowerMacs. The PMU controls power, battery charging, ADB, NVRAM/RTC, brightness-related events, sleep/wake, and user-visible `/dev/pmu` plus `/proc/pmu` interfaces.

Important APIs and functions: exported APIs include `pmu_request()`, `pmu_queue_request()`, `pmu_poll()`, `pmu_poll_adb()`, `pmu_wait_complete()`, `pmu_suspend()`, `pmu_resume()`, `pmu_unlock()`, and on PPC32 battery/IR LED exports. ADB integration is `via_pmu_driver` with `pmu_send_request()`, `pmu_adb_autopoll()`, and `pmu_adb_reset_bus()`. Core transport is `pmu_start()`, `pmu_sr_intr()`, and `via_pmu_interrupt()`. Power/RTC helpers are `pmu_get_time()`, `pmu_set_rtc_time()`, `pmu_restart()`, and `pmu_shutdown()`.

Control flow: `find_via_pmu()` locates and maps VIA/optional GPIO registers, determines PMU kind, initializes interrupt masks, and calls `init_pmu()`. `via_pmu_start()` requests VIA/GPIO IRQs early and drains pending PMU work. Requests are validated against `pmu_data_len`, queued under `pmu_lock`, and byte-framed through VIA shift-register handshakes. `via_pmu_interrupt()` handles SR and CB1/GPIO events, completes normal requests outside the lock, acknowledges PMU interrupt packets into two buffers, then decodes ADB, tick, environment, brightness, and battery events.

State and persistence: global PMU state machine, current/last request queue, awaiting ADB reply, interrupt buffers, IRQ stats, battery cache, PMU model/version, proc entries, sleep flags, server/lid wake options, and `/dev/pmu` per-open ring buffers. RTC, server mode, wake events, and power actions affect hardware persistence.

Dependencies and integration: tightly integrated with unified ADB, PMac feature calls, OF/IRQ mapping, GPIO, procfs, miscdevice, suspend/syscore, PMac backlight, input PMU events, low-level sleep assembly, PCI/cache/MMU helpers, and battery/APM consumers.

Risks: this is timing-sensitive VIA protocol code with shared interrupt and polling paths. Many globals are protected only by `pmu_lock` or local IRQ disabling, and request structures must outlive completion. `/dev/pmu` is an old ABI with a small interrupt ring. Sleep paths are hardware-specific and manipulate cache, MMU, ASIC power, IRQs, and PMU locks. `pmu_data_len` must match firmware command framing exactly.

Test signals: PMU detection across Ohare/Heathrow/Paddington/KeyLargo and m68k PB2, ADB keyboard/mouse via PMU, request queue completion, PMU interrupt stats, battery proc updates, RTC get/set, `/dev/pmu` read/poll/ioctl and compat ioctl, backlight and PMU event integration, server-mode proc option, restart/shutdown commands, suspend/resume on supported PPC32 systems, and no interrupt-loop stalls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/via-pmu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm.h -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm.h

Purpose: defines the shared Windfarm thermal-control API for PowerMac fan controls, sensors, clients, and overtemperature notifications.

Important APIs and types: `struct wf_control_ops` and `struct wf_control` describe controllable devices with set/get/min/max/release operations, kref lifetime, sysfs attribute, type, and private data. `struct wf_sensor_ops` and `struct wf_sensor` describe readable sensors. Inline helpers wrap control set/get min/max and sensor get. External APIs register/unregister/get/put controls and sensors, register/unregister notifier clients, and set/clear refcounted overtemperature.

Control flow: provider drivers allocate/populate `wf_control` or `wf_sensor`, register them with the Windfarm core, and rely on kref release callbacks after unregister. Client drivers register notifier blocks and react to events such as new sensors/controls and ticks.

State and persistence: no state in the header, but it defines lifetime ownership rules. Registered objects persist until the provider unregisters and final references drop.

Dependencies and integration: depends on Linux list, kref, module, notifier, and device attribute APIs. Used by Windfarm sensor/control providers such as `windfarm_ad7417_sensor.c` and policy clients elsewhere in the Macintosh tree.

Risks: notifier callbacks for all events except `WF_EVENT_TICK` run with an internal mutex held, and the header warns clients not to call core routines from those callbacks. Notifier blocks have no module owner, creating potential lifetime races. Fixed 16.16 formatting macro assumes signed 32-bit values.

Test signals: provider registration/unregistration lifetime, kref balancing through get/put, sysfs attribute creation by the core, notifier delivery ordering, overtemp refcount behavior, and client behavior that defers work from mutex-held callbacks to tick/work context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_ad7417_sensor.c -->
# sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_ad7417_sensor.c

Purpose: registers Windfarm sensors for AD7417 chips on supported PowerMac7,2, PowerMac7,3, and RackMac3,1 systems. It exposes ambient CPU temperature and ADC-derived diode, voltage, and current readings to Windfarm policy code.

Important APIs and functions: `struct wf_ad7417_priv` holds kref, I2C client, cached config, CPU number, MPU calibration data, five `wf_sensor` objects, and a mutex. `wf_ad7417_temp_get()` reads register 0 and converts 8.8 temperature to 16.16 fixed point. `wf_ad7417_adc_get()` selects ADC channels, waits for conversion, reads register 4, converts raw values via `wf_ad7417_adc_convert()`, and retries I2C failures. `wf_ad7417_add_sensor()` registers each Windfarm sensor and bumps the private kref on success. Probe/remove are I2C callbacks.

Control flow: module init restricts registration to known machines. Probe requires `hwsensor-location`, maps `CPU A`/`CPU B` to CPU number, retrieves MPU calibration with `wf_get_mpu()`, allocates state, initializes the AD7417 config registers, then registers five hard-coded sensor names suffixed by CPU number. Remove clears the client pointer, unregisters sensors, and drops the base kref.

State and persistence: per-chip private state plus registered Windfarm sensor objects. Sensor names are dynamically allocated and freed by release callbacks. Hardware config is cached in `pv->config`.

Dependencies and integration: depends on I2C, OF properties, Windfarm core, `windfarm_mpu.h` calibration data, and PowerMac machine matching.

Risks: endian casts use `be16_to_cpup((__le16 *)buf)`, which is unusual and should be handled carefully if refactored. `pv->i2c` is set to NULL on remove while outstanding sensor references may still exist; read paths assume valid client. Sensor registration failures are tolerated individually, so policy may see partial sensor sets.

Test signals: module loads only on supported machines, CPU A/B location parsing, MPU calibration availability, five sensors per chip with expected names, temperature/ADC fixed-point values, retry behavior on I2C errors, and clean kref/name release after unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/macintosh/windfarm_ad7417_sensor.c -->
