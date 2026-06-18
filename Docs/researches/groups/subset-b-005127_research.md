# subset-b-005127 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mips/cpu_hwmon.c -->
# sources/distributed-fs/ceph-client/drivers/platform/mips/cpu_hwmon.c

Purpose: Loongson-3 CPU hardware-monitor driver exposing per-package CPU temperature through hwmon sysfs and enforcing an emergency thermal poweroff threshold. It supports both newer CSR temperature access and older Loongson chip-temperature registers, translating raw sensor values by PRID revision.

Important APIs, types, and functions: `loongson3_cpu_temp()` is the primary exported-in-file helper and returns millidegrees Celsius for a package index. `SENSOR_DEVICE_ATTR(tempN_input/tempN_label)` defines up to four hwmon channels. `cpu_hwmon_is_visible()` hides channels beyond `nr_packages`. `loongson_hwmon_init()` detects CSR temperature support, computes package count from `loongson_sysconf`, registers `cpu_hwmon` with `hwmon_device_register_with_groups()`, and schedules `thermal_work`. `do_thermal_timer()` polls every 5 seconds and calls `orderly_poweroff(true)` when a package exceeds `CPU_THERMAL_THRESHOLD` of 90000 millidegrees.

Control flow: module init checks `cpu_has_csr()` and `LOONGSON_CSRF_TEMP`; if neither CSR nor legacy `loongson_chiptemp[0]` is available it returns `-ENODEV`. Sysfs reads call `get_cpu_temp()`, which maps the hwmon attribute index to package id and delegates to `loongson3_cpu_temp()`. The delayed work starts after 20 seconds and reschedules itself after each scan. Module exit synchronously cancels the delayed work and unregisters the hwmon device.

State and persistence: state is in static globals: `csr_temp_enable`, `nr_packages`, `cpu_hwmon_dev`, and the delayed work item. No persistent storage is used. Runtime state is visible through hwmon sysfs files, and thermal enforcement is timer-driven.

Dependencies and integration points: depends on Loongson MIPS platform headers (`loongson.h`, `boot_param.h`, `loongson_hwmon.h`, `loongson_regs.h`), MIPS PRID revision constants, Linux hwmon, workqueues, and reboot/poweroff infrastructure. Integration points are `/sys/class/hwmon` channel files and kernel orderly poweroff.

Risks: package count divides by `loongson_sysconf.cores_per_package`, so invalid platform configuration can break initialization. The driver assumes at most four packages because only four channel pairs are declared. Temperature conversion is revision-specific and can misreport if PRID mappings are incomplete. Thermal shutdown is abrupt and unconditional once a single read exceeds threshold; transient or faulty sensor values can power off the system. `loongson3_cpu_temp()` can be called with package ids derived from sysfs visibility, but any external caller would need to pass a valid id.

Test signals: build with Loongson platform config and hwmon enabled; boot on a system with CSR temperature and one with legacy chiptemp. Verify sysfs `temp*_input` and `temp*_label` count matches packages, values are plausible in millidegrees, and hidden channels do not appear. Use fault injection or mocked register reads to exercise the 90 C poweroff branch and delayed-work cancellation on module removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mips/cpu_hwmon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mips/ls2k-reset.c -->
# sources/distributed-fs/ceph-client/drivers/platform/mips/ls2k-reset.c

Purpose: Early Loongson-2K1000 reset and poweroff support. It maps the platform PM register block from device tree and installs machine restart and power-off hooks.

Important APIs, types, and functions: `ls2k_restart()` writes `0x1` to `RST_CNT`; `ls2k_poweroff()` clears PM status then writes sleep type and sleep enable bits to `PM1_CNT`; `ls2k_reset_init()` finds the `loongson,ls2k-pm` node, maps its first resource with `of_iomap()`, assigns `_machine_restart` and `pm_power_off`, and is registered with `arch_initcall()`.

Control flow: during arch init, the driver locates the PM node. Missing node yields `-ENODEV`; mapping failure yields `-ENOMEM`. On success, future restart/poweroff flows enter the static callbacks and directly program the PM registers.

State and persistence: only static `base` persists for the mapped PM register region. No cleanup path is present because the code is built as early platform support. Hardware register writes are one-shot and do not persist beyond platform power state.

Dependencies and integration points: depends on Open Firmware address mapping, `asm/reboot.h` for `_machine_restart`, and Linux PM global `pm_power_off`. It integrates through device-tree compatible `loongson,ls2k-pm`.

Risks: hooks are installed globally and overwrite any prior restart/poweroff implementation without arbitration. There is no unmap or owner tracking, appropriate for arch init but risky if platform probing order changes. `ls2k_poweroff()` writes a broad status clear and sleep control value, so register definitions must match the exact SoC.

Test signals: boot with a DT node for `loongson,ls2k-pm`, confirm mapping succeeds, and test `reboot` and `poweroff` on LS2K hardware or an emulator with observable PM writes. Negative tests should omit the node and verify no hooks are installed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mips/ls2k-reset.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mips/rs780e-acpi.c -->
# sources/distributed-fs/ceph-client/drivers/platform/mips/rs780e-acpi.c

Purpose: RS780E southbridge ACPI I/O setup for Loongson systems. The driver programs PM index/data ports and ACPI I/O decode registers so SCI, GPE, and power-management blocks are available at the platform-provided I/O resource.

Important APIs, types, and functions: `pmio_write_index()` and `pmio_read_index()` implement indexed PM register access through `PM_INDEX/PM_DATA`; `pm2_iowrite()` and `pm2_ioread()` target the second index pair. `acpi_registers_setup()` writes PM status/control/GPE base registers, enables ACPI decode and SCI generation, configures GPM3/GPM9, and pull-downs. `acpi_hw_clear_status()` clears wake/power button and GPE status. `rs780e_acpi_probe()` requests the I/O resource and invokes setup. The driver is a builtin platform driver matched by `loongson,rs780e-acpi`.

