# subset-b-005166 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/intel_rapl_common.c -->
# sources/distributed-fs/ceph-client/drivers/powercap/intel_rapl_common.c

Purpose: shared Intel RAPL implementation used by interface backends such as MSR and TPMI. It converts backend register primitives into Linux powercap zones, constraints, energy counters, and optional perf PMU events.

Important APIs/types/functions: exported `rapl_add_package*()`, `rapl_remove_package*()`, `rapl_find_package_domain*()`, `rapl_package_add_pmu*()`, `rapl_package_remove_pmu*()`, `rapl_default_check_unit()`, `rapl_default_set_floor_freq()`, and `rapl_default_compute_time_window()`. Core types come from `linux/intel_rapl.h`: `rapl_package`, `rapl_domain`, `rapl_if_priv`, `rapl_defaults`, `rapl_primitive_info`, and `reg_action`. The powercap-facing ops are `zone_ops[]` and `constraint_ops`.

Control flow: a backend builds `rapl_if_priv` with register tables, primitive descriptors, callbacks, and a powercap control type, then calls `rapl_add_package()`. The common layer resolves package id, checks configuration, detects domains by reading energy status registers, initializes per-domain register/unit data, detects power-limit availability and BIOS locks, registers parent and child powercap zones, and adds the package to the global list. Sysfs callbacks read/write translated primitive values through `rapl_read_data_raw()` and `rapl_write_data_raw()`. Optional perf support registers a dynamic `power` PMU, maps perf event ids to RAPL domains, scales hardware energy deltas to 2^-32 Joules, and periodically samples counters with an hrtimer.

State and persistence: `rapl_packages` is protected by the CPU hotplug read lock. Per-package state tracks domains, powercap parent zone, lead CPU, PMU data, IRQ-save state, and last suspend power limits. Suspend notifications save package PL values and restore them after resume. Removal disables PL enable/clamp bits, restores package power-limit interrupt masking, unregisters child zones before parent, removes the package list node, and frees memory through powercap release paths.

Dependencies/integration: depends on x86 topology, MSR feature bits, powercap core, perf events, sysfs, suspend notifiers, CPU hotplug locking, and backend callbacks. It imports RAPL interface details from MSR/TPMI modules and exports the `INTEL_RAPL` namespace to those modules.

Risks: primitive mask/shift mistakes affect all users; package identity differs between AMD/Hygon package-scope MSRs and Intel die-scope MSRs; PL lock detection must avoid writable sysfs for BIOS-locked controls; PMU updates unregister/re-register the PMU when domain coverage grows; energy counter wrap handling depends on hrtimer interval and scale math; `rapl_detect_domains()` currently does not abort on per-domain unit failures.

Test signals: boot on supported MSR and TPMI platforms; inspect `/sys/class/powercap/intel-rapl:*`; read energy counters and constraint files; write power limits and time windows; suspend/resume and confirm limits persist; offline/online package CPUs; run `perf list`/`perf stat -e power/energy-pkg/`; exercise BIOS-locked and monitoring-only domains.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/intel_rapl_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/intel_rapl_msr.c -->
# sources/distributed-fs/ceph-client/drivers/powercap/intel_rapl_msr.c

Purpose: RAPL backend for MSR-based Intel, AMD, and Hygon platforms. It supplies MSR register maps, primitive bit layouts, platform defaults, CPU matching, and hotplug package creation for the common RAPL layer.

Important APIs/types/functions: `rapl_msr_probe()`, `rapl_msr_remove()`, `rapl_cpu_online()`, `rapl_cpu_down_prep()`, `rapl_msr_read_raw()`, `rapl_msr_write_raw()`, `rapl_check_unit_atom()`, `set_floor_freq_atom()`, and `rapl_compute_time_window_atom()`. Static `rapl_if_priv` instances describe Intel and AMD/Hygon register availability. `rpi_msr[]` maps RAPL primitives to MSR masks and shifts.

Control flow: module init registers a platform driver, matches the boot CPU against `rapl_ids`, and creates an `intel_rapl_msr` platform device with the selected defaults. Probe selects vendor-specific `rapl_if_priv`, installs raw read/write callbacks, attaches defaults and primitive descriptors, enables PL4 or MSR PMU support when requested by CPU defaults, registers the `intel-rapl` powercap control type, and installs a dynamic CPU hotplug state. CPU-online creates a common-layer package when the first CPU for that package/die appears; CPU-down removes the package when its cpumask becomes empty.

State and persistence: global `rapl_msr_priv` is the active backend descriptor and `rapl_msr_pmu` gates PMU registration. Per-package state lives in common RAPL structures. The write path uses `smp_call_function_single()` to update MSRs on the selected CPU with read-modify-write semantics; PMU reads can use direct `rdmsrq()` when already executing in the PMU context.

Dependencies/integration: depends on x86 CPU model tables, `asm/msr.h`, Intel family macros, IOSF MBI for Atom floor-frequency control, CPU hotplug, powercap, and common RAPL exported symbols. AMD/Hygon support is monitoring-oriented with package and core energy status registers.

Risks: CPU model defaults must match actual MSR layouts; PL4 and SPR Psys layout fixups require correct feature flags; Atom unit conversion differs from core CPUs; floor-frequency IOSF writes cache an original static value; CPU hotplug ordering must keep `lead_cpu` valid for MSR access; failed platform-device registration is logged but module init still succeeds.