Control flow: platform probe obtains `IORESOURCE_IO`, reserves it with `request_region()`, stores `acpi_iobase`, programs the southbridge, and clears pending hardware status. There is no remove path; setup is expected to be permanent for the booted system.

State and persistence: `acpi_iobase` is static and all meaningful state is in the chipset registers. No Linux-managed persistent data structure is retained after probe except the reserved I/O region.

Dependencies and integration points: uses x86-style I/O port access (`inb/outb/inw/outw/inl/outl`) on a MIPS platform, platform-device resources, and OF compatible matching. It integrates with ACPI/SCI electrical behavior rather than registering a Linux ACPI core object itself.

Risks: hard-coded PM register indices and bit positions make this tightly bound to RS780E wiring. `request_region()` has no matching release because there is no remove path. SCI/GPE configuration can break wake or power-button behavior if the I/O resource or GPM wiring is wrong. The code assumes 16-bit ACPI base programming is sufficient.

Test signals: boot with a `loongson,rs780e-acpi` platform device and verify I/O region reservation, SCI delivery, power-button status clearing, and GPE events. Use register tracing or hardware diagnostics to confirm PM index writes and GPM pull-down configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/mips/rs780e-acpi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/olpc/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/olpc/Kconfig

Purpose: Kconfig definitions for OLPC embedded-controller platform support, especially the ARM-based XO-1.75 family.

Important APIs, types, and functions: `config OLPC_EC` is an internal boolean selecting `REGULATOR`; `menuconfig OLPC_XO175` exposes platform support for `ARCH_MMP` or `COMPILE_TEST`; `config OLPC_XO175_EC` builds the SPI slave EC driver and depends on `SPI_SLAVE`, `INPUT`, and `POWER_SUPPLY`, while selecting `OLPC_EC`.

Control flow: this file is evaluated by Kconfig. Enabling `OLPC_XO175_EC` selects the generic OLPC EC layer and makes both `olpc-ec.o` and `olpc-xo175-ec.o` available through the Makefile.

State and persistence: configuration state is persisted in the kernel `.config`. No runtime state is declared here.

Dependencies and integration points: ties platform support to ARM MMP or compile testing, SPI target/slave support, input power-button reporting, power-supply notifications, and the regulator framework via the generic EC layer.

Risks: `OLPC_EC` is a bool selected by `OLPC_XO175_EC`; if other OLPC EC transports need it, dependencies must ensure the generic object is built in a compatible link mode. Missing `SPI_SLAVE`, `INPUT`, or `POWER_SUPPLY` prevents the XO-1.75 EC driver from appearing.

Test signals: run `make olddefconfig`/`menuconfig` combinations for `ARCH_MMP`, `COMPILE_TEST`, built-in and module variants of `OLPC_XO175_EC`, and verify selected objects and dependencies are consistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/olpc/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/olpc/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/olpc/Makefile

Purpose: Build mapping for OLPC platform drivers.

Important APIs, types, and functions: `obj-$(CONFIG_OLPC_EC) += olpc-ec.o` builds the generic EC command/regulator/debugfs layer; `obj-$(CONFIG_OLPC_XO175_EC) += olpc-xo175-ec.o` builds the XO-1.75 SPI transport and platform integration.

Control flow: kbuild includes each object according to Kconfig symbols. Since `OLPC_XO175_EC` selects `OLPC_EC`, the transport normally links with the generic EC service.

State and persistence: no runtime state; build state follows `.config`.

Dependencies and integration points: integrates Kconfig symbols with kbuild and the broader `drivers/platform` build.

Risks: module/built-in combinations must leave the generic EC layer available before the transport registers the platform device. If future transports select `OLPC_EC`, object ordering and symbol export assumptions should be reviewed.

Test signals: inspect `make V=1 drivers/platform/olpc/` for expected object inclusion under `CONFIG_OLPC_EC=y/m` and `CONFIG_OLPC_XO175_EC=y/m`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/olpc/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/olpc/olpc-ec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/olpc/olpc-ec.c

Purpose: Generic OLPC embedded-controller service layer. It serializes EC commands through a platform-provided transport driver, exports common OLPC EC APIs, provides wake mask helpers, exposes an optional debugfs command endpoint, and registers a DCON regulator controlled by EC command.

Important APIs, types, and functions: `struct ec_cmd_desc` represents one queued command and completion. `struct olpc_ec_priv` stores the registered transport, command workqueue state, wake mask, suspend state, DCON regulator state, and debugfs root. `olpc_ec_driver_register()` records the transport `struct olpc_ec_driver` and callback argument. `olpc_ec_cmd()` is the exported synchronous command API: it queues a stack descriptor, waits for completion, and returns the platform transport status. `olpc_ec_wakeup_set()`, `olpc_ec_wakeup_clear()`, `olpc_ec_mask_write()`, `olpc_ec_wakeup_available()`, and `olpc_ec_sci_query()` implement common EC wake/event operations. `olpc_ec_worker()` serializes queued commands under `cmd_lock` and calls `ec_driver->ec_cmd()`. DCON regulator operations call `EC_DCON_POWER_MODE`.

Control flow: the platform transport first calls `olpc_ec_driver_register()`. The generic platform driver probes an `olpc-ec` platform device, allocates `olpc_ec_priv`, initializes queue and worker state, assigns the global `ec_priv`, reads `EC_FIRMWARE_REV`, registers the DCON regulator, and creates debugfs if enabled. `olpc_ec_cmd()` validates driver availability and suspend state, queues the command, and blocks until the worker completes it. Suspend writes the accumulated wake mask to the EC, optionally calls the transport suspend hook, then marks the generic layer suspended; resume clears that flag and calls an optional transport resume hook.

State and persistence: `ec_driver`, `ec_priv`, and `ec_cb_arg` are global singleton state. Per-driver state includes command queue, worker, `cmd_lock`, `suspended`, `ec_wakeup_mask`, EC firmware version, and `dcon_enabled`. No persistent storage is used; wake mask and DCON state are runtime-only and reconstructed after probe.

Dependencies and integration points: depends on `linux/olpc-ec.h` command definitions and transport callback type, workqueues, completions, spinlocks, regulator framework, debugfs, and platform driver infrastructure. The XO-1.75 SPI driver is a key transport; battery/AC and other OLPC drivers consume exported EC APIs.

Risks: the generic layer is singleton-based, so multiple EC instances are unsupported. `olpc_ec_cmd()` uses a stack descriptor and depends on the worker completing before the caller returns, which is valid because it waits unconditionally but makes platform transport timeouts essential. During suspend, commands return `-EBUSY`, so callers must tolerate transient failure. Debugfs accepts raw EC commands from root and can alter hardware state. `olpc_ec_probe()` sets `ec_priv` before reading firmware revision; the error path clears it but queued work should not exist yet.

Test signals: unit or integration tests should verify command serialization under concurrent callers, `-EPROBE_DEFER` before transport registration, `-EBUSY` while suspended, wide/narrow SCI mask selection based on firmware revision, DCON regulator enable/disable idempotence, debugfs input validation, and suspend/resume wake-mask writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/olpc/olpc-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/olpc/olpc-xo175-ec.c -->
# sources/distributed-fs/ceph-client/drivers/platform/olpc/olpc-xo175-ec.c

Purpose: OLPC XO-1.75 EC transport and platform integration over SPI target/slave mode. It implements the EC command state machine, receives asynchronous EC channels/events, reports the power button, updates power-supply devices on battery/AC events, registers the generic `olpc-ec` platform device, and provides EC-driven poweroff.

Important APIs, types, and functions: `enum ec_chan_t` defines SPI response channels such as command response, event, debug, keyboard, and touchpad. `enum ec_state_t` tracks command progression from waiting for switch through response/error. `struct olpc_xo175_ec` stores SPI transfer/message buffers, command GPIO, state lock, active command, expected/received response bytes, power-button input device, suspend flag, and debug log buffer. `olpc_xo175_ec_resp_len()` validates known commands and expected response lengths. `olpc_xo175_ec_send_command()` submits asynchronous SPI transfers; `olpc_xo175_ec_read_packet()` sends the nonce used to keep reading EC packets. `olpc_xo175_ec_complete()` is the central SPI completion/channel dispatcher. `olpc_xo175_ec_cmd()` implements `struct olpc_ec_driver.ec_cmd`. Probe/remove are `olpc_xo175_ec_probe()` and `olpc_xo175_ec_remove()`.

Control flow: probe allocates state, obtains the `cmd` GPIO, initializes locks and completions, registers a power-button input device, initializes SPI transfer buffers, starts packet reads, registers the generic OLPC EC transport callback, creates the `olpc-ec` platform device, enables all EC events, and installs `pm_power_off` if free. For a command, the generic layer calls `olpc_xo175_ec_cmd()`, which validates length/suspend state, determines expected response length, initializes command state, raises the command GPIO, and waits up to 4 seconds. `olpc_xo175_ec_complete()` reacts to EC channel packets: `CHAN_SWITCH` lowers the GPIO and sends the command, `CHAN_NONE` marks command sent and may complete zero-length commands, `CHAN_CMD_RESP` accumulates response bytes, `CHAN_CMD_ERROR` completes with remote error, `CHAN_EVENT` notifies power supplies or input/PM wakeup, and `CHAN_DEBUG` buffers printable debug output. On timeout it lowers GPIO, aborts the SPI target, restarts packet reads, and returns `-ETIMEDOUT`.

State and persistence: state is per SPI device but guarded by singleton `olpc_ec` platform-device pointer. Command state is protected by `cmd_state_lock`; only one command is expected because the generic layer serializes calls with its mutex. Runtime event mask is set to all events while awake. No persistent storage exists.

Dependencies and integration points: depends on SPI target/slave APIs (`spi_async`, `spi_target_abort`), GPIO descriptors, input subsystem, power_supply lookup/notification, PM wakeup, reboot poweroff hook, and the generic `olpc-ec` layer. Device-tree compatible is `olpc,xo1.75-ec`; SPI id is `xo1.75-ec`.

Risks: multiple ECs are rejected with `-EBUSY`. The state machine depends on asynchronous SPI completion ordering and command GPIO transitions; missed `CHAN_SWITCH` or packet loss leads to timeout. Unknown commands are allowed if the caller's requested response length fits the internal buffer, which preserves flexibility but expands the ABI surface. Event handling looks up power supplies by fixed names `olpc_ac` and `olpc_battery`. Runtime/system PM hooks are unusual: suspend sets `priv->suspended` after sending a hint and resume noirq clears it; callers during the gap see `-EBUSY`.

Test signals: run on XO-1.75 hardware or a SPI target simulator that emits each channel. Verify known command response length handling, unknown command pass-through limits, timeout recovery, EC error returns, AC/battery power_supply_changed calls, power button input events and wakeups, debug log flushing, suspend/resume hint flow, `pm_power_off` loop command, and remove cleanup of SPI target/platform device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/olpc/olpc-xo175-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/Kconfig