Test signals: verify CPU model table coverage, module/device probe, powercap zones for each online package/die, hotplug add/remove, PL4 sysfs exposure on selected CPUs, PMU event exposure on PMU-capable defaults, AMD/Hygon energy reads, and Atom unit/time-window conversion on applicable systems.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/intel_rapl_msr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/intel_rapl_tpmi.c -->
# sources/distributed-fs/ceph-client/drivers/powercap/intel_rapl_tpmi.c

Purpose: RAPL backend for Intel TPMI auxiliary devices. It maps TPMI MMIO domain records into common RAPL packages and exposes powercap and perf PMU support without CPU-hotplug package discovery.

Important APIs/types/functions: `struct tpmi_rapl_package`, `trp_alloc()`, `trp_release()`, `parse_one_domain()`, `tpmi_rapl_read_raw()`, `tpmi_rapl_write_raw()`, `rapl_check_unit_tpmi()`, `intel_rapl_tpmi_probe()`, and `intel_rapl_tpmi_remove()`. `rpi_tpmi[]` defines TPMI primitive masks for PL1, PL2, PL4, locks, enables, energy, perf, and power info.

Control flow: auxiliary probe obtains TPMI platform data and a single resource, allocates a TPMI package wrapper, ioremaps the resource, and walks 128-byte domain records. `parse_one_domain()` validates version, domain size, mandatory unit/energy registers, domain type, root-system-domain status, duplicate domains, and register flags. It fills the backend register table with MMIO addresses and limit bitmaps. Probe then initializes `rapl_if_priv`, rejects duplicate package ids, calls `rapl_add_package()` with package id rather than CPU id, and adds a common RAPL PMU.

State and persistence: `tpmi_rapl_packages` and `tpmi_control_type` are protected by `tpmi_rapl_lock`; the shared `intel-rapl` powercap control type is registered for the first TPMI package and unregistered after the last is released. Per-package MMIO state is owned by devm ioremap plus the `tpmi_rapl_package` allocation; removal removes PMU, powercap package, and wrapper.

Dependencies/integration: depends on auxiliary bus, Intel VSEC/TPMI helpers, MMIO `readq()/writeq()`, common RAPL namespace, and powercap. Domain root filtering prevents non-root system domains from creating platform RAPL zones.

Risks: firmware-reported domain flags are trusted after validation; unsupported minor versions are only logged and still parsed; a parsing error aborts the whole package; write operations are unlocked MMIO read-modify-write through the common layer; multiple resources are rejected; `trp_alloc()` has careful first-package cleanup requirements.

Test signals: probe with valid/invalid TPMI resources, duplicate domains, non-root system domains, PL1/PL2/PL4 availability, package removal, powercap control type lifetime across multiple devices, perf PMU event visibility, and sysfs reads/writes against TPMI registers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/intel_rapl_tpmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/powercap_sys.c -->
# sources/distributed-fs/ceph-client/drivers/powercap/powercap_sys.c

Purpose: generic Linux power capping sysfs class. It lets drivers register control types and nested zones with common attributes for enable state, energy/power telemetry, and power-limit constraints.

Important APIs/types/functions: exported `powercap_register_control_type()`, `powercap_unregister_control_type()`, `powercap_register_zone()`, and `powercap_unregister_zone()`. Internal helpers seed global `constraint_N_*` device attributes, create constraints, validate control types, manage device release, and implement sysfs show/store callbacks.

Control flow: `powercap_init()` seeds one global set of constraint attribute objects and registers class `powercap`. Drivers first register a control type device, then register zones under either the control type or another zone. Zone registration validates callbacks, allocates or resets the zone, assigns an ID from the parent idr, duplicates the name, allocates constraints and attribute arrays, attaches attributes based on supplied ops, registers the device, and increments `nr_zones`. Unregistration decrements `nr_zones` and unregisters the device; device release removes IDs, destroys child idrs, frees allocations, and calls driver release hooks.

State and persistence: `powercap_cntrl_list` is protected by `powercap_cntrl_list_lock`; each control type has its own lock and idr. Constraint attribute name strings are global and allocated once for `MAX_CONSTRAINTS_PER_ZONE`, while each zone stores pointers to the relevant attributes. Device lifetime uses kernel device references and release callbacks.

Dependencies/integration: used by RAPL and other powercap providers. The sysfs ABI includes `enabled`, zone `name`, `energy_uj`, `power_uw`, max range files, and `constraint_<id>_{power_limit_uw,time_window_us,name,...}` depending on callbacks.

Risks: unregistering a control type with live zones fails; global constraint attributes must outlive all zones; sysfs attribute names are parsed with `sscanf`; a driver-supplied embedded zone requires a release callback; `enabled_show()` treats callback failures as disabled; energy reset only accepts zero and silently ignores nonzero input.

Test signals: module init class creation, control type registration/unregistration with and without zones, nested zone registration, sysfs permission modes, constraint count bounds, callback failure propagation, device lifetime under open sysfs references, and invalid registration parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/powercap/powercap_sys.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pps/Kconfig

Purpose: top-level Kconfig for LinuxPPS support.