Purpose: Kconfig menu for Broadcom VideoCore support on Raspberry Pi platforms, including the VCHIQ core and optional userspace character device, plus the MMAL-over-VCHIQ service.

Important APIs, types, and functions: `menuconfig BCM_VIDEOCORE` gates the subsystem and depends on OF plus Raspberry Pi firmware support or compatible compile-test conditions. `config BCM2835_VCHIQ` enables the VCHIQ messaging driver and depends on `HAS_DMA`; it implies `VCHIQ_CDEV`. `config VCHIQ_CDEV` controls `/dev/vchiq` ioctl exposure. The file sources `drivers/platform/raspberrypi/vchiq-mmal/Kconfig`.

Control flow: Kconfig determines whether the VCHIQ platform driver, bus, debugfs, optional cdev, and MMAL child directory are built.

State and persistence: configuration state is persisted in `.config`; no runtime state.

Dependencies and integration points: integrates Raspberry Pi firmware mailbox support, device tree, DMA-capable builds, kernel consumers such as audio/camera/MMAL, and optional userspace ABI exposure.

Risks: `BCM_VIDEOCORE` defaults to `y`, but buildability depends on firmware availability or compile-test path. Disabling `VCHIQ_CDEV` removes userspace ABI while preserving kernel-client support; downstream userland libraries may assume it exists.

Test signals: generate configs for Raspberry Pi firmware-enabled builds, compile-test builds without firmware, VCHIQ as module/built-in, and `VCHIQ_CDEV=n`; verify object selection and user-facing device presence match expectations.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/Makefile

Purpose: kbuild rules for the Raspberry Pi VideoCore/VCHIQ driver group.

Important APIs, types, and functions: `obj-$(CONFIG_BCM2835_VCHIQ) += vchiq.o` builds a composite object from `vchiq_core.o`, `vchiq_arm.o`, `vchiq_bus.o`, and `vchiq_debugfs.o`; `vchiq_dev.o` is conditionally added when `CONFIG_VCHIQ_CDEV` is set. `obj-$(CONFIG_BCM2835_VCHIQ_MMAL) += vchiq-mmal/` descends into the MMAL service directory.

Control flow: kbuild links the composite VCHIQ module/built-in and optional child directory based on Kconfig.

State and persistence: no runtime state; build outputs track `.config`.

Dependencies and integration points: ties VCHIQ core, platform glue, bus registration, debugfs, optional miscdevice ABI, and MMAL service into one build product.

Risks: the composite object always includes debugfs stubs even when `CONFIG_DEBUG_FS` is disabled, which is intentional. If `CONFIG_VCHIQ_CDEV=n`, ioctl code is absent; callers must use kernel bus clients only. MMAL depends on VCHIQ symbols exported from the composite.

Test signals: build all combinations of `BCM2835_VCHIQ`, `VCHIQ_CDEV`, and `BCM2835_VCHIQ_MMAL`; inspect final object contents and module dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_arm.c -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_arm.c

Purpose: ARM/platform glue for Raspberry Pi VCHIQ. It allocates coherent shared slots/fragments, initializes the VCHIQ core, handles the doorbell IRQ and firmware initialization mailbox, exposes kernel-client APIs, maintains platform use counts/keepalive state, registers the VCHIQ bus and platform driver, and optionally registers `/dev/vchiq`.

Important APIs, types, and functions: `struct vchiq_arm_state` tracks keepalive thread, completions/counters, suspend-resource lock, VideoCore use counts, and first-connect state. `vchiq_platform_init()` allocates coherent slot and fragment memory, fills slot-zero platform data, initializes the core, maps registers, requests the doorbell IRQ, and sends `RPI_FIRMWARE_VCHIQ_INIT`. `vchiq_initialise()`, `vchiq_shutdown()`, `vchiq_connect()`, `vchiq_open_service()`, `vchiq_bulk_transmit()`, `vchiq_bulk_receive()`, `vchiq_use_service()`, and `vchiq_release_service()` are exported kernel-client entry points. `service_callback()` converts core callbacks into user-service completion/message queues. `vchiq_add_connected_callback()` defers bus-client callbacks until the VCHIQ stack is connected. Probe/remove wire the platform driver to firmware, debugfs, cdev, and the `bcm2835-audio` VCHIQ device.

Control flow: module init registers `vchiq_bus_type` then the platform driver. Probe obtains SoC-specific cache-line data from OF, gets Raspberry Pi firmware, calls `vchiq_platform_init()`, registers the char device, initializes debugfs, and registers a `bcm2835-audio` VCHIQ bus device. Doorbell IRQ reads and clears `BELL0`; when `ARM_DS_ACTIVE` is set it polls all remote events. Kernel clients call `vchiq_initialise()`, wait for remote initialization, then `vchiq_connect()` and service APIs. Bulk APIs select blocking or callback paths. Connection-state changes start a keepalive thread on first connected transition.

State and persistence: `bcm2835_audio` is a global registered VCHIQ child device. Per-platform management state is stored as platform driver data and includes `struct vchiq_state`, mapped regs, firmware handle, coherent fragments, callback deferral state, and cache-line/platform info. Per-instance state tracks connection, completions, bulk waiters, pid, and debugfs node. No persistent storage exists.

Dependencies and integration points: depends on Raspberry Pi firmware property API, OF compatibles `brcm,bcm2835-vchiq` and `brcm,bcm2836-vchiq`, DMA coherent allocation, platform IRQ/resource mapping, VCHIQ core, VCHIQ bus, debugfs, optional char-device registration, and kernel clients such as bcm2835 audio/MMAL.

Risks: the local source snapshot contains duplicated `if (err) {` text in the IRQ request error path, which is a compile-time merge/syntax risk to verify before build. The code relies on 32-bit DMA addresses for firmware. `vchiq_add_connected_callback()` has a fixed deferred callback limit. Keepalive is documented as unused on Raspberry Pi but still implemented, so use-count imbalance can still produce warnings and failed service checks. `vchiq_driver_exit()` unregisters the bus before the platform driver, which should be reviewed against active child devices.

Test signals: compile the file to catch the duplicated IRQ error branch. Boot on BCM2835/BCM2836 DT with firmware node, verify DMA mask, firmware init response, IRQ delivery, `/dev/vchiq` creation when enabled, debugfs state, and child `bcm2835-audio` device registration. Exercise kernel-client initialize/connect/open/bulk/use/release/shutdown paths and suspend use-count diagnostics.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_arm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_bus.c -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_bus.c

Purpose: Generic VCHIQ bus implementation for non-discoverable VideoCore services. It lets the platform driver register named VCHIQ child devices and lets kernel VCHIQ clients bind as normal Linux drivers.

Important APIs, types, and functions: `vchiq_bus_type` defines `.name = "vchiq-bus"`, name-based `.match`, modalias `.uevent`, and probe/remove shims. `vchiq_device_register()` allocates a `struct vchiq_device`, initializes its embedded `struct device`, inherits DMA configuration from the parent, stores parent driver management data, and registers the device. `vchiq_device_unregister()` unregisters it. `vchiq_driver_register()` and `vchiq_driver_unregister()` export registration for `struct vchiq_driver`.

Control flow: `vchiq_arm.c` registers the bus at module init. Platform probe calls `vchiq_device_register(parent, "bcm2835-audio")`; matching is string equality between device name and driver name. Probe/remove callbacks cast from generic device/driver to VCHIQ-specific wrappers and call client hooks.

State and persistence: each registered VCHIQ device is heap allocated and freed by `vchiq_device_release()`. The device stores a pointer to the platform driver's management state. No persistent storage exists.

Dependencies and integration points: depends on Linux driver core, OF DMA configuration, and VCHIQ public bus headers. Integrates with kernel module autoload via `MODALIAS=vchiq:<name>`.

Risks: matching by exact `dev_name()` requires driver names to match registered service names precisely. `vchiq_device_unregister()` assumes a non-NULL pointer; callers should guard failed registrations. Device `init_name` and release semantics are simple but require no later renaming.

Test signals: register/unregister a dummy VCHIQ device and driver, check modalias emission, probe/remove call order, DMA mask configuration, and failure cleanup on `device_register()` errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_bus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_core.c -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_core.c

Purpose: Core VCHIQ message, service, slot, event, bulk-transfer, and connection-state engine. It manages the shared slot ring with VideoCore, service lifecycle/state machines, message queuing, remote events/doorbells, bulk DMA page lists, quotas, and debug dumping.

Important APIs, types, and functions: message type macros encode/decode VCHIQ message ids. `vchiq_init_slots()` lays out slot zero and master/slave shared slot ranges. `vchiq_init_state()` initializes state, quotas, events, mutexes, and starts slot handler, recycle, and sync threads. Service lookup and lifetime are handled by `find_service_by_handle()`, `find_service_for_instance()`, `next_service_by_instance()`, `vchiq_service_get()`, and `vchiq_service_put()` with RCU/kref. `queue_message()` and `queue_message_sync()` send normal and synchronous messages. `parse_message()` handles incoming OPEN/OPENACK/CLOSE/DATA/BULK_DONE/PAUSE/RESUME/REMOTE_USE messages. Bulk support flows through `create_pagelist()`, `free_pagelist()`, `vchiq_prepare_bulk_data()`, `vchiq_bulk_xfer_queue_msg_killable()`, `vchiq_bulk_xfer_blocking()`, `vchiq_bulk_xfer_callback()`, and `vchiq_bulk_xfer_waiting()`. Public APIs include `vchiq_add_service_internal()`, `vchiq_open_service_internal()`, `vchiq_connect_internal()`, `vchiq_close_service()`, `vchiq_remove_service()`, `vchiq_queue_message()`, `vchiq_queue_kernel_message()`, `vchiq_release_message()`, `vchiq_get_peer_version()`, `vchiq_get_config()`, and `vchiq_set_service_option()`.

Control flow: platform setup calls `vchiq_init_slots()` then `vchiq_init_state()`. The slot handler thread waits on the trigger remote event, handles requested polls, and parses RX slots. The recycle thread waits on recycle events and returns freed slots to the available queue while releasing per-service quotas. The sync thread handles synchronous slot messages. Client connect sends CONNECT and waits for remote completion. Service open sends OPEN, waits on `remove_event`, then transitions to OPEN/OPENSYNC. Data messages reserve slot space, enforce global and per-service quotas, copy payload via callback, publish header and tx position with barriers, and signal the remote trigger. Incoming DATA claims the slot and calls the service callback; release later recycles the slot. CLOSE paths mark services closing, abort bulks, release claimed messages, send CLOSE, notify callbacks, and eventually free services.

State and persistence: all runtime state is in `struct vchiq_state`, shared slot memory, service arrays, quotas, completion counters, remote events, and per-service bulk/message queues. Static `handle_seq` provides monotonically changing service handles. DMA pagelist allocations and pinned user pages live for the duration of bulk transfers. No state persists across unload/reboot.

Dependencies and integration points: depends on the Linux scheduler/kthreads, completions, mutexes/spinlocks, RCU, krefs, DMA mapping, user page pinning, highmem helpers, and architecture memory barriers. Platform-specific hooks are `vchiq_platform_init_state()`, `vchiq_platform_conn_state_changed()`, remote event doorbell signaling, and service use/release callbacks in `vchiq_arm.c`.