Important entries: `menuconfig PPS` builds `pps_core.ko` and describes Pulse Per Second time-reference use cases. `PPS_DEBUG` enables debug messages by adding `-DDEBUG` in Makefiles. `NTP_PPS` enables the in-kernel hardpps consumer and depends on `!NO_HZ_COMMON`. It sources client and generator Kconfig files.

Control flow: selecting `PPS` opens subordinate options for clients and generators; `NTP_PPS` conditionally includes `kc.o` in the core build.

State/dependencies: configuration-only file; no runtime state. Depends on TTY/parport/platform-specific options indirectly through sourced Kconfigs.

Risks: `NTP_PPS` is unavailable with common tickless support, so kernel time synchronization may be absent even when PPS char devices are enabled.

Test signals: verify menu visibility, module names, `CONFIG_PPS_DEBUG` compile flags, and `CONFIG_NTP_PPS` gating of kernel consumer APIs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pps/Makefile

Purpose: builds the PPS core and descends into client/generator directories.

Important rules: `pps_core-y := pps.o kapi.o sysfs.o`; `pps_core-$(CONFIG_NTP_PPS) += kc.o`; `obj-$(CONFIG_PPS) := pps_core.o`; `obj-y += clients/`; `obj-$(CONFIG_PPS_GENERATOR) += generators/`; debug config adds `-DDEBUG`.

Control flow/state: build-only file. The clients directory is always visited so individual client objects can follow their own Kconfig symbols. Generator core is only included when `CONFIG_PPS_GENERATOR` is set.

Dependencies/integration: aligns with top-level Kconfig and header-provided exported PPS APIs.

Risks/test signals: confirm `kc.o` appears only with `CONFIG_NTP_PPS`, clients still build as modules when `PPS` is enabled, generator directory is skipped unless configured, and debug builds emit expected dev/pr debug calls.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pps/clients/Kconfig

Purpose: configuration menu for PPS input clients.

Important entries: `PPS_CLIENT_KTIMER` is a debug timer source; `PPS_CLIENT_LDISC` depends on `TTY` and captures serial carrier-detect changes; `PPS_CLIENT_PARPORT` depends on `PARPORT`; `PPS_CLIENT_GPIO` captures PPS from a GPIO-backed platform device.

Control flow/state: configuration-only. Each option maps to a client object in the clients Makefile and depends on the PPS core APIs at runtime.

Dependencies/integration: TTY line discipline, parallel-port subsystem, GPIO descriptor/platform firmware, and timer APIs.

Risks/test signals: verify menu dependencies hide unavailable clients, module names match help text, and selected clients link against exported `pps_register_source()`, `pps_unregister_source()`, and `pps_event()`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pps/clients/Makefile

Purpose: maps PPS client Kconfig symbols to client object files.

Important rules: builds `pps-ktimer.o`, `pps-ldisc.o`, `pps_parport.o`, and `pps-gpio.o` from their respective `CONFIG_PPS_CLIENT_*` symbols. Debug config adds `-DDEBUG`.

Control flow/state: build-only file with no runtime state.

Dependencies/integration: object names define module names and must match Kconfig help text plus source module metadata.

Risks/test signals: run configured builds for each client as built-in and module; confirm debug flag and object naming, especially hyphen/underscore distinction for `pps_parport`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/pps-gpio.c -->
# sources/distributed-fs/ceph-client/drivers/pps/clients/pps-gpio.c

Purpose: platform driver that turns GPIO edges into PPS assert/clear events, optionally driving an echo GPIO for a bounded active pulse.

Important APIs/types/functions: `struct pps_gpio_device_data`, `pps_gpio_probe()`, `pps_gpio_remove()`, `pps_gpio_irq_handler()`, `pps_gpio_echo()`, `pps_gpio_setup()`, and `get_irqf_trigger_flags()`.

Control flow: probe allocates per-device data, obtains an input GPIO, reads `assert-falling-edge`, optionally obtains an `echo` GPIO and validates `echo-active-ms`, maps the GPIO to an IRQ, fills `pps_source_info`, registers a PPS source, then requests the IRQ with rising/falling/both-edge flags. The IRQ handler timestamps immediately with `pps_get_ts()`, samples GPIO value when clear capture is enabled, emits assert or clear with `pps_event()`, or rate-limited warns if the edge direction does not map. Echo mode sets the echo GPIO and arms a timer to clear it.

State and persistence: per-device state is devm-managed except the PPS source, IRQ, and timer. Remove frees IRQ, unregisters PPS, deletes echo timer, and forces echo low.

Dependencies/integration: platform bus, firmware properties, gpiod consumer API, IRQ subsystem, timers, jiffies, and PPS core.

Risks: `capture_clear` is never populated from firmware in this file, so clear capture appears disabled unless initialized elsewhere; remove calls `gpiod_set_value()` even if echo GPIO is absent; IRQ value sampling after timestamp can race edge bounce; echo timer uses `add_timer()` rather than modifying an active timer; bad `echo-active-ms` rejects probe.

Test signals: device-tree compatible `pps-gpio`, assert edge selection, optional echo GPIO pulse duration, IRQ cleanup, PPS sysfs sequence increments, and clear-capture behavior if firmware support is added.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/pps-gpio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/pps-ktimer.c -->
# sources/distributed-fs/ceph-client/drivers/pps/clients/pps-ktimer.c

Purpose: debug PPS client that synthesizes one assert event per second from a kernel timer.

Important APIs/functions: global `pps`, `ktimer`, `pps_ktimer_event()`, `pps_ktimer_init()`, `pps_ktimer_exit()`, and static `pps_source_info`.

Control flow: module init registers a PPS source with assert capture, offset, echo, wait, and timespec capabilities, initializes a timer, and schedules it for `jiffies + HZ`. Each timer callback timestamps with `pps_get_ts()`, emits `PPS_CAPTUREASSERT`, and reschedules itself one second later. Exit deletes the timer synchronously and unregisters the source.

State/dependencies: global singleton state, PPS core, timer wheel, jiffies, module ownership. No persistent configuration.

Risks: intended only for debugging; timer jitter makes it unsuitable as a precision reference; global state supports one source only; callback assumes registration succeeded and `pps` remains valid until timer deletion.

Test signals: load/unload module, observe `/dev/ppsN`, `assert` sysfs sequence increments approximately once per second, blocking `PPS_FETCH`, and clean unload while userspace has the device open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/pps-ktimer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/pps-ldisc.c -->
# sources/distributed-fs/ceph-client/drivers/pps/clients/pps-ldisc.c

Purpose: TTY line discipline that exposes serial DCD transitions as PPS assert/clear events.

Important APIs/functions: `pps_tty_init()`, `pps_tty_cleanup()`, `pps_tty_open()`, `pps_tty_close()`, and `pps_tty_dcd_change()`. It inherits N_TTY operations through `n_tty_inherit_ops()`.

Control flow: init clones N_TTY ops, replaces owner, number, name, DCD-change, open, and close callbacks, then registers line discipline `N_PPS`. Open creates PPS source metadata from tty driver name/index, registers a PPS source with both-edge capture, stores the tty pointer in `lookup_cookie`, then opens the underlying N_TTY discipline. DCD changes timestamp immediately, find the PPS device by cookie, and emit assert on active or clear on inactive. Close calls the original N_TTY close, looks up the PPS device, and unregisters it.

State/dependencies: state is per-open PPS device plus global saved N_TTY callbacks. Uses `pps_lookup_dev()` cookie matching instead of tty-owned storage. Depends on TTY line discipline locking, serial DCD notifications, and PPS core.

Risks: comments acknowledge convoluted ldisc locking; lookup failure is only warned; open failure after PPS registration must unregister; close unregisters after base close; cookie lookup is a linear idr scan and must not dereference stale tty cookies.

Test signals: attach `N_PPS` to a serial tty, toggle DCD, verify assert/clear sequences and `/dev/ppsN` path, open error rollback, close cleanup, and module unload after line disciplines detach.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/pps-ldisc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/pps_parport.c -->
# sources/distributed-fs/ceph-client/drivers/pps/clients/pps_parport.c

Purpose: PPS client for parallel-port ACK interrupt pulses, with optional polling to capture the clear edge.

Important APIs/types/functions: `struct pps_client_pp`, module parameter `clear_wait`, `parport_irq()`, `parport_attach()`, `parport_detach()`, `signal_is_set()`, and `pps_parport_driver`.

Control flow: parport attach validates `clear_wait`, allocates state and an IDA index, registers an exclusive parport device with an IRQ callback, claims the port, registers a PPS source with both-edge support, stores the clear-wait count, enables port IRQs, and logs attachment. IRQ handler timestamps assert immediately; if clear capture is enabled it disables local IRQs, verifies signal is still high, polls status up to `cw` reads for signal clear, timestamps clear if observed, and emits assert plus optional clear. Repeated clear timeouts disable clear capture. Detach identifies its current parport device, disables IRQ, unregisters PPS, releases/unregisters parport device, frees IDA index and memory.

State/dependencies: per-port `pps_client_pp` holds parport device, PPS device, timeout counters, and index. Depends on parport ops and PPS core.

Risks: detach relies on `port->cad` and a comment calls this ugly; local IRQ disabling while polling must remain bounded; clear edge can be lost; repeated timeouts silently degrade to assert-only capture; attach rollback has several resource stages.

Test signals: attach/detach on parport hardware, IRQ assert capture, clear capture with different `clear_wait` values, timeout degradation after five failures, IDA reuse, and exclusive claim conflicts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/clients/pps_parport.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pps/generators/Kconfig

Purpose: configuration menu for PPS signal generators.

Important entries: `PPS_GENERATOR` builds generator core `pps_gen_core`; `PPS_GENERATOR_DUMMY` builds a debug generator; `PPS_GENERATOR_TIO` depends on x86 Intel CPU support and targets Intel Time-Aware IO hardware.

Control flow/state: configuration-only. TIO help states it needs specialized external hardware to observe pulses.

Dependencies/integration: PPS generator core, x86 CPU feature support, and platform/ACPI hardware for TIO.

Risks/test signals: confirm generator core can be modular, dummy and TIO module names match help text, TIO is hidden on non-x86/non-Intel builds, and `PPS_DEBUG` affects generator compilation through Makefile flags.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pps/generators/Makefile

Purpose: builds the PPS generator core and optional generator drivers.

Important rules: `pps_gen_core-y := pps_gen.o sysfs.o`; `obj-$(CONFIG_PPS_GENERATOR) := pps_gen_core.o`; optional objects are `pps_gen-dummy.o` and `pps_gen_tio.o`; debug config adds `-DDEBUG`.