Risks: this is highly concurrent code with subtle memory barriers across CPU/VideoCore shared memory; missing barriers can corrupt the protocol. Bulk handling pins user pages and maps scatterlists, so error paths must always unpin/unmap and return fragments. Several waits are interruptible/killable and return `-EAGAIN`/`-EINTR`; callers must retry correctly. Quota and service state transitions can deadlock or leak references if callbacks return `-EAGAIN` repeatedly. `vchiq_msg_hold()` has an initial empty-queue return before its wait loop, making the later wait unreachable for empty queues. The core assumes fixed structure sizes and power-of-two constants verified by build-time checks.

Test signals: compile-time static assertions and build coverage across configs. Runtime tests should stress connect/open/close/remove, server and client services, data messages at max size and quota limits, blocking/callback/no-callback bulk transfers, signal interruption and retry, user-page pin failures, partial cache-line receive fragments, pause/resume, remote use/release, and debugfs dumps under active traffic. Sanitizers/lockdep/KCSAN are valuable because most defects are races or lifetime bugs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_debugfs.c

Purpose: Debugfs integration for VCHIQ global state and per-client controls. It exposes a global VCHIQ state dump plus per-instance use count and trace toggle files.

Important APIs, types, and functions: `debugfs_usecount_show()` prints `vchiq_instance_get_use_count()`. `debugfs_trace_show()` and `debugfs_trace_write()` read and set per-instance trace using `vchiq_instance_get_trace()` and `vchiq_instance_set_trace()`. `vchiq_dump_show()` delegates to `vchiq_dump_state()`. `vchiq_debugfs_init()` creates `/sys/kernel/debug/vchiq/state` and `clients/`; `vchiq_debugfs_add_instance()` creates a pid-named directory with `use_count` and `trace`; `vchiq_debugfs_remove_instance()` and `vchiq_debugfs_deinit()` clean up. Stub functions are provided when `CONFIG_DEBUG_FS` is off.

Control flow: platform probe calls `vchiq_debugfs_init()`. Each `/dev/vchiq` open calls `vchiq_debugfs_add_instance()`, and release removes that instance directory. Writes to a client's `trace` file accept first characters `Y/y/1` and `N/n/0`.

State and persistence: static dentries track the top-level VCHIQ directory and clients directory. Per-instance dentry is stored in the instance debugfs node. Debugfs contents are runtime-only and disappear on unload.

Dependencies and integration points: depends on Linux debugfs, seq_file helpers, VCHIQ arm/core getters, and cdev open/release lifecycle.

Risks: `debugfs_trace_write()` copies one byte regardless of `count`; zero-length writes can still attempt copy and should be reviewed. No explicit validation is done for top-level directory creation failures, relying on debugfs tolerance. Per-client directories are named only by pid, so pid reuse is acceptable only because directories are removed on close.

Test signals: with debugfs enabled, verify state dump while services are active, per-client directories on open/close, trace toggling propagation to services, invalid trace writes being ignored, and no-op behavior with `CONFIG_DEBUG_FS=n`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_dev.c -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_dev.c

Purpose: Optional `/dev/vchiq` miscdevice and ioctl ABI for userspace VCHIQ clients. It translates user ioctl structures into core service/message/bulk operations, manages per-file instances, completion queues, VCHI-style message queues, compat 32-bit ABI, and release cleanup.

Important APIs, types, and functions: `ioctl_names[]` maps command numbers to names and is size-checked against `VCHIQ_IOC_MAX`. `vchiq_ioc_create_service()` creates user services with `service_callback`. `vchiq_ioc_queue_message()` copies a vector of user elements through `vchiq_ioc_copy_element_data()`. `vchiq_ioc_dequeue_message()` serves VCHI-style queued messages. `vchiq_irq_queue_bulk_tx_rx()` handles bulk transmit/receive in blocking, waiting, callback, and no-callback modes. `vchiq_ioc_await_completion()` drains the completion ring into user buffers and copies message payloads. `vchiq_ioctl()` dispatches all native ioctls. Compat helpers translate 32-bit pointer-containing structures. `vchiq_open()` allocates an instance; `vchiq_release()` terminates services, releases messages/completions, drops use counts, frees bulk waiters, removes debugfs, and frees the instance. `vchiq_register_chrdev()` and `vchiq_deregister_chrdev()` register the miscdevice.

Control flow: on open, the driver verifies remote initialization, allocates and initializes a `struct vchiq_instance`, records `current->tgid`, creates debugfs, and stores it as `file->private_data`. Ioctls then connect, create/open/listen services, queue messages, queue or wait for bulk transfers, await completions, dequeue VCHI messages, query config/client id, close/remove services, manage use counts, and negotiate library version. Core callbacks call `service_callback()` in `vchiq_arm.c`, which fills the instance completion ring and message queue consumed here. Release marks the instance closing, wakes waiters, terminates all services, waits for them to reach FREE, releases queued message headers and closed-service references, releases peer use count, and frees memory.

State and persistence: per-open instance state includes connected/closing flags, completion ring indices, bulk waiter list, pid, close-delivered mode, and debugfs node. Per-user service state stores the underlying service pointer, userspace userdata, VCHI flag, close pending state, message queue indices, and completions. No persistent storage exists; ABI state lives for the file descriptor lifetime.

Dependencies and integration points: depends on VCHIQ core and arm helpers, miscdevice, Linux user-copy APIs, compat syscall support, debugfs hooks, completions, mutexes, spinlocks, and ioctl definitions in `vchiq_ioctl.h`. It is included only with `CONFIG_VCHIQ_CDEV`.