Control flow/state: build-only file.

Dependencies/integration: source module names and Kconfig symbols must align with userspace-visible `/dev/pps-genN` support from the core.

Risks/test signals: build all generator combinations as built-in/module, verify core is present before optional drivers link, and ensure debug builds compile all generator objects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen-dummy.c -->
# sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen-dummy.c

Purpose: debug PPS generator that never drives real hardware and reports missed-pulse events after a randomized timer delay.

Important APIs/functions: global `pps_gen`, `ktimer`, `get_random_delay()`, `pps_gen_ktimer_event()`, `pps_gen_dummy_get_time()`, `pps_gen_dummy_enable()`, and `pps_gen_dummy_info`.

Control flow: module init registers a generator source and sets up a timer. Enabling arms the timer for 1-16 seconds based on a random low nibble; disabling deletes it. Timer callback reports `PPS_GEN_EVENT_MISSEDPULSE` through `pps_gen_event()`. Time reads return a realtime snapshot.

State/dependencies: singleton generator state, timer wheel, random byte helper, system time snapshot, and PPS generator core. No persistent configuration.

Risks: timer callback is one-shot and not rescheduled, so each enable produces at most one missed event unless userspace toggles enable; no real pulse output; global state supports one instance.

Test signals: load module, see `/dev/pps-genN`, read `system` and `time` sysfs, enable/disable through ioctl or sysfs, wait for missed-pulse event, and unload cleanly with timer pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen-dummy.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen.c -->
# sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen.c

Purpose: core PPS generator character-device framework. It registers `/dev/pps-genN` devices, exposes generator sysfs groups, supports enable/time ioctls, and lets hardware drivers report generator events.

Important APIs/types/functions: exported `pps_gen_register_source()`, `pps_gen_unregister_source()`, and `pps_gen_event()`. Internal paths include `pps_gen_cdev_ioctl()`, `pps_gen_register_cdev()`, `pps_gen_unregister_cdev()`, `pps_gen_device_destruct()`, and class `pps_gen_class`.

Control flow: subsystem init registers class `pps-gen` and allocates a chrdev range. A generator driver passes `pps_gen_source_info`; the core allocates a `pps_gen_device`, initializes waitqueue and spinlock, allocates an IDA id, adds a cdev, creates `pps-genN`, and stores drvdata. Open gets a device reference. `PPS_GEN_SETENABLE` calls the driver `enable()` callback then updates `enabled`; `PPS_GEN_USESYSTEMCLOCK` returns the source flag; `PPS_GEN_FETCHEVENT` blocks until `last_ev` changes, copies sequence and event to userspace. `pps_gen_event()` updates event state, wakes waiters, and signals async readers.

State/dependencies: global devt and IDA, per-generator waitqueue/spinlock/event counters/fasync queue. Depends on cdev, device class, uaccess, poll, fasync, and generator sysfs declarations.

Risks: `poll()` always reports readable rather than checking event sequence; unregister only destroys the device and relies on release for freeing; ioctl and sysfs can both call driver enable paths; event wait snapshots `last_ev` before sleeping and can miss only if driver updates incorrectly; owner field may be unset by simple generators.

Test signals: register multiple generators up to `PPS_GEN_MAX_SOURCES`, ioctl enable/time/event paths, blocking and interrupted event fetch, fasync SIGIO, open file during unregister, and class cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen_tio.c -->
# sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen_tio.c

Purpose: Intel PMC Time-Aware IO PPS generator. It programs a hardware compare register against ART-derived time and uses an hrtimer to keep future pulses scheduled.

Important APIs/types/functions: `struct pps_tio`, `pps_gen_tio_probe()`, `pps_gen_tio_remove()`, `pps_tio_gen_enable()`, `hrtimer_callback()`, `pps_generate_next_pulse()`, `pps_tio_direction_output()`, `pps_tio_disable()`, and `pps_tio_enable()`.

Control flow: platform probe checks TSC known frequency and ART CPU features, allocates state, initializes generator callbacks, registers with PPS generator core, maps MMIO resource, disables hardware, initializes an absolute realtime hrtimer and spinlock, and stores drvdata. Enable verifies the clocksource has ART base, configures output/toggle mode, enables hardware, and starts the hrtimer for the first event just before the next second boundary. The hrtimer checks event counter progress, ensures it is not too late, converts the next realtime expiry to ART cycles, writes compare value minus hardware delay, and forwards by half a second. Missed events disable hardware and report `PPS_GEN_EVENT_MISSEDPULSE`.

State/dependencies: per-device MMIO base, hrtimer, previous event count, spinlock, generator device, and callback structure. Depends on ACPI IDs, platform resources, ART clocksource conversion, CPU feature bits, and `hi_lo_writeq()` ordering.

Risks: probe leaks a registered generator if MMIO mapping fails after registration; timing depends on realtime-to-ART conversion and `SAFE_TIME_NS`; event-count check disables on missed pulses; sysfs/core `enabled` state is updated both by core and driver; spinlock protects enable/timer races.

Test signals: ACPI match, feature-gated probe failure, MMIO resource failure cleanup, enable/disable, ART conversion failure, event-counter missed-pulse path, external observation of PPS pulse timing, and remove while enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/pps_gen_tio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/pps/generators/sysfs.c