Risks: this is a direct userspace ABI and must be hardened against invalid pointers, sizes, counts, and signal interruption. The compat queue-message path copies `sizeof(element32)` for the full fixed array rather than `count * sizeof(...)`, requiring user memory for the whole stack array and worth testing. Completion handling depends on memory barriers around ring updates. Close-delivered mode holds service references until userspace acknowledges; misbehaving clients can delay cleanup. Release forces VideoCore awake and assumes use/release balancing succeeds.

Test signals: ioctl ABI tests should cover native and compat create service, connect, close/remove, lib-version negotiation, close-delivered, message vector copy with zero-length elements, invalid user pointers, completion copy with too few msg buffers, blocking and interrupted dequeue, bulk modes and signal retry, release with outstanding services/messages/bulks, and `CONFIG_VCHIQ_CDEV=n` builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_dev.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_ioctl.h -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_ioctl.h

Purpose: Private ioctl ABI definitions for the VCHIQ character device.

Important APIs, types, and functions: `VCHIQ_IOC_MAGIC` is `0xc4`; `VCHIQ_IOC_MAX` is 17. ABI structures include `vchiq_service_params`, `vchiq_create_service`, `vchiq_queue_message`, `vchiq_queue_bulk_transfer`, `vchiq_completion_data`, `vchiq_await_completion`, `vchiq_dequeue_message`, `vchiq_get_config`, `vchiq_set_service_option`, and `vchiq_dump_mem`. Ioctls define connect, shutdown, create/remove/close service, queue message, queue bulk transmit/receive, await completion, dequeue message, get client id/config, use/release service, set service option, dump physical memory, library version, and close-delivered notification.

Control flow: userspace passes these structures to `vchiq_dev.c`, which dispatches by ioctl number and copies data to/from user buffers. The header itself contains no executable flow.

State and persistence: ABI structures describe per-call state crossing the user/kernel boundary. No runtime state is stored in the header.

Dependencies and integration points: includes `linux/ioctl.h` and public `linux/raspberrypi/vchiq.h` for shared enums and types. It is tightly coupled to `vchiq_dev.c` native and compat handlers and userspace VCHIQ libraries.

Risks: ABI layout is fixed; changing field types, order, or ioctl numbers would break userspace. Function-pointer-looking `callback` in `vchiq_service_params` is a userspace token, not invoked directly by the kernel. Pointer-bearing structures require explicit compat translations.

Test signals: compile userspace/kernel headers together, verify ioctl number stability with static tests, and run native plus 32-bit compat ioctl round trips for every pointer-containing command.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-interface/vchiq_ioctl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/Kconfig

Purpose: Kconfig option for the BCM2835 MMAL service over VCHIQ.

Important APIs, types, and functions: `config BCM2835_VCHIQ_MMAL` is a tristate depending on `BCM2835_VCHIQ`. Its help states that it enables the MMAL API over VCHIQ for VideoCore multimedia services.

Control flow: selected by configuration; the parent Raspberry Pi Kconfig sources this file under the VideoCore menu.

State and persistence: configuration state persists in `.config`; no runtime state.

Dependencies and integration points: depends on the VCHIQ core driver and integrates with the `vchiq-mmal/Makefile` to build `bcm2835-mmal-vchiq.o`.

Risks: help text contains a minor typo ("Broadcomd"). Enabling this without consumers still builds the MMAL VCHIQ service object; disabling it removes MMAL kernel support even if camera/multimedia drivers expect it.

Test signals: build with `BCM2835_VCHIQ_MMAL=y/m/n` and confirm object inclusion and symbol availability for MMAL consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/Makefile -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/Makefile

Purpose: kbuild rules for the BCM2835 MMAL-over-VCHIQ service object.

Important APIs, types, and functions: `bcm2835-mmal-vchiq-objs := mmal-vchiq.o` defines the composite object contents. `obj-$(CONFIG_BCM2835_VCHIQ_MMAL) += bcm2835-mmal-vchiq.o` includes it based on Kconfig.

Control flow: kbuild compiles and links `mmal-vchiq.o` into the named object when enabled.

State and persistence: no runtime state; build state follows `.config`.

Dependencies and integration points: depends on `CONFIG_BCM2835_VCHIQ_MMAL` and MMAL source/header files in the same directory.

Risks: the Makefile only includes `mmal-vchiq.o`; all shared structures must remain header-only or linked from that object. Missing `mmal-vchiq.c` would fail the build.

Test signals: build the directory under built-in and module configurations and inspect module/object contents.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-common.h -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-common.h

Purpose: Common MMAL data structures and constants shared by the BCM2835 V4L2/MMAL bridge.

Important APIs, types, and functions: `MMAL_FOURCC()` constructs little-endian FourCC values; `MMAL_MAGIC` identifies MMAL messages; `MMAL_TIME_UNKNOWN` marks unknown timestamps. `struct mmal_fmt` maps V4L2 pixel formats to MMAL encodings, flags, depths, component selection, planar Y bits-per-pixel, and padding behavior. `struct mmal_buffer` embeds `vb2_v4l2_buffer` first, adds list linkage, allocated buffer pointer/size, MMAL message context, payload length, MMAL flags, DTS, and PTS. `struct mmal_colourfx` carries color-effect enable and U/V values.

Control flow: this header defines data contracts only; consumers allocate and populate these structures in MMAL/V4L2 implementation code.

State and persistence: no global state. Buffer instances persist for their vb2/MMAL lifecycle and carry timestamps/flags between V4L2 and MMAL callbacks.

Dependencies and integration points: relies on Linux integer types, `BIT_ULL`, V4L2/videobuf2 types included by users, list heads, and MMAL message context definitions. It is used by MMAL VCHIQ and likely camera/video code.

Risks: `struct mmal_buffer` requires the V4L2 buffer to remain first for container casts; reordering would break callers. FourCC construction assumes byte ordering matching MMAL protocol expectations. Padding-removal fields must agree with GPU behavior and V4L2 bytesperline handling.

Test signals: compile all MMAL consumers, verify container casts from `vb2_v4l2_buffer`, check format table mappings, and exercise timestamp/flag propagation through buffer completion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-encodings.h -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-encodings.h

Purpose: MMAL encoding, image format, audio format, H.264 variant, and colorspace FourCC constants.

Important APIs, types, and functions: defines codec encodings such as H264/H263/MP4V/MJPEG/JPEG/PNG; raw image formats such as I420/YV12/YUYV/NV12/RGBA/BGRA/RGB variants; VideoCore-specific `MMAL_ENCODING_YUVUV128`, `MMAL_ENCODING_OPAQUE`, and `MMAL_ENCODING_EGL_IMAGE`; PCM audio endian/sign variants; H.264 stream variants; and predefined color spaces such as BT.601, BT.709, JPEG JFIF, FCC, SMPTE240M, and BT.470.

Control flow: no executable flow; constants are consumed when configuring MMAL component formats and translating to/from V4L2.

State and persistence: no runtime state.

Dependencies and integration points: depends on `MMAL_FOURCC()` from `mmal-common.h` being included before or alongside this header by consumers. Integrates with MMAL firmware protocol and V4L2 format mapping tables.

Risks: constants are protocol ABI values; any typo changes firmware negotiation. Some FourCC values include spaces and lowercase letters, so style cleanup can accidentally alter ABI. Consumers must include prerequisites in the correct order because this header does not include `mmal-common.h` itself.

Test signals: static assertions or unit tests comparing expected FourCC numeric values, format-negotiation tests with VideoCore firmware, and compile tests for include ordering in all consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-encodings.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-common.h -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-common.h

Purpose: Common MMAL message status values and basic geometry structure for MMAL protocol messages.

Important APIs, types, and functions: `enum mmal_msg_status` mirrors firmware status/error codes including success, memory/resource errors, invalid argument, not implemented, device/address errors, I/O/corrupt data, not ready/configured, connection state errors, retry, and bad address. `struct mmal_rect` contains signed x/y/width/height fields.

Control flow: no executable flow; these definitions are embedded in request/response structures and status conversion logic elsewhere.

State and persistence: no state.

Dependencies and integration points: includes `linux/types.h`; used by MMAL format and port message headers and by MMAL VCHIQ response handlers.

Risks: enum numeric order is part of the protocol contract with firmware; inserting or reordering values would break status decoding. `mmal_rect` signed fields must match firmware structure layout.

Test signals: ABI/layout checks against firmware expectations, status-to-errno mapping tests in MMAL implementation, and crop/rectangle round-trip tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-format.h -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-format.h

Purpose: Local and remote MMAL elementary stream format structures used to describe audio, video, and subpicture streams in MMAL messages.

Important APIs, types, and functions: `struct mmal_audio_format` carries channel count, sample rate, bits per sample, and block alignment. `struct mmal_video_format` carries width, height, crop rectangle, frame rate, pixel aspect ratio, and color space. `struct mmal_subpicture_format` carries x/y offsets. `union mmal_es_specific_format` selects the type-specific structure. `struct mmal_es_format_local` uses real kernel pointers for type-specific data and extradata. `struct mmal_es_format` is the remote/wire representation using 32-bit pointer/handle fields.

Control flow: no executable flow; consumers convert between local pointer-rich structures and remote 32-bit firmware message representations.

State and persistence: no global state. Format instances persist as component/port configuration state in consumers.

Dependencies and integration points: includes `linux/math.h` for `struct s32_fract` and `mmal-msg-common.h` for `mmal_rect`. Integrates with MMAL port setup and V4L2 format negotiation.

Risks: confusing local and remote forms can leak kernel pointers or send invalid firmware addresses. Structure layout and field widths must match the VideoCore MMAL ABI. Extradata size/pointer handling is a common bounds and lifetime risk.

Test signals: compile-time layout checks, local-to-remote conversion tests, video crop/frame-rate/PAR negotiation tests, and codec extradata round trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-format.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-port.h -->
# sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-port.h

Purpose: MMAL port type, capability flags, and remote port descriptor structure.

Important APIs, types, and functions: `enum mmal_port_type` identifies unknown, control, input, output, and clock ports. Capability flags describe pass-through ports, ports preferring payload allocation, and ports supporting event-based format changes. `struct mmal_port` mirrors firmware port metadata: private/name pointers, type, index, enabled state, format pointer, minimum/recommended buffer counts and sizes, alignment, selected buffer count/size, component pointer, userdata, and capabilities.

Control flow: no executable flow; this is a protocol structure exchanged with or interpreted from MMAL firmware.

State and persistence: no global state. Port descriptors become runtime component/port configuration state in MMAL consumers.

Dependencies and integration points: expects Linux fixed-width integer types from surrounding includes. Integrates with MMAL format structures and component/port enable/configuration messages.

Risks: most fields are informational/read-only, while comments state only `buffer_num`, `buffer_size`, and `userdata` are writable when setting values. Writing other fields may be ignored or rejected by firmware. Pointer-like fields are 32-bit remote references, not kernel pointers. Capability flags control buffer allocation strategy and format-change handling; misinterpreting them can cause buffer underruns or failed reconfiguration.

Test signals: port query/set round trips with firmware, layout checks, tests that only writable fields are changed during set operations, and format-change event handling on ports advertising the capability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/raspberrypi/vchiq-mmal/mmal-msg-port.h -->