Purpose: sysfs attributes for PPS generator devices.

Important APIs/functions: `system_show()`, `time_show()`, `enable_store()`, `pps_gen_attrs[]`, `pps_gen_group`, and exported `pps_gen_groups`.

Control flow: class registration in `pps_gen.c` attaches `pps_gen_groups` to each generator device. `system` returns whether the generator uses the system clock, `time` calls the driver `get_time()` callback and prints seconds/nanoseconds, and write-only `enable` parses a boolean, calls the driver `enable()` callback, then updates `pps_gen->enabled`.

State/dependencies: uses device drvdata set by generator core and callback pointers supplied by each generator driver.

Risks: no locking around `enabled`; sysfs and ioctl share enable behavior and can race; missing callbacks would crash, so generator registration must provide them; `time` returns driver errors directly.

Test signals: read `system` and `time`, write valid/invalid booleans to `enable`, concurrent ioctl/sysfs enables, callback error propagation, and device removal while sysfs files are open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/generators/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/kapi.c -->
# sources/distributed-fs/ceph-client/drivers/pps/kapi.c

Purpose: exported kernel API for PPS source drivers. It registers PPS sources, unregisters them, and records timestamped assert/clear events.

Important APIs/functions: exported `pps_register_source()`, `pps_unregister_source()`, and `pps_event()`. Helpers include `pps_add_offset()` and default echo callback `pps_echo_client_default()`.

Control flow: source registration validates that defaults are supported by capabilities and that a timestamp format is advertised, allocates `pps_device`, initializes API version, params, copied source info, default echo if needed, waitqueue and spinlock, then creates the char device through `pps_register_cdev()`. `pps_event()` requires assert or clear, converts realtime timestamp, takes the device spinlock, optionally calls echo, applies configured offsets, stores assert/clear timestamps and sequence counters, sends kernel-consumer hardpps notification, wakes blocking readers, and signals fasync.

State/dependencies: per-source params, info, timestamps, sequences, waitqueue, fasync queue, and spinlock. Unregister first removes kernel consumer binding and then cdev/device state. Depends on PPS core cdev helpers and optional kernel consumer wrappers in `kc.h`.

Risks: `pps_event()` uses `BUG_ON()` for invalid event masks; echo callback runs under spinlock and must not sleep; source registration error path returns `ERR_PTR(err)` but must ensure `err` is initialized; offsets mutate a single timestamp copy reused for assert and clear when both captured.

Test signals: register invalid/default capability combinations, emit assert/clear/both events, verify sysfs and ioctl sequence updates, echo callbacks, fasync notification, kernel consumer binding, and unregister with open file descriptors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/kapi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/kc.c -->
# sources/distributed-fs/ceph-client/drivers/pps/kc.c

Purpose: optional kernel consumer bridge from PPS events to the kernel NTP `hardpps()` discipline.

Important APIs/functions: `pps_kc_bind()`, `pps_kc_remove()`, and `pps_kc_event()`.

Control flow: `PPS_KC_BIND` ioctl reaches `pps_kc_bind()`, which under a spinlock either unbinds the current device when edge is zero, binds the source if no other source is active or the same source is rebinding, or rejects competing consumers. `pps_kc_remove()` clears the binding if a source is being removed. `pps_kc_event()` checks whether the event came from the bound source and matches the selected edge mask, then calls `hardpps()` with realtime and raw timestamps.

State/dependencies: global `pps_kc_hardpps_dev` and `pps_kc_hardpps_mode` protected by `pps_kc_hardpps_lock`. Depends on `CONFIG_NTP_PPS`, timex/hardpps, and PPS core.

Risks: only one kernel consumer source can be bound system-wide; bind/unbind must not be called from interrupt context; source removal must reliably clear binding; edge validation is split between ioctl and bind function.

Test signals: bind assert and clear modes, reject second source, unbind wrong source, remove bound source, and verify `hardpps()` invocation under PPS events when `CONFIG_NTP_PPS=y`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/kc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/kc.h -->
# sources/distributed-fs/ceph-client/drivers/pps/kc.h

Purpose: private header that abstracts PPS kernel consumer support behind `CONFIG_NTP_PPS`.

Important APIs: declarations for `pps_kc_bind()`, `pps_kc_remove()`, and `pps_kc_event()` when enabled; inline stubs returning `-EOPNOTSUPP` or doing nothing otherwise.

Control flow/state: compile-time selection only. PPS core can call these helpers unconditionally, while builds without kernel PPS consumer support keep the char-device API available but reject kernel-consumer binding.

Dependencies/integration: includes `linux/pps_kernel.h` and `linux/errno.h`; included by `kapi.c`, `kc.c`, and `pps.c`.

Risks/test signals: verify non-`CONFIG_NTP_PPS` builds compile and `PPS_KC_BIND` returns `-EOPNOTSUPP`; enabled builds link to `kc.o`; source removal calls are harmless in both modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/kc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/pps.c -->
# sources/distributed-fs/ceph-client/drivers/pps/pps.c

Purpose: LinuxPPS character-device core implementing `/dev/ppsN`, RFC 2783 ioctls, polling, fasync, ID allocation, class registration, and cookie lookup.

Important APIs/functions: `pps_register_cdev()`, `pps_unregister_cdev()`, exported `pps_lookup_dev()`, `pps_cdev_ioctl()`, `pps_cdev_compat_ioctl()`, `pps_cdev_poll()`, `pps_cdev_pps_fetch()`, `pps_cdev_open()`, and `pps_cdev_release()`.

Control flow: subsystem init registers class `pps` and a dynamic major for up to `PPS_MAX_SOURCES`. Source registration allocates an idr minor, initializes device fields, registers `ppsN`, and takes a device reference for the idr. Open looks up by minor and takes a reference. `PPS_GETPARAMS`, `PPS_SETPARAMS`, `PPS_GETCAP`, `PPS_FETCH`, and `PPS_KC_BIND` implement userspace control. Fetch waits indefinitely or with a timeout until `last_ev` changes, then copies assert/clear sequence and timestamp state. Unregister clears `lookup_cookie`, destroys the device, removes the idr entry, and drops the idr reference.

State/dependencies: global `pps_idr` protected by `pps_idr_lock`, global major, class with `pps_groups`, per-device waitqueue/spinlock/fasync state managed in `kapi.c`.

Risks: `PPS_SETPARAMS` and kernel consumer bind require `CAP_SYS_TIME`; timeout conversion can truncate nanoseconds to ticks; compat fetch manually copies compat time layouts; `pps_lookup_dev()` uses RCU over idr without taking a reference and is documented for limited ldisc use; open devices can outlive unregister through device references.

Test signals: ioctl coverage including permission failures and bad modes, blocking and timed `PPS_FETCH`, poll readiness before/after fetch, compat ioctl on 32-bit userspace, fasync SIGIO, lookup-cookie user through tty ldisc, idr exhaustion, and unregister with active readers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/pps.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/sysfs.c -->
# sources/distributed-fs/ceph-client/drivers/pps/sysfs.c

Purpose: sysfs attributes for PPS source devices.

Important APIs/functions: `assert_show()`, `clear_show()`, `mode_show()`, `echo_show()`, `name_show()`, `path_show()`, `pps_attrs[]`, `pps_group`, and exported `pps_groups`.

Control flow: class registration in `pps.c` attaches `pps_groups` to every PPS device. Attribute reads print current assert/clear timestamp plus sequence when supported, static capability mode, whether echo callback exists, source name, and source path.

State/dependencies: reads per-device state from drvdata without taking `pps->lock`, so values can update concurrently with `pps_event()`. Depends on PPS core storing source info and timestamps.

Risks: uses `sprintf()` rather than `sysfs_emit()`; lockless reads can observe mixed timestamp/sequence pairs; unsupported assert/clear modes return an empty read rather than an error.

Test signals: read sysfs attributes before and after events, unsupported clear/assert mode behavior, concurrent PPS events during reads, name/path propagation from each client, and device removal while sysfs is open.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pps/sysfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/Makefile -->
# sources/distributed-fs/ceph-client/drivers/ps3/Makefile

Purpose: builds PS3 platform support drivers.

Important rules: `CONFIG_PS3_VUART` builds `ps3-vuart.o`; `CONFIG_PS3_PS3AV` builds composite `ps3av_mod.o` from `ps3av.o` and `ps3av_cmd.o`; `CONFIG_PPC_PS3` builds `sys-manager-core.o`; `CONFIG_PS3_SYS_MANAGER`, `CONFIG_PS3_STORAGE`, and `CONFIG_PS3_LPM` build their respective modules.

Control flow/state: build-only file. It ties PS3 system bus, VUART, system manager, storage, AV, and logical performance monitor objects to Kconfig symbols.

Dependencies/integration: PowerPC PS3 firmware/LV1 environment and PS3 system bus headers.

Risks/test signals: verify object inclusion for built-in vs modules, composite AV object linkage, and dependency ordering for VUART consumers such as system manager.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3-lpm.c -->
# sources/distributed-fs/ceph-client/drivers/ps3/ps3-lpm.c

Purpose: PS3 Logical Performance Monitor driver. It exposes exported APIs for Cell performance counters, trace buffer copying, signal selection, bookmarks, and LPM lifecycle through LV1 hypervisor calls.

Important APIs/types/functions: `struct ps3_lpm_priv`, exported `ps3_set_bookmark()`, `ps3_set_pm_bookmark()`, counter read/write functions, `ps3_read_pm()`, `ps3_write_pm()`, `ps3_set_signal()`, `ps3_enable_pm()`, `ps3_disable_pm()`, trace-buffer copy helpers, interrupt helpers, `ps3_lpm_open()`, and `ps3_lpm_close()`.

Control flow: probe creates a singleton `lpm_priv` from PS3 system bus LPM descriptors. Consumers call `ps3_lpm_open()` to allocate or validate a 128-byte-aligned trace cache, construct an LV1 LPM instance, and initialize shadow registers. Counter and control APIs translate Linux/Cell PM abstractions into LV1 calls, using shadow registers for write-only PM control state. Signal selection translates island/group/bus encodings before `lv1_set_lpm_signal()`. Enabling PM optionally programs start/stop bookmark triggers, starts LPM, and writes a bookmark; disabling writes a stop bookmark, stops LPM, and records trace-buffer byte count. Copy helpers pull trace data through LV1 into kernel or user buffers.

State/dependencies: singleton global `lpm_priv`, atomic open flag enforcing one active LPM instance, LV1 ids/outlet, trace cache pointers, trace byte count, and shadow registers. Depends on PS3 LV1 calls, Cell PMU definitions, timebase, and PS3 system bus.

Risks: singleton design means exported APIs `BUG_ON()` if called before probe/open; remove calls `ps3_lpm_close()` unconditionally even if not open; many invalid parameters trigger `BUG()`; trace-buffer copy loops depend on hypervisor partial-copy behavior; user-copy helper can return partial data plus error; open rollback must free internal aligned buffer and decrement atomic flag.

Test signals: PS3 firmware probe, open/close with no trace buffer and aligned/unaligned buffers, counter size modes, PM control shadows, signal-group translation, enable/disable LPM, trace copy to kernel/user, removal after active open, and LV1 error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3-lpm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3-sys-manager.c -->
# sources/distributed-fs/ceph-client/drivers/ps3/ps3-sys-manager.c

Purpose: PS3 system manager VUART client. It handles power/reset/thermal notifications and coordinates final poweroff/restart with the system policy module.

Important APIs/types/functions: message header and enums for service ids, attributes, events, commands, next operations, and wake sources; `ps3_sys_manager_write()`, send helpers for attributes/next-op/shutdown-request/response, `ps3_sys_manager_handle_msg()`, event/command handlers, final poweroff/restart routines, exported WOL getters/setters, and VUART port driver callbacks.

Control flow: probe registers platform power/restart ops, subscribes to all system-manager attributes, and starts async VUART reads for the minimum message length. VUART work handles one message then rearms async read. Message handling reads a fixed header, validates version/size/payload, dispatches external events and commands, and clears payload bytes for unhandled ids. Power/reset press events set `ps3_sm_force_power_off`, use a memory barrier, and signal ctrl-alt-del. Final poweroff/restart cancels async reads, sends next-op settings, requests shutdown, then spins handling messages until the system manager sends shutdown command and the driver acknowledges it.

State/dependencies: global `user_wake_sources` with a mutex in setter, global `ps3_sm_force_power_off`, VUART device state owned by `ps3-vuart`, and registered system-manager ops. Depends on PS3 LV1 firmware, reboot infrastructure, signal delivery, and VUART exported helpers.

Risks: many protocol assumptions use `BUG_ON()` for unexpected payload sizes or read failures; module remove is not supported; final shutdown loops never return; `ps3_sm_force_power_off` uses only barriers rather than a lock; async read minimum assumes all messages are 24 or 32 bytes.

Test signals: firmware-gated registration, attribute subscription, synthetic power/reset/thermal VUART messages, malformed header handling and RX clearing, WOL state changes, final poweroff/restart protocol, async read rearm, and interaction with VUART shutdown polling mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3-sys-manager.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3-vuart.c -->
# sources/distributed-fs/ceph-client/drivers/ps3/ps3-vuart.c

Purpose: PS3 virtual UART transport for inter-partition byte streams, primarily AV settings on port 0 and system manager on port 2. It provides exported read/write/async helpers and a wrapper driver registration model for VUART port clients.

Important APIs/types/functions: `struct ps3_vuart_port_priv`, `ps3_vuart_get_triggers()`, `ps3_vuart_set_triggers()`, interrupt enable/disable helpers, exported `ps3_vuart_write()`, `ps3_vuart_read()`, `ps3_vuart_read_async()`, `ps3_vuart_cancel_async()`, `ps3_vuart_clear_rx_bytes()`, `ps3_vuart_port_driver_register()`, and unregister. Internal `list_buffer` queues TX/RX data.

Control flow: bus init checks PS3 LV1 firmware and initializes probe mutex. A port driver registers through `ps3_vuart_port_driver_register()`, which substitutes common probe/remove/shutdown hooks. Probe obtains the shared bus interrupt, claims the port, allocates per-port state, initializes queues/work, clears stale RX, enables RX interrupts, sets triggers, then calls the client probe. Writes attempt immediate LV1 write when the TX queue is empty, queue remaining bytes, and enable TX interrupts. RX interrupts pull all waiting bytes into list buffers and schedule client work once the requested async threshold is met. Reads queue pending bytes if necessary and dequeue exactly the requested amount or return `-EAGAIN`. The shared IRQ scans a hypervisor-updated port bitmap and dispatches per-port interrupt handlers.

State/dependencies: global `vuart_bus_priv` holds the aligned port bitmap, virq, probe mutex, use count, and active port devices. Each port has interrupt mask, TX/RX list locks, async trigger, bytes-held count, and stats. Depends on PS3 LV1 VUART calls, PS3 system bus, workqueues, IRQs, and physical-to-LPAR address conversion.

Risks: several impossible states use `BUG_ON()`; disconnect handling is unimplemented and intentionally BUGs; IRQ bitmap scanning assumes nonzero status semantics; `use_count` assumes at most two users despite `PORT_COUNT` being three; queued buffer allocations in RX interrupt use `GFP_ATOMIC`; shutdown leaves polling usable for system-manager final power sequence.

Test signals: register AV/system-manager clients, shared IRQ setup/teardown across multiple ports, partial TX write queue draining, RX async threshold scheduling, polled reads returning `-EAGAIN`, stale RX clearing, shutdown polling behavior, and error paths for busy ports or unsupported firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ps3/ps3-vuart.c -->
