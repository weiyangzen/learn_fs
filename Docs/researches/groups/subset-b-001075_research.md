# subset-b-001075 Research

Grouped source research for subset B work item `subset-b-001075`. Each section is delimited for deterministic reconciliation into source-tree-aligned per-file reports.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ds1620.c -->
# sources/distributed-fs/ceph-client/drivers/char/ds1620.c

## Purpose
This is the NetWinder-specific Dallas DS1620 thermometer and fan-control character driver. It registers `/dev/temp` as a misc device, optionally exposes `/proc/therm`, reads current temperature, programs DS1620 thermostat thresholds, and controls the NetWinder fan GPIO.

## Important APIs, Types, and Functions
- `struct therm` and `CMD_*` ioctls come from `asm/therm.h`.
- `ds1620_in()` and `ds1620_out()` bit-bang command/data transactions over NetWinder GPIO/CPLD lines.
- `ds1620_read()`, `ds1620_ioctl()`, and `ds1620_unlocked_ioctl()` implement the userspace ABI.
- `ds1620_write_state()`/`ds1620_read_state()` persist threshold state into the DS1620.
- `ds1620_init()` probes `machine_is_netwinder()`, starts conversion, pulses the fan, registers the misc device, and creates `/proc/therm`.

## Control Flow
The init path resets the sensor, configures CPU continuous-conversion mode, starts conversion, briefly lowers the high threshold to force fan startup, restores saved thresholds, and registers userspace interfaces. Reads fetch `THERM_READ_TEMP`, sign-extend the 9-bit value, convert Celsius to a one-byte Fahrenheit value, and copy it to userspace. Ioctls serialize under `ds1620_mutex`, check `CAP_SYS_ADMIN` for threshold/fan writes, and route requests to threshold, temperature, status, and fan helpers.

## State and Persistence Behavior
The driver has no heap state. Durable settings are in the DS1620 threshold/config registers and fan GPIO/CPLD state. The mutex protects ioctl transactions, while `nw_gpio_lock` with IRQs disabled protects bit-banged sensor access from other NetWinder GPIO users.

## Dependencies and Integration Points
It depends on ARM NetWinder machine support, `mach/hardware.h`, `nw_gpio_*`, `nw_cpld_modify()`, miscdevice minor `TEMP_MINOR`, procfs, and the legacy therm ioctl ABI. It integrates with userspace through `/dev/temp`, `/proc/therm`, and module init/exit.

## Risks
Bit-banged timing and GPIO locking are hardware-specific and fragile outside NetWinder. The read ABI returns one byte in Fahrenheit while ioctls expose Celsius and half-degree raw values, so callers must know the legacy contract. Fan and threshold writes are privileged but still trust user-provided threshold ranges.

## Test Signals
Build with NetWinder support and `CONFIG_PROC_FS`; verify non-NetWinder returns `-ENODEV`. On hardware, read `/dev/temp`, exercise all `CMD_GET_*` ioctls, test `CMD_SET_FAN`/threshold privilege failures, and confirm `/proc/therm` displays threshold, temperature, and fan state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ds1620.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/dsp56k.c -->
# sources/distributed-fs/ceph-client/drivers/char/dsp56k.c

## Purpose
This is the Atari DSP56001 character driver. It exposes the Atari DSP host port at major `DSP56K_MAJOR`, supports upload of DSP programs via firmware-assisted bootstrap, and moves data between userspace and the DSP in 8-, 16-, 24-, or 32-bit word sizes.

## Important APIs, Types, and Functions
- Hardware access is through `dsp56k_host_interface` and Atari `sound_ym` registers.
- `struct dsp56k_device` tracks open state, max I/O burst, timeout, and selected TX/RX word sizes.
- `dsp56k_upload()` resets the DSP, loads `dsp56k/bootstrap.bin`, streams user program words, and sends the execute command.
- `dsp56k_read()` and `dsp56k_write()` use `handshake`, `tx_wait`, and `rx_wait` macros around host-port readiness bits.
- `dsp56k_ioctl()` handles `DSP56K_UPLOAD`, word-size changes, host flags, and host command writes.

## Control Flow
Module init checks Atari hardware presence, registers the char device and class device, then leaves the DSP idle. `open()` enforces exclusive use with a bit flag, resets per-open defaults, disables DSP host interrupts, and clears host flags. Reads and writes dispatch on minor 0 and the selected word size, waiting for receive/transmit readiness before copying each item. Upload reset powers the DSP down/up, writes bootstrap firmware as 24-bit words, then streams the caller's binary.

## State and Persistence Behavior
Runtime state is global and protected by `dsp56k_mutex` for open/ioctl state changes and upload. The actual DSP program persists in DSP memory until reset or power state changes. Word-size settings are per global device, reset on open, not per file descriptor beyond exclusive access.

## Dependencies and Integration Points
The driver depends on m68k Atari platform headers, firmware loader support, a platform device used only as firmware-loading context, and `asm/dsp56k.h` ioctl definitions. Userspace integrates through `/dev/dsp56k`, ioctl commands, and binary firmware `dsp56k/bootstrap.bin`.

## Risks
The `handshake` macro embeds user copies and returns from the caller, making error paths hard to audit. Some `get_user()`/`put_user()` calls inside handshake do not inspect individual copy return values. The firmware load path registers a temporary platform device and assumes the bootstrap image size is a multiple of three bytes.

## Test Signals
Compile for Atari with DSP56K present. Test exclusive open, invalid minor handling, ioctl argument validation, missing and malformed bootstrap firmware, all TX/RX word sizes, and nonblocking expectations at userspace level through controlled host-port readiness.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/dsp56k.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/dtlk.c -->
# sources/distributed-fs/ceph-client/drivers/char/dtlk.c

## Purpose
This driver supports the RC Systems DoubleTalk PC ISA speech synthesizer. It registers a dynamic character major for the legacy `DTLK_MINOR`, writes speech/control bytes to the TTS port, reads index markers from the LPC port when supported, and exposes status/interrogation ioctls.

## Important APIs, Types, and Functions
- `dtlk_read()`, `dtlk_write()`, `dtlk_poll()`, `dtlk_ioctl()`, `dtlk_open()`, and `dtlk_release()` implement the file ABI.
- `dtlk_dev_probe()` scans fixed I/O ports, claims a region, interrogates the card, initializes marker mode, and determines indexing support.
- `dtlk_interrogate()` sends the `\030\001?` command and fills `struct dtlk_settings`.
- `dtlk_read_tts()`, `dtlk_read_lpc()`, `dtlk_write_tts()`, and `dtlk_write_bytes()` perform raw port handshakes.

## Control Flow
Init registers the char driver, probes candidate ISA port pairs, requests the matching I/O region, interrogates the device, and initializes a wait queue. Writes loop until user data is sent or the device stops being writeable, yielding periodically to limit transfer rate. Reads pull LPC index markers only when indexing exists, sleeping and retrying for blocking callers. Poll registers the wait queue, samples readable/writeable status, and arms a short timer because the hardware has no interrupts.

## State and Persistence Behavior
Global state stores port addresses, indexing support, a nominal busy flag, wait queue, and timer. The card itself stores speech mode/settings changed by command bytes. `dtlk_mutex` serializes interrogation only. The comment notes `dtlk_busy` is never set, so opens are effectively not exclusive.

## Dependencies and Integration Points
It depends on x86-style I/O ports, `linux/dtlk.h`, `request_region()`, wait queues, timers, and poll. It integrates with speech software through the char device, `DTLK_INTERROGATE`, `DTLK_STATUS`, and byte-stream command writes.

## Risks
The driver is timing-sensitive and uses busy loops based on `loops_per_jiffy`. Open exclusivity appears incomplete. `dtlk_interrogate()` parses a static buffer from device bytes without strong bounds on malformed device responses. Polling depends on a timer wakeup rather than hardware interrupts.

## Test Signals
Validate registration and port-claim failures under emulated or instrumented I/O. Exercise write timeouts, nonblocking read/write behavior, poll wakeups, `DTLK_INTERROGATE` structure population, no-indexing reads returning `-EINVAL`, and cleanup releasing the claimed I/O region.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/dtlk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hangcheck-timer.c -->
# sources/distributed-fs/ceph-client/drivers/char/hangcheck-timer.c

## Purpose
`hangcheck-timer.c` implements a lightweight hang detector. It periodically schedules a kernel timer, compares actual elapsed monotonic nanoseconds against configured tick plus margin, optionally dumps task state, and optionally reboots via `emergency_restart()`.

## Important APIs, Types, and Functions
- Module parameters: `hangcheck_tick`, `hangcheck_margin`, `hangcheck_reboot`, and `hangcheck_dump_tasks`.
- Built-in boot options: `hcheck_tick`, `hcheck_margin`, `hcheck_reboot`, and `hcheck_dump_tasks`.
- `hangcheck_fire()` is the timer callback and main decision point.
- `hangcheck_init()` computes the nanosecond margin and arms `hangcheck_ticktock`.
- `hangcheck_exit()` deletes the timer synchronously.

## Control Flow
Init computes `(hangcheck_tick + hangcheck_margin) * 1e9`, records `ktime_get_ns()`, and schedules the timer for `hangcheck_tick * HZ`. Each callback computes elapsed time since the last recorded callback. If elapsed exceeds the margin, it may print SysRq task state and either reboot or log a critical warning. It then rearms the timer and records a new timestamp.

## State and Persistence Behavior
All state is in module parameters plus two global nanosecond counters. No userspace ABI or persistent storage is created. The timer state exists until module exit, where `timer_delete_sync()` prevents a callback from running after removal.

## Dependencies and Integration Points
It uses the kernel timer wheel, `ktime_get_ns()`, module parameters, `CONFIG_MAGIC_SYSRQ` task dump support, and `emergency_restart()`. It is intended for cluster fencing or systems that prefer a hard restart when scheduling stalls exceed a tolerance.

## Risks
The code is intentionally disruptive when `hangcheck_reboot` is enabled. Very large parameter values can overflow `jiffies + hangcheck_tick * HZ` or the nanosecond product. The wraparound fallback for `ktime_get_ns()` is theoretical because monotonic nanoseconds should not wrap in practical runtime.

## Test Signals
Build as module and built-in. Validate parameter parsing, timer arm/delete, warnings with reboot disabled, SysRq task dump under `CONFIG_MAGIC_SYSRQ`, and reboot path only in controlled test environments. Static tests should cover extreme tick/margin values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hangcheck-timer.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hpet.c -->
# sources/distributed-fs/ceph-client/drivers/char/hpet.c

## Purpose
This is the legacy `/dev/hpet` character driver for High Precision Event Timer comparators. It discovers HPET blocks via ACPI or platform allocation, exposes timer comparators to userspace, supports interrupt frequency programming, blocking reads/poll/fasync, optional mmap of the HPET page, and a sysctl for maximum unprivileged frequency.

## Important APIs, Types, and Functions
- `struct hpets` represents one HPET block; `struct hpet_dev` represents one comparator.
- `hpet_alloc()` registers an HPET block and initializes comparator devices.
- `hpet_open()`, `hpet_release()`, `hpet_read()`, `hpet_poll()`, `hpet_ioctl()`, `hpet_compat_ioctl()`, and `hpet_fasync()` implement `/dev/hpet`.
- `hpet_ioctl_common()` handles `HPET_IE_ON/OFF`, `HPET_INFO`, `HPET_EPI/DPI`, and `HPET_IRQFREQ`.
- `hpet_interrupt()` accounts interrupts and rearms nonperiodic comparators to emulate periodic behavior.
- `hpet_acpi_probe()` walks `_CRS` resources and calls `hpet_alloc()`.

## Control Flow
`hpet_init()` registers the misc device, `dev/hpet/max-user-freq` sysctl, and ACPI platform driver. ACPI probe maps MMIO and IRQ resources, then allocation verifies timer count, enables the main counter if needed, initializes per-comparator state, and calibrates comparator write latency. An open picks the first unused comparator. Ioctls set frequency, periodic mode, and interrupt enable. On interrupt, the handler increments pending event count, updates comparator state, wakes readers, and signals async listeners.

## State and Persistence Behavior
Global `hpets` is an append-only linked list of discovered HPETs. Per comparator state tracks open/interrupt/periodic/shared-IRQ flags, requested HPET-tick interval, pending interrupt count, IRQ assignment, wait queue, and fasync queue. `hpet_mutex` serializes ioctl/open transitions, while `hpet_lock` protects ISR-shared fields and MMIO programming. HPET hardware comparator configuration persists until release disables it.

## Dependencies and Integration Points
It depends on ACPI `PNP0103`, HPET register definitions, miscdevice minor `HPET_MINOR`, sysctl, wait queues, fasync, compat ioctl support, IRQ routing via ACPI GSI, optional `CONFIG_HPET_MMAP`, and platform code that may call exported `hpet_alloc()`.

## Risks
This exposes MMIO-backed timer programming to userspace, so frequency caps and `CAP_SYS_RESOURCE` checks are important. Shared IRQ handling depends on correct ISR bit clearing. The linked list is not removed on ACPI device removal, and mapped resources are effectively lifetime-long. Mmap is page-alignment dependent and disabled unless configured/boot-enabled.

## Test Signals
Test ACPI resource parsing, duplicate detection, comparator reservation state, open exhaustion, `HPET_IRQFREQ` privilege limits, periodic/nonperiodic interrupt delivery, read size differences under compat, fasync signals, poll readiness, release cleanup, sysctl writes, and optional `hpet_mmap=` boot behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hpet.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/Kconfig

## Purpose
This Kconfig file defines the hardware random number generator menu. It enables the common `HW_RANDOM` core and a large set of architecture, bus, firmware, and SoC-specific RNG provider drivers, plus UML random integration.

## Important APIs, Types, and Functions
- `menuconfig HW_RANDOM` gates the core `rng-core` module and `/dev/hwrng` infrastructure.
- Individual `config HW_RANDOM_*` symbols select provider drivers for Intel, AMD, Broadcom, Cavium/Marvell, CryptoCell, ARM SMCCC, Exynos, i.MX, Ingenic, Keystone, Meson, Mediatek, MPFS, JH7110, and others.
- Dependency clauses encode architecture, bus, firmware, I/O, OF, PCI, AMBA, and PM assumptions.

## Control Flow
There is no runtime control flow. Kconfig evaluation presents options under `if HW_RANDOM`, applies `depends on`, `default`, and help text rules, and emits configuration symbols consumed by the Makefile. `UML_RANDOM` sits outside the menu and selects `HW_RANDOM`.

## State and Persistence Behavior
The file persists build-time configuration state through `.config`. It does not create runtime state. Defaults often follow `HW_RANDOM` or specific architectures, making many provider modules available when the core is enabled.

## Dependencies and Integration Points
It integrates directly with `drivers/char/hw_random/Makefile`, provider source files, architecture symbols, PCI/OF/AMBA/OPTEE/IBMVIO/VIRTIO availability, and the kernel random subsystem through the selected core.

## Risks
Incorrect dependencies can expose unbuildable drivers to `COMPILE_TEST` or hide a valid provider for an SoC. Broad defaults to `HW_RANDOM` can increase build coverage and module footprint. Help text contains provider names used by users to select modules, so stale names can mislead configuration.

## Test Signals
Run `make olddefconfig`, `allmodconfig`, and targeted `COMPILE_TEST` builds for changed symbols. Verify each enabled symbol maps to an object in the Makefile and that architecture-specific providers are hidden without their required bus or firmware dependencies.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/Makefile -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/Makefile

## Purpose
This Makefile maps `CONFIG_HW_RANDOM*` symbols to the common hwrng core object and provider modules. It is the build integration point for all hardware RNG drivers in the directory.

## Important APIs, Types, and Functions
- `obj-$(CONFIG_HW_RANDOM) += rng-core.o` with `rng-core-y := core.o` builds the common framework.
- Each provider symbol appends one module object, for example `intel-rng.o`, `amd-rng.o`, `cctrng.o`, `arm_smccc_trng.o`, and `jh7110-trng.o`.
- Composite modules include `n2-rng-y := n2-drv.o n2-asm.o` and Cavium PF/VF objects under `CONFIG_HW_RANDOM_CAVIUM`.

## Control Flow
Kbuild evaluates configured symbols and builds the listed objects either built-in or as modules according to their tristate values. Composite object variables determine which source files are linked into a module.

## State and Persistence Behavior
No runtime state exists. Build state is the selected object list and module composition produced from `.config`.

## Dependencies and Integration Points
The file must stay synchronized with `Kconfig` symbol names and source filenames. It integrates with kbuild module naming, provider `MODULE_*` metadata, and the `rng-core` exported registration APIs.

## Risks
Missing or stale object mappings produce selected-but-unbuilt drivers. Composite mappings can break module linkage if one component is renamed. Object names are also visible as module filenames, so changes can affect user module-loading expectations.

## Test Signals
Run `make M=drivers/char/hw_random` with targeted symbols as built-in and modules, plus `allmodconfig`. Check that every Kconfig provider in this subset has a matching `obj-*` line and that `n2-rng` links both the C driver and assembly helper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/airoha-trng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/airoha-trng.c

## Purpose
This platform driver registers the Airoha EN7581 true RNG with the hwrng core. It enables raw data output, uses an interrupt to wait for reset/startup health checks, validates health status, and returns 32-bit raw samples.

## Important APIs, Types, and Functions
- `struct airoha_trng` stores MMIO base, `struct hwrng`, device pointer, and completion.
- `airoha_trng_init()` enables RNG, leaves software reset, waits for health-check completion, validates failure bits, and polls readiness.
- `airoha_trng_read()` polls `RAW_DATA_VALID` and reads `TRNG_RAW_DATA_OUT`.
- `airoha_trng_irq()` masks interrupts and completes startup.
- `airoha_trng_probe()` maps resources, requests IRQ, configures interrupt/raw data/reset state, and calls `devm_hwrng_register()`.

## Control Flow
Probe masks interrupts, installs the IRQ, enables reset-startup interrupts, enables raw output, places hardware in reset, and registers the hwrng. Core init then enables RNG and unresets hardware. The IRQ completion tells init that health testing completed. Reads wait up to a short timeout for raw data validity and return one word.

## State and Persistence Behavior
Driver state is devm-managed. Hardware enable/reset and interrupt mask state persist between init, reads, and cleanup. The completion is one-shot for the startup health event; cleanup disables RNG and reasserts software reset.

## Dependencies and Integration Points
It depends on OF compatible `airoha,en7581-trng`, platform MMIO, a platform IRQ, hwrng core, completions, and `readl_poll_timeout()`.

## Risks
The startup completion is not reinitialized in `init()`, so repeated init/cleanup cycles rely on completion semantics from first startup. Read ignores `wait` and always polls up to the timeout. A health-check interrupt failure leaves interrupts masked and returns `-ENODEV`.

## Test Signals
Test probe without IRQ/MMIO, startup health pass/fail bits, raw-data timeout, cleanup reset, repeated hwrng selection cycles, and entropy reads through `/dev/hwrng`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/airoha-trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/amd-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/amd-rng.c

## Purpose
This legacy driver exposes the AMD 768/76x chipset RNG through the hwrng core. It manually scans PCI IDs, maps PM I/O space, enables RNG and PM I/O bits in PCI config space, and reads 32-bit RNG data when `RNGDONE` is set.

## Important APIs, Types, and Functions
- `struct amd768_priv` holds mapped I/O base, PCI device reference, and PM base.
- `amd_rng_init()` enables RNG and PMIO PCI config bits.
- `amd_rng_cleanup()` disables the RNG bit.
- `amd_rng_read()` polls `RNGDONE`, sleeps per datasheet when waiting, and reads `RNGDATA`.
- `amd_rng_mod_init()` scans PCI, requests I/O region, maps it, and registers `amd_rng`.

## Control Flow
Module init finds a matching PCI bridge, extracts the PM base, claims the RNG PM I/O region, maps it, stores private data, and registers the hwrng. When selected, core init flips enable bits. Reads loop while space remains, waiting at most one delay budget per requested word batch. Module exit unregisters, unmaps, releases the I/O region, drops the PCI reference, and frees private state.

## State and Persistence Behavior
Global `amd_rng` holds a pointer to one allocated private structure. Hardware enable bits persist until cleanup or module unload. There is no per-device PCI driver binding, so the code intentionally avoids claiming the bridge as a PCI driver.

## Dependencies and Integration Points
It depends on x86/PCI, `HAS_IOPORT_MAP`, hwrng core, PCI config space access, and I/O port resource management. PCI IDs are exported with `MODULE_DEVICE_TABLE`.

## Risks
Manual PCI scanning supports only one device and must balance `pci_dev_put()` correctly. `amd_rng_read()` returns partial data on timeout and zero for nonblocking unavailable data. Config-space writes can affect chipset power-management behavior outside the RNG.

## Test Signals
Test no-device, zero PMBASE, busy I/O region, `ioport_map()` failure, hwrng registration failure cleanup, enable/disable config bits, blocking and nonblocking reads, and module unload resource release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/amd-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/arm_smccc_trng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/arm_smccc_trng.c

## Purpose
This driver exposes the Arm SMCCC TRNG firmware interface as an hwrng provider. It reads entropy from firmware or a higher exception level using the SMCCC TRNG calls, abstracting machine-specific hardware access.

## Important APIs, Types, and Functions
- `ARM_SMCCC_TRNG_RND` selects 64-bit or 32-bit firmware calls by architecture.
- `copy_from_registers()` copies returned entropy from SMCCC result registers.
- `smccc_trng_read()` loops over firmware calls, handling success, no-entropy, invalid parameter, and other errors.
- `smccc_trng_probe()` allocates `struct hwrng` and registers it with name `smccc_trng`.

## Control Flow
Probe creates a platform-backed hwrng. Reads request up to three result registers per SMCCC call. On success, bytes are copied from registers into the caller buffer. On `NO_ENTROPY`, nonblocking callers receive what has already been copied, while blocking callers retry up to `SMCCC_TRNG_MAX_TRIES` with `cond_resched()`.

## State and Persistence Behavior
The driver has no persistent hardware state and no init/cleanup hooks. Runtime state is limited to stack counters during reads. Firmware owns entropy source state.

## Dependencies and Integration Points
It depends on `HAVE_ARM_SMCCC_DISCOVERY`, the platform device named `smccc_trng`, `linux/arm-smccc.h`, and hwrng core registration. The platform device is typically created by SMCCC discovery code.

## Risks
Trust and liveness are delegated to firmware. A broken firmware implementation can return repeated no-entropy or bad status, yielding short reads or `-EIO`. The driver bounds retries to avoid indefinite stalls.

## Test Signals
Use SMCCC discovery/emulation to test success sizes, 32-bit vs 64-bit register packing, no-entropy retry limit, nonblocking partial returns, unexpected firmware status errors, and module alias autoloading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/arm_smccc_trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/atmel-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/atmel-rng.c

## Purpose
This platform driver registers Atmel/Microchip TRNG hardware with hwrng. It manages the peripheral clock, optional half-rate mode for high clock rates, runtime PM autosuspend, and reads one 32-bit word from `TRNG_ODATA` when data is ready.

## Important APIs, Types, and Functions
- `struct atmel_trng_data` identifies variants needing half-rate configuration.
- `struct atmel_trng` stores clock, MMIO base, hwrng, device, and variant flag.
- `atmel_trng_init()` enables the clock, programs `TRNG_MR` if needed, and enables with `TRNG_KEY`.
- `atmel_trng_read()` uses runtime PM, waits for `TRNG_ISR_DATRDY`, reads output, and re-reads ISR to avoid stale data.
- Runtime PM hooks call init/cleanup.

## Control Flow
Probe maps MMIO, gets the clock and match data, configures hwrng callbacks, enables runtime PM, and registers the provider. Reads resume the device, wait or immediately sample readiness depending on `wait`, read one word, then autosuspend. Remove and runtime suspend disable hardware.

## State and Persistence Behavior
Hardware enable and clock state are tied to runtime PM. The variant half-rate flag is immutable after probe. No software entropy buffer is kept; each read returns at most one word.

## Dependencies and Integration Points
It depends on OF compatibles `atmel,at91sam9g45-trng` and `microchip,sam9x60-trng`, platform MMIO, a clock, PM runtime, and hwrng core.

## Risks
The wait helper ignores the return value of `readl_poll_timeout()` and returns only final ready state. Probe/remove cleanup paths differ under `CONFIG_PM`; remove calls cleanup regardless and expects hardware to be accessible. Re-reading ISR is necessary to avoid duplicate data if altered.

## Test Signals
Test both compatibles, clock rate above/below 100 MHz, runtime suspend/resume, nonblocking no-data reads, data-ready polling timeout, remove cleanup, and repeated `/dev/hwrng` reads after autosuspend.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/atmel-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/ba431-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/ba431-rng.c

## Purpose
This driver supports Silex Insight BA431 TRNG IP. It resets/enables the IP, reads words from its FIFO, detects hardware error states, and schedules asynchronous reset work when errors are seen during reads.

## Important APIs, Types, and Functions
- `enum ba431_state` describes reset/startup/running/error states from the status register.
- `struct ba431_trng` stores device, MMIO base, hwrng, reset-pending flag, and reset work.
- `ba431_trng_reset()` soft-resets the IP, enables it, and polls until it leaves error/reset state.
- `ba431_trng_read()` drains FIFO words and schedules reset on empty/error conditions.
- `ba431_trng_cleanup()` disables the IP and cancels reset work.

## Control Flow
Probe maps MMIO, initializes reset work, installs hwrng callbacks, and registers. Core init runs a reset. Reads check FIFO level; if empty and in error, they schedule reset and return partial data. If waiting and not in error, they delay briefly and retry. After reading a FIFO batch, the code rechecks state before accepting those words.

## State and Persistence Behavior
The driver maintains one atomic `reset_pending` to avoid duplicate reset work. Hardware enable and softreset bits persist until cleanup. FIFO contents are transient and not buffered in software.

## Dependencies and Integration Points
It depends on OF compatible `silex-insight,ba431-rng`, platform MMIO, workqueues, hwrng core, and polling helpers.

## Risks
The final byte count calculation uses `n *= sizeof(data)`, where `data` is a pointer variable; on 64-bit this reports 8 bytes per word instead of 4. Error recovery is asynchronous, so reads may return short data while reset work is pending.

## Test Signals
Test reset success/timeout, FIFO-empty blocking/nonblocking reads, error-state reset scheduling, cleanup canceling work, and byte-count correctness on 32-bit and 64-bit builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/ba431-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/bcm2835-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/bcm2835-rng.c

## Purpose
This platform driver supports Broadcom BCM2835/BCM63xx/NSP-style RNG blocks. It handles optional clock and reset resources, optional interrupt masking for some variants, warm-up discard count programming, and FIFO-based word reads.

## Important APIs, Types, and Functions
- `struct bcm2835_rng_priv` stores hwrng, MMIO base, variant interrupt-mask flag, optional clock, and optional reset.
- `bcm2835_rng_init()` enables the clock, resets hardware, masks interrupts if needed, writes warm-up count, and enables generation.
- `bcm2835_rng_read()` waits for FIFO count in `RNG_STATUS[31:24]` and reads up to caller capacity.
- Endian-aware `rng_readl()`/`rng_writel()` use raw MMIO on big-endian MIPS variants.

## Control Flow
Probe maps the peripheral, obtains optional clock/reset, records OF variant data, sets hwrng callbacks, and registers. Core init powers the RNG and starts generation. Reads spin/yield while no words are available if blocking, then drain the available FIFO words. Cleanup disables generation and clock.

## State and Persistence Behavior
Hardware enable, warm-up count, interrupt mask, clock, and reset state persist while the hwrng is selected. No software buffer is maintained.

## Dependencies and Integration Points
It supports multiple OF compatibles and platform IDs, integrates with reset and clock frameworks, hwrng core, and architecture endian configuration.

## Risks
Blocking reads can yield repeatedly without an explicit timeout. Endian-specific raw access is necessary for BMIPS-like systems; changing it can break those variants. Warm-up count assumes hardware discards weaker early values.

## Test Signals
Test each compatible/ID, optional clock and reset absence, interrupt mask variants, big-endian MIPS accessors, FIFO empty nonblocking reads, and repeated init/cleanup through sysfs hwrng selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/bcm2835-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/bcm74110-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/bcm74110-rng.c

## Purpose
This driver exposes the Broadcom BCM74110 RNG FIFO to the hwrng core. It maps a simple host register block and reads available FIFO words with a bounded wait when blocking.

## Important APIs, Types, and Functions
- `struct bcm74110_priv` stores MMIO base.
- `bcm74110_rng_fifo_count()` reads and masks `HOST_FIFO_COUNT`.
- `bcm74110_rng_read()` waits briefly for FIFO data and drains up to `max`.
- `bcm74110_rng_probe()` maps resources, fills static hwrng name/private pointer, and registers.

## Control Flow
Probe maps the OF-described MMIO region and registers a static hwrng object. Reads loop while FIFO count is zero, returning immediately for nonblocking callers or after a small bounded retry budget for blocking callers. Once words are available, the driver reads until requested capacity or FIFO underrun.

## State and Persistence Behavior
State is minimal: a private MMIO pointer stored through the hwrng `priv` field. There is no explicit enable, reset, or cleanup sequence. FIFO state is hardware-owned.

## Dependencies and Integration Points
It depends on OF compatible `brcm,bcm74110-rng`, platform MMIO, hwrng core, and relaxed MMIO reads.

## Risks
The static `bcm74110_hwrng` object makes multiple instances unsafe because name and priv are overwritten. Blocking waits are intentionally short and may return zero even if entropy appears later.

## Test Signals
Test no-MMIO probe failure, FIFO empty blocking/nonblocking reads, FIFO underrun during drain, multiple device instances, and `/dev/hwrng` throughput under repeated reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/bcm74110-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/cavium-rng-vf.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/cavium-rng-vf.c

## Purpose
This PCI VF driver exposes Cavium ThunderX/OcteonTx RNG output through hwrng. It maps the VF result BAR, optionally maps PF health registers, checks health status before reads, and reads arbitrary byte counts from the result register.

## Important APIs, Types, and Functions
- `struct cavium_rng` stores hwrng ops, result MMIO, optional PF CSR base, PCI device, clock rate, and previous health-error timing.
- `cavium_rng_read()` calls `check_rng_health()` and reads 64-bit or byte chunks.
- `cavium_map_pf_regs()` locates/maps the PF device for health status unless running on older OcteonTx CPUs.
- `check_rng_health()` detects startup and persistent health failures using PF status and architectural timer deltas.
- `cavium_rng_probe_vf()` maps BAR0, names the hwrng, maps PF registers, and registers.

## Control Flow
VF probe allocates state, maps the result BAR, sets a device-unique hwrng name, maps PF CSRs for health checking when supported, and registers. Each read first validates health. If healthy, the read path streams as many 64-bit values as possible and handles trailing bytes from byte reads.

## State and Persistence Behavior
Per-device state is devm-managed except the PF mapping is manually unmapped on remove. `prev_error` and `prev_time` persist across reads to decide whether health failures are new/persistent. The PF driver separately enables the RNG and SR-IOV VF.

## Dependencies and Integration Points
It depends on PCI vendor/device IDs, hwrng core, ARM64 MIDR helpers, arch timer reads, and a paired Cavium RNG PF device for enabling hardware and health registers.

## Risks
The remove path unconditionally `iounmap()`s `pf_regbase`, which can be `NULL` on OcteonTx. Health timing assumes CNTVCT runs at 100 MHz in a comment, making portability sensitive. Read ignores `wait` because the register interface is always sampled directly.

## Test Signals
Test VF probe with/without PF present, older CPU model health-skip path, startup health failure, repeated health failure timing, arbitrary read sizes, and remove with `pf_regbase == NULL`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/cavium-rng-vf.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/cavium-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/cavium-rng.c

## Purpose
This PCI PF driver enables Cavium ThunderX RNG hardware and creates one SR-IOV virtual function. The companion VF driver registers the hwrng provider and reads random data.

## Important APIs, Types, and Functions
- `struct cavium_rng_pf` stores the mapped control/status register.
- `cavium_rng_probe()` maps BAR0, writes `THUNDERX_RNM_RNG_EN | THUNDERX_RNM_ENT_EN`, and enables one VF with `pci_enable_sriov()`.
- `cavium_rng_remove()` disables SR-IOV and clears the control register.
- PCI ID table matches device `0xa018`.

## Control Flow
When the PF is probed, it maps control registers, enables RNG and entropy source bits, stores driver data, and requests one VF. If SR-IOV setup fails, it disables hardware again. Remove tears down the VF first, then disables RNG hardware.

## State and Persistence Behavior
Persistent state is one MMIO control bitfield and PCI SR-IOV VF enablement. State is tied to the PF device lifecycle and does not directly register with hwrng.

## Dependencies and Integration Points
It depends on PCI, SR-IOV support, Cavium PCI IDs, and the VF driver `cavium-rng-vf.c` for actual hwrng data access.

## Risks
If SR-IOV enable fails, no hwrng provider appears even though the PF exists. The driver enables exactly one VF, so multi-consumer scaling is not attempted. Hardware remains enabled until remove or probe failure cleanup.

## Test Signals
Test PF probe, BAR mapping failure, SR-IOV unavailable/failure cleanup, VF creation and companion driver binding, and remove disabling both VF and hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/cavium-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/cctrng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/cctrng.c

## Purpose
This platform driver supports Arm CryptoCell 703/713 TRNG hardware. It configures ring oscillator sampling ratios from devicetree, collects entropy holding register data via IRQ and workqueues, buffers generated words in a circular buffer, handles runtime PM, and registers an hwrng provider with full entropy quality.

## Important APIs, Types, and Functions
- `struct cctrng_drvdata` stores platform device, MMIO base, clock, hwrng, active ROSC, sampling ratios, circular buffer, work items, pending flag, and read lock.
- `cc_trng_parse_sampling_ratio()` reads `arm,rosc-ratio`.
- `cc_trng_hw_trigger()` programs sampling, reset, debug, config, watchdog, and source enable registers.
- `cctrng_read()` copies from the circular buffer and schedules hardware refill work.
- `cc_isr()` masks RNG interrupts and schedules completion work.
- `cc_trng_compwork_handler()` validates ISR status, handles FIPS CRNGT failures, copies EHR words, changes ROSC on autocorrelation/watchdog errors, and releases PM usage.
- `cctrng_suspend()`/`cctrng_resume()` manage power-down and reset completion.

## Control Flow
Probe validates buffer constraints, allocates state, maps registers, gets IRQ and clock, initializes work and PM, takes an initial runtime PM reference, registers hwrng, and triggers the first hardware collection. The IRQ clears host causes and schedules deferred work. Completion work reads the RNG ISR, handles errors, copies six EHR words into the ring, and either starts another collection or autosuspends. Reads take a spin trylock, copy available buffered words, and schedule collection if buffer space permits.

## State and Persistence Behavior
The circular buffer persists entropy between IRQ completions and user/core reads. `pending_hw` prevents concurrent hardware operations. Runtime PM state and clock enablement persist around pending collection windows. Active ROSC advances on health-related collection errors. In FIPS mode, CRNGT error notifies and panics.

## Dependencies and Integration Points
It depends on OF compatibles `arm,cryptocell-713-trng` and `arm,cryptocell-703-trng`, `arm,rosc-ratio`, platform IRQ/MMIO, optional clock, runtime PM, hwrng core, FIPS hooks, and register definitions from `cctrng.h`.

## Risks
`cctrng_read()` ignores the `wait` parameter and returns only currently buffered bytes. `spin_trylock()` can cause short zero reads under concurrent consumers. Error handling cycles ROSCs but can stop refilling if no valid oscillator remains. FIPS CRNGT failure intentionally panics.

## Test Signals
Test missing/invalid `arm,rosc-ratio`, IRQ delivery, EHR valid path, autocorrelation/watchdog ROSC failover, zero EHR discard, concurrent reads, runtime suspend/resume, FIPS CRNGT path, and buffer wraparound.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/cctrng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/cctrng.h -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/cctrng.h

## Purpose
This header provides CryptoCell TRNG register offsets, bit shifts, masks, power constants, entropy quality, and EHR sizing used by `cctrng.c`.

## Important APIs, Types, and Functions
- `CC_TRNG_QUALITY` declares 1024 bits of entropy per 1024 bits of input.
- `CC_TRNG_NUM_OF_ROSCS`, `CC_TRNG_EHR_IN_WORDS`, and `CC_TRNG_EHR_IN_BITS` define ring oscillator and EHR geometry.
- `CC_HOST_RNG_IRQ_MASK` and `CC_RNG_INT_MASK` define interrupt routing/masking.
- Register offsets cover RNG, secure host RGF, power-down, and NVM idle status.

## Control Flow
There is no executable control flow. The C driver uses these constants to program TRNG collection, decode ISR fields through generated masks, handle host interrupts, and manage suspend/resume state.

## State and Persistence Behavior
The header creates no state. It describes MMIO layout and constants that govern persistent hardware register state controlled by `cctrng.c`.

## Dependencies and Integration Points
It depends on `linux/bitops.h` and is included only by the CryptoCell TRNG driver in this subset. The constants must match the CryptoCell 703/713 register map and driver field-extraction macros.

## Risks
Wrong offsets or bit positions can mask interrupts incorrectly, miss FIPS health failures, corrupt power state, or read the wrong EHR words. Since the values are compile-time constants, errors are only visible at runtime on hardware.

## Test Signals
Build-test `cctrng.c`, validate register writes against hardware documentation or trace logs, test interrupt mask bits, EHR word count assumptions, and suspend/resume NVM idle polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/cctrng.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/cn10k-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/cn10k-rng.c

## Purpose
This PCI driver exposes Marvell CN10K RVU RNG hardware through hwrng. It maps PF registers, checks entropy block health, optionally uses extended TRNG registers on newer revisions, and falls back to legacy random registers with zero-value mitigation.

## Important APIs, Types, and Functions
- `struct cn10k_rng` stores register base, hwrng ops, PCI device, and extended-register support flag.
- `cn10k_is_extended_trng_regs_supported()` gates extended TRNG use based on subsystem device and revision.
- `reset_rng_health_state()` issues an SMC call to reset EBG health state.
- `check_rng_health()` checks `RNM_PF_EBG_HEALTH` and resets health state when failure is detected.
- `cn10k_read_trng()` reads extended or legacy random data.
- `cn10k_rng_read()` fills caller buffers in 64-bit and trailing-byte chunks.

## Control Flow
Probe maps BAR0, names and registers the hwrng, determines revision capability, and resets health state. Reads first check health. Extended-register reads try `RNM_PF_TRNG_DAT` and status. Legacy reads use `RNM_PF_RANDOM`; if zero appears, the driver combines nonzero upper/lower halves from subsequent reads.

## State and Persistence Behavior
Driver state is per PCI device and devm-managed. Hardware health state can be reset through secure firmware. Extended-register capability is fixed at probe.

## Dependencies and Integration Points
It depends on PCI vendor `CAVIUM` device `0xA098`, MMIO, Arm SMCCC SMC services, hwrng core, and CN10K firmware support for the health reset call.

## Risks
Legacy zero mitigation can busy-loop until nonzero halves appear. Health reset failure returns `-EIO`, disabling reads. Revision filtering must stay aligned with errata for extended TRNG register availability.

## Test Signals
Test supported and unsupported revisions, SMC health reset success/failure, extended register no-status timeout, legacy zero handling, arbitrary read sizes, and PCI probe failure cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/cn10k-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/core.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/core.c

## Purpose
This is the common Linux hardware RNG core. It registers `/dev/hwrng`, manages registered `struct hwrng` providers, selects the current provider by quality or userspace choice, exposes sysfs controls, serializes reads, and runs a kernel thread that feeds hardware randomness into the kernel random subsystem.

## Important APIs, Types, and Functions
- Exported APIs: `hwrng_register()`, `hwrng_unregister()`, `devm_hwrng_register()`, `devm_hwrng_unregister()`, `hwrng_msleep()`, and `hwrng_yield()`.
- Provider selection: `set_current_rng()`, `drop_current_rng()`, `enable_best_rng()`, `get_current_rng()`, and `put_rng()`.
- Userspace ABI: `/dev/hwrng` via `rng_dev_open()` and `rng_dev_read()`.
- Sysfs attributes: `rng_current`, `rng_available`, `rng_selected`, and `rng_quality`.
- `hwrng_fillfn()` continuously reads from the current provider and calls `add_hwgenerator_randomness()`.

## Control Flow
Core init allocates cacheline-sized buffers and registers the misc device. Provider registration validates callbacks/name uniqueness, initializes list state, clamps quality, and may become current if it is the best provider and userspace has not pinned another. Setting current initializes the provider, swaps the RCU pointer, drops the old provider after synchronization, and starts the fill thread. Reads get a refcounted current provider, serialize hardware access with `reading_mutex`, refill `rng_buffer` as needed, copy to userspace, and handle nonblocking/signal cases.

## State and Persistence Behavior
Global state includes RCU `current_rng`, provider list, current user-selection flag, fill thread pointer, buffers, buffered byte count, quality values, and mutexes. Provider lifetime is protected by `kref`, RCU, cleanup work, and cleanup completion. The selected provider persists until unregistered or changed through sysfs.

## Dependencies and Integration Points
It integrates with miscdevice `/dev/hwrng`, sysfs device groups, provider drivers through `linux/hw_random.h`, kthreads, workqueues, RCU, krefs, and the kernel random subsystem.

## Risks
Provider callbacks run under `reading_mutex`, so slow hardware can stall user reads and the fill thread. Obsolete `current_quality` can still override provider quality. `rng_current_store()` accepts provider names from sysfs and can disable the current RNG with `none`, affecting entropy feeding.

## Test Signals
Test provider register/unregister ordering, duplicate names, provider init/cleanup failures, sysfs provider switching, `none` selection, quality changes, blocking/nonblocking `/dev/hwrng` reads, signal interruption, fill-thread startup/stop, and devm unregister behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/exynos-trng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/exynos-trng.c

## Purpose
This driver supports Samsung Exynos TRNG hardware through either direct MMIO registers or a secure monitor call interface. It manages clocks, runtime PM, suspend/resume behavior, and registers an hwrng provider.

## Important APIs, Types, and Functions
- `struct exynos_trng_dev` stores device, MMIO, clocks, hwrng, and feature flags.
- `exynos_trng_do_read_reg()` requests FIFO generation, polls completion, and copies FIFO registers.
- `exynos_trng_do_read_smc()` reads pairs of 32-bit words via `SMC_CMD_RANDOM`.
- `exynos_trng_init_reg()` programs clock divider, enables RNG, and disables post-processing.
- `exynos_trng_init_smc()` initializes firmware TRNG access.
- PM hooks call SMC exit/resume/init and runtime PM transitions.

## Control Flow
Probe selects MMIO or SMC callbacks from OF match data, enables runtime PM, obtains clocks, and registers hwrng. MMIO init configures the generator. SMC init asks firmware to initialize. Reads either trigger/poll the FIFO and copy up to eight words, or loop SMC calls with retry handling. Remove and suspend notify firmware for SMC variants and release runtime PM.

## State and Persistence Behavior
Clocks and runtime PM state persist while the device is active. SMC firmware owns secure TRNG state. MMIO registers hold divider, enable, post-processing, and FIFO request state.

## Dependencies and Integration Points
It depends on OF compatibles `samsung,exynos5250-trng` and `samsung,exynos850-trng`, Arm SMCCC for SMC variants, clocks `secss` and optional `pclk`, runtime PM, and hwrng core.

## Risks
`exynos_trng_do_read_smc()` writes two words per success and assumes caller `max` is sized suitably by the hwrng core. Resume error paths after acquiring runtime PM may leave usage counts elevated on SMC failures. Secure firmware availability is mandatory for Exynos850 mode.

## Test Signals
Test both compatibles, missing clocks, MMIO poll timeout, SMC retry/error statuses, suspend/resume, remove SMC exit, and `/dev/hwrng` reads with small and large sizes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/exynos-trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/geode-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/geode-rng.c

## Purpose
This legacy driver exposes the AMD Geode LX RNG to hwrng. It manually scans for the Geode AES PCI device, maps MMIO, polls the RNG status register, and reads 32-bit data words.

## Important APIs, Types, and Functions
- `struct amd_geode_priv` stores PCI reference and mapped MMIO base.
- `geode_rng_data_present()` polls `GEODE_RNG_STATUS_REG` with small delays.
- `geode_rng_data_read()` reads `GEODE_RNG_DATA_REG`.
- `geode_rng_init()` scans PCI IDs, maps BAR0, sets hwrng private data, and registers.
- `geode_rng_exit()` unregisters and frees resources.

## Control Flow
Module init finds a matching PCI device, allocates private data, maps the register window, and registers the global hwrng object. Core reads use the older `data_present`/`data_read` API. Module exit unregisters, unmaps, drops the PCI device reference, and frees private state.

## State and Persistence Behavior
Global `geode_rng` holds one private pointer. No hardware enable/disable hooks are implemented. All persistent state is the mapping and PCI reference.

## Dependencies and Integration Points
It depends on x86 PCI, Geode LX AES PCI ID, hwrng core, and MMIO mapping.

## Risks
Manual PCI scanning supports a single device and no hotplug binding. There is no explicit hardware health check beyond a nonzero status register. The older `data_read` path returns four bytes whenever called.

## Test Signals
Test no-device, zero BAR, ioremap failure, hwrng registration failure cleanup, status polling, and module unload resource balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/geode-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/hisi-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/hisi-rng.c

## Purpose
This driver supports HiSilicon Hip04/Hip05 RNG hardware. It seeds the generator from kernel randomness, optionally selects ring-oscillator seed reload, enables generation, and returns one 32-bit random number per read.

## Important APIs, Types, and Functions
- `seed_sel` module parameter selects LFSR or ring-oscillator seed reload.
- `struct hisi_rng` stores MMIO base and hwrng.
- `hisi_rng_init()` writes `RNG_SEED` and enables `RNG_CTRL` bits.
- `hisi_rng_cleanup()` disables the RNG.
- `hisi_rng_read()` reads `RNG_RAN_NUM`.

## Control Flow
Probe maps MMIO, fills callbacks, and registers devm hwrng. Core init seeds and enables the hardware. Reads directly return one word. Cleanup clears control bits.

## State and Persistence Behavior
The selected seed mode is global module state. Hardware seed and control bits persist while selected. There is no readiness polling or software buffer.

## Dependencies and Integration Points
It depends on OF compatibles `hisilicon,hip04-rng` and `hisilicon,hip05-rng`, platform MMIO, hwrng core, and `get_random_bytes()` for initial seed.

## Risks
Reads do not check readiness or health status, so correctness depends on hardware always having valid output after enable. The module parameter is global across possible instances.

## Test Signals
Test both compatibles, seed parameter modes, init/cleanup register writes, repeated reads, and probe resource failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/hisi-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/histb-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/histb-rng.c

## Purpose
This driver supports HiSilicon STB RNG hardware. It configures source, post-processing, drop mode, and post-processing depth, exposes the depth as a sysfs attribute, and reads available RNG words.

## Important APIs, Types, and Functions
- `struct histb_rng_priv` stores hwrng and MMIO base.
- `histb_rng_init()` programs source and post-processing depth.
- `histb_rng_wait()` polls `RNG_STAT.DATA_COUNT`.
- `histb_rng_read()` reads `RNG_NUMBER` for each requested word.
- `depth_show()`/`depth_store()` expose and reprogram depth.

## Control Flow
Probe maps MMIO, initializes depth to 144, waits for the first value, registers hwrng, and installs device groups. Reads check data count for each word, optionally wait up to 30 ms, and return partial bytes or timeout. Sysfs writes parse a depth and reinitialize the control register.

## State and Persistence Behavior
The programmed depth persists in the control register and can be changed at runtime. No software buffer exists. Driver data is stored on both platform and device.

## Dependencies and Integration Points
It depends on OF compatible `hisilicon,histb-rng`, hwrng core, platform MMIO, sysfs attribute groups, and relaxed polling helpers.

## Risks
`histb_rng_read()` increments by four bytes but tests `i < max`, so unaligned `max` values can write a full `u32` past the intended size; the core normally asks aligned buffer sizes but the provider is not defensive. Depth writes are not synchronized with concurrent reads.

## Test Signals
Test initial bring-up timeout, sysfs depth show/store, blocking and nonblocking reads, unaligned max handling in provider-level tests, and repeated depth changes while reading.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/histb-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/imx-rngc.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/imx-rngc.c

## Purpose
This driver supports Freescale i.MX RNGC/RNGB hardware. It validates the RNG type, optionally runs self-test, seeds the generator with interrupt completion, enables automatic reseeding, reads FIFO words, and manages clocks through runtime PM.

## Important APIs, Types, and Functions
- `struct imx_rngc` stores device, clock, MMIO base, hwrng, operation completion, and error register snapshot.
- `imx_rngc_irq_mask_clear()` and `imx_rngc_irq_unmask()` manage done/error interrupts and clear status.
- `imx_rngc_self_test()` runs hardware self-test.
- `imx_rngc_init()` clears errors, seeds repeatedly until statistical errors stop, enables auto-seed, and leaves interrupts unmasked.
- `imx_rngc_read()` drains FIFO words under runtime PM.
- `imx_rngc_irq()` snapshots status/error, masks/clears, and completes seed/self-test events.

## Control Flow
Probe maps MMIO, enables clock, verifies version type, initializes completion, masks interrupts, requests IRQ, optionally self-tests, enables runtime PM, and registers hwrng. Core init performs seed creation and auto-seed setup. Reads resume the device, pull FIFO words until empty/error, and autosuspend.

## State and Persistence Behavior
`err_reg` stores the last interrupt error while interrupts are masked. Hardware seed and auto-seed configuration persist while selected. Clock state is runtime-PM controlled.

## Dependencies and Integration Points
It depends on OF compatible `fsl,imx25-rngb`, platform IRQ/MMIO, clocks, runtime PM, hwrng core, and module parameter `self_test`.

## Risks
The read path returns `-EIO` when no word is available even if `wait` is false. Init loops on statistical seed errors and can timeout. Correct interrupt masking is critical because clearing interrupts can also clear error information.

## Test Signals
Test unsupported RNG type, self-test pass/fail/timeout, seed statistical retry, FIFO empty/error reads, runtime suspend/resume, IRQ completion, and cleanup masking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/imx-rngc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/ingenic-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/ingenic-rng.c

## Purpose
This platform driver supports Ingenic JZ4780 and X1000 RNG blocks. It enables the generator, handles version-specific readiness behavior, and returns one 32-bit word per hwrng read.

## Important APIs, Types, and Functions
- `enum ingenic_rng_version` distinguishes `ID_JZ4780` and `ID_X1000`.
- `struct ingenic_rng` stores version, MMIO base, and hwrng.
- `ingenic_rng_init()` enables `ERNG_ENABLE`.
- `ingenic_rng_read()` polls `ERNG_READY` on X1000+ or delays 20 usec on JZ4780, then reads `RNG_REG_RNG_OFFSET`.
- `ingenic_rng_remove()` manually unregisters and disables the device.

## Control Flow
Probe maps MMIO, reads match data, fills callbacks, manually registers hwrng, and stores driver data. Core init enables the generator. Reads apply variant-specific readiness handling and return one word. Remove unregisters and clears the enable register.

## State and Persistence Behavior
Variant selection is fixed at probe. Hardware enable state persists until cleanup/remove. No software buffering exists.

## Dependencies and Integration Points
It depends on OF compatibles `ingenic,jz4780-rng` and `ingenic,x1000-rng`, platform MMIO, hwrng core, and polling helpers.

## Risks
Manual `hwrng_register()` requires remove-time balancing. The JZ4780 delay is empirical to avoid shifted repeat data. The X1000 polling path always waits and does not honor nonblocking `wait`.

## Test Signals
Test both variants, timeout on X1000 readiness, JZ4780 continuous-read delay behavior, register/unregister balancing, and init/cleanup enable writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/ingenic-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/ingenic-trng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/ingenic-trng.c

## Purpose
This driver supports the Ingenic X1830 DTRNG true random number generator. It enables the generator through a config bit, waits for data-ready status, and returns one 32-bit word.

## Important APIs, Types, and Functions
- `struct ingenic_trng` stores MMIO base and hwrng.
- `ingenic_trng_init()` sets `CFG_GEN_EN`.
- `ingenic_trng_cleanup()` clears `CFG_GEN_EN`.
- `ingenic_trng_read()` polls `STATUS_RANDOM_RDY` and reads `TRNG_REG_RANDOMNUM_OFFSET`.
- `ingenic_trng_probe()` maps registers, enables the clock, and registers devm hwrng.

## Control Flow
Probe maps MMIO, obtains/enables the clock, configures callbacks, and registers. Core init enables generation. Reads wait up to 1 ms for ready status and return one word. Cleanup clears the enable bit.

## State and Persistence Behavior
Hardware generation state persists while enabled; the clock is devm-enabled for device lifetime. No software buffer exists.

## Dependencies and Integration Points
It depends on OF compatible `ingenic,x1830-dtrng`, platform MMIO, a clock, hwrng core, and polling helpers.

## Risks
Read ignores nonblocking `wait` and always polls. The clock remains enabled for the platform device lifetime rather than runtime PM. Timeout returns an error instead of partial data.

## Test Signals
Test clock and MMIO probe failures, init/cleanup toggling, ready timeout, successful reads, and repeated hwrng provider selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/ingenic-trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/intel-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/intel-rng.c

## Purpose
This legacy driver exposes Intel 82802/i8xx firmware-hub RNG hardware. It verifies firmware hub presence using temporary FWH read-ID cycles under `stop_machine()`, maps the magic RNG address, enables the RNG, and reads one byte at a time through the hwrng core.

## Important APIs, Types, and Functions
- `intel_rng_data_present()` polls the RNG status data-present bit.
- `intel_rng_data_read()` reads one byte from `INTEL_RNG_DATA`.
- `intel_rng_init()` enables the RNG hardware status bit.
- `intel_rng_cleanup()` disables it.
- `struct intel_rng_hw` captures PCI config registers and temporary FWH mapping for detection.
- `intel_rng_hw_init()` runs under `stop_machine()` to switch FWH to read-ID mode and restore config.
- `intel_rng_mod_init()` scans supported PCI IDs, performs FWH detection unless disabled, maps RNG registers, and registers hwrng.

## Control Flow
Module init finds a known Intel LPC bridge. Unless `no_fwh_detect` skips detection, it reads/possibly modifies BIOS/FWH decode config, maps FWH space, stops the machine, issues read-ID commands, restores state, and verifies manufacturer/device IDs. It then maps the RNG magic address, checks present bit, and registers the hwrng. Core init enables RNG. Reads use the legacy present/read callbacks. Exit unregisters and unmaps.

## State and Persistence Behavior
Global `intel_rng` holds the RNG MMIO pointer. Hardware enable status persists while selected. Detection temporarily modifies PCI config and FWH command state but restores them before returning.

## Dependencies and Integration Points
It depends on x86 PCI bridge IDs, fixed legacy MMIO addresses, `stop_machine()`, hwrng core, and module parameter `no_fwh_detect`.

## Risks
FWH detection manipulates firmware address space and must run with the system stopped; bad restoration can affect firmware flash access. Locked BIOS control can block safe detection. Reads provide only one byte per callback, limiting throughput.

## Test Signals
Test `no_fwh_detect` modes, locked firmware-space behavior, FWH ID success/failure, RNG-present bit failure, enable/disable status bits, registration cleanup paths, and module unload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/intel-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/iproc-rng200.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/iproc-rng200.c

## Purpose
This platform driver supports Broadcom iProc/STB RNG200 hardware. It enables the random bit generator, detects NIST/master-fail lockout status, resets hardware on failure, drains FIFO data, and supports system sleep suspend/resume.

## Important APIs, Types, and Functions
- `struct iproc_rng200_dev` stores hwrng and MMIO base.
- `iproc_rng200_enable_set()` toggles the generator enable field.
- `iproc_rng200_restart()` disables, clears status, resets RNG/RBG blocks, and re-enables.
- `iproc_rng200_read()` drains FIFO words/partial words with bounded idle wait and at most one reset per read.
- `iproc_rng200_init()` and `iproc_rng200_cleanup()` enable/disable hardware.

## Control Flow
Probe maps MMIO, stores driver data, sets hwrng callbacks, and registers. Reads loop until requested bytes are filled or a one-second idle timeout expires. On health failure status, the driver restarts hardware once and continues. If FIFO has data, it copies full or partial words; otherwise it returns immediately for nonblocking callers or sleeps briefly.

## State and Persistence Behavior
Hardware enable/reset/status state persists until cleanup or suspend. There is no software buffer. Suspend disables the generator and resume re-enables it.

## Dependencies and Integration Points
It depends on OF compatibles for BCM2711/7211/7278/iProc RNG200, platform MMIO, hwrng core, and system sleep PM.

## Risks
One reset per read prevents endless reset loops but can return short reads after repeated hardware failures. The wait sleep upper bound is fixed at 500 usec while idle timeout is jiffies based. Health status clearing is broad (`0xffffffff`).

## Test Signals
Test FIFO full and empty paths, partial final word copies, health failure/reset path, nonblocking returns, idle timeout, suspend/resume, and probe MMIO failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/iproc-rng200.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/ixp4xx-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/ixp4xx-rng.c

## Purpose
This small driver exposes the Intel IXP45x/46x NPU pseudo-random generator through hwrng. It maps the RNG register and returns one raw 32-bit value per read.

## Important APIs, Types, and Functions
- `ixp4xx_rng_data_read()` reads a 32-bit value from the mapped base address.
- Static `ixp4xx_rng_ops` registers the legacy `data_read` callback.
- `ixp4xx_rng_probe()` verifies `cpu_is_ixp46x()`, maps MMIO, stores the base in `priv`, and registers devm hwrng.

## Control Flow
Platform probe rejects non-IXP46x CPUs, maps the resource, and registers the hwrng. The core treats data as always present because only `data_read` is supplied. Each read returns four bytes.

## State and Persistence Behavior
State is a static hwrng object with one `priv` MMIO pointer. There is no enable, cleanup, or software buffer.

## Dependencies and Integration Points
It depends on OF compatible `intel,ixp46x-rng`, IXP4xx CPU detection helpers, platform MMIO, and hwrng core.

## Risks
The static hwrng object is not multi-instance safe. The generator is pseudo-random and has no readiness or health check in this driver. Probe is gated by CPU family even if devicetree matches.

## Test Signals
Test CPU family rejection, MMIO mapping failure, one-word reads, devm unregister, and static-object behavior if multiple platform devices are described.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/ixp4xx-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/jh7110-trng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/jh7110-trng.c

## Purpose
This driver supports the StarFive JH7110 TRNG. It manages clocks, reset, IRQ completions for random/reseed events, auto-reseed parameters, runtime PM, and reads 128- or 256-bit random blocks.

## Important APIs, Types, and Functions
- `struct starfive_trng` stores device, MMIO, clocks, reset, hwrng, completions, mode/reseed settings, and a spinlock for control writes.
- Module parameters `autoreq` and `autoage` configure automatic reseeding thresholds.
- `starfive_trng_init()` programs auto-reseed, interrupts, mode, and performs initial reseed.
- `starfive_trng_cmd()` writes commands and waits for completion.
- `starfive_trng_irq()` completes random/reseed events and triggers reseed on LFSR lockup.
- `starfive_trng_read()` waits idle, generates random data, and copies result registers.

## Control Flow
Probe maps resources, requests IRQ, gets clocks/reset, enables hardware, initializes runtime PM, and registers hwrng. Core init enables interrupts, programs 256-bit mode by default, and reseeds. Reads resume runtime PM, cap maximum length by mode, optionally wait for idle, issue generate command, copy registers, and autosuspend.

## State and Persistence Behavior
Mode, mission, reseed, autoage, and autoreq persist in software/registers. Completions synchronize IRQ-driven command completion. Runtime PM controls clocks; cleanup asserts reset and disables clocks.

## Dependencies and Integration Points
It depends on OF compatible `starfive,jh7110-trng`, platform IRQ/MMIO, clocks `hclk` and `ahb`, reset controller, runtime PM, and hwrng core.

## Risks
`starfive_trng_read()` returns early on errors without putting the runtime PM reference, which can leak PM usage. IRQ handler writes reseed command on LFSR lockup without reinitializing completion. Module parameters are global rather than per device.

## Test Signals
Test initial reseed timeout, random generation timeout with `wait` false/true, PM reference balancing on error paths, LFSR lockup IRQ, suspend/resume, clock/reset failures, and 128/256-bit mode behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/jh7110-trng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/ks-sa-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/ks-sa-rng.c

## Purpose
This driver exposes the TI Keystone NETCP Security Accelerator TRNG. It enables the SA module through syscon, configures TRNG sampling/refill cycles, tracks expected readiness timestamps, and returns 64-bit output through legacy hwrng callbacks.

## Important APIs, Types, and Functions
- `struct trng_regs` maps output, status, interrupt, control, and config registers.
- `struct ks_sa_rng` stores hwrng, clock, syscon regmap, MMIO registers, readiness timestamp, and refill delay.
- `cycles_to_ns()`, `startup_delay_ns()`, and `refill_delay_ns()` derive timing from clock rate.
- `ks_sa_rng_init()` enables/configures hardware and computes delays.
- `ks_sa_rng_data_present()` waits until expected ready time and polls status.
- `ks_sa_rng_data_read()` reads low/high output, acknowledges ready, and updates next ready time.

## Control Flow
Probe maps TRNG registers, obtains the syscon regmap and clock, enables runtime PM/power domain, and registers hwrng. Core init enables SA TRNG and programs timing. The hwrng core first calls `data_present`; when ready, `data_read` returns two words and acknowledges the interrupt/status.

## State and Persistence Behavior
`ready_ts` and `refill_delay_ns` persist across reads to avoid polling before hardware can refill. Hardware enable/config registers persist until cleanup. Runtime PM is enabled at probe and released on remove.

## Dependencies and Integration Points
It depends on OF compatible `ti,keystone-rng`, `ti,syscon-sa-cfg` phandle, regmap, platform MMIO, clocks, runtime PM, and hwrng core.

## Risks
Timing constants are hard-coded defaults, so hardware characterization changes require code updates. The remove path only handles PM; hwrng cleanup disables hardware when the core unregisters. `data_present` truncates nanosecond delta to `u32` for sleep calculation.

## Test Signals
Test missing syscon/clock/MMIO, startup and refill delays at different clock rates, status-ready polling, output ack, runtime PM enable/disable, and repeated reads under high demand.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/ks-sa-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/meson-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/meson-rng.c

## Purpose
This driver supports Amlogic Meson RNG blocks, including the older direct-data register variant and the S4 variant that requires seed/run status polling.

## Important APIs, Types, and Functions
- `struct meson_rng_priv` supplies a variant read callback.
- `struct meson_rng_data` stores MMIO base, hwrng, and device.
- `meson_rng_read()` reads one word from `RNG_DATA`.
- `meson_s4_rng_read()` clears seed-ready status, waits for seed and run bits to clear, then reads `RNG_S4_DATA`.
- `meson_rng_probe()` maps MMIO, enables optional `core` clock, selects variant data, and registers hwrng.

## Control Flow
Probe gets match data and resources, sets the hwrng read callback, and registers. Old Meson reads return one word immediately. S4 reads perform two atomic poll loops around the config register before reading data.

## State and Persistence Behavior
The selected read callback is fixed at probe. Optional clock is devm-enabled for device lifetime. Hardware status bits are manipulated per S4 read.

## Dependencies and Integration Points
It depends on OF compatibles `amlogic,meson-rng` and `amlogic,meson-s4-rng`, optional `core` clock, platform MMIO, and hwrng core.

## Risks
The older variant has no readiness or health check. S4 polling ignores the `wait` argument and returns `-EBUSY` on timeout. Only one word is returned regardless of larger buffer requests.

## Test Signals
Test both compatibles, missing match data, optional clock failure, S4 seed/run timeout, and repeated reads through `/dev/hwrng`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/meson-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/mpfs-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/mpfs-rng.c

## Purpose
This driver exposes the Microchip PolarFire SoC system-controller RNG service through hwrng. It sends mailbox transactions to the MSS system controller and copies 32-byte responses into the hwrng buffer.

## Important APIs, Types, and Functions
- `struct mpfs_rng` stores the system-controller handle and hwrng.
- `mpfs_rng_read()` builds `mpfs_mss_msg`/`mpfs_mss_response`, calls `mpfs_blocking_transaction()`, and copies response bytes.
- `mpfs_rng_probe()` obtains the system controller and registers hwrng.

## Control Flow
Probe allocates state, gets the MPFS system-controller handle, sets read/name callbacks, and registers. Reads repeatedly issue command opcode `0x21` until `max` bytes are filled, unless `wait` is false, in which case a single response is copied.

## State and Persistence Behavior
The driver has no local hardware state; the system controller owns RNG state. Stack response buffers are copied to callers and discarded. The system-controller pointer persists for device lifetime.

## Dependencies and Integration Points
It depends on `POLARFIRE_SOC_SYS_CTRL`, `soc/microchip/mpfs.h`, platform device registration, and hwrng core.

## Risks
All entropy and blocking behavior depend on system-controller firmware. `buf + count` uses void-pointer arithmetic, accepted by GNU C but nonstandard. Transaction errors abort reads even after prior successful chunks in the same call.

## Test Signals
Test missing controller, transaction failure, blocking multi-response reads, nonblocking single-response reads, partial final copy sizes, and module unload through devm.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/mpfs-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/mtk-rng.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/mtk-rng.c

## Purpose
This driver supports Mediatek hardware RNG blocks. It controls the `rng` clock, enables/disables the generator, waits for readiness, returns 32-bit words, and uses runtime PM autosuspend when available.

## Important APIs, Types, and Functions
- `struct mtk_rng` stores MMIO base, clock, hwrng, and device.
- `mtk_rng_init()` enables the clock and sets `RNG_EN`.
- `mtk_rng_cleanup()` clears `RNG_EN` and disables the clock.
- `mtk_rng_wait_ready()` checks/polls `RNG_READY`.
- `mtk_rng_read()` resumes runtime PM, loops over ready words, and autosuspends.
- Runtime PM hooks call init/cleanup under `CONFIG_PM`.

## Control Flow
Probe allocates state, gets clock and MMIO, registers hwrng, stores driver data, and enables runtime PM. Reads resume the device, read available words while ready, and schedule autosuspend. Without PM, hwrng init/cleanup directly manage hardware.

## State and Persistence Behavior
Hardware enable and clock state are runtime-PM controlled. Quality is set to 900. No software buffer is kept.

## Dependencies and Integration Points
It depends on OF compatibles `mediatek,mt7986-rng` and `mediatek,mt7623-rng`, clock named `rng`, platform MMIO, runtime PM, and hwrng core.

## Risks
`pm_runtime_get_sync()` return value is ignored in read, which can lead to MMIO access after resume failure. Atomic polling always happens when requested by `wait`; timeout returns `-EIO` only if no data was read and wait was true.

## Test Signals
Test clock/MMIO failures, runtime PM resume failure, ready timeout, partial reads, PM autosuspend/resume, non-PM builds, and quality-based provider selection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/mtk-rng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/mxc-rnga.c -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/mxc-rnga.c

## Purpose
This driver supports Freescale i.MX RNGA hardware. It wakes and starts the generator, checks oscillator health, exposes FIFO-level readiness through legacy hwrng callbacks, and reads one word from the output FIFO.

## Important APIs, Types, and Functions
- `struct mxc_rng` stores device, hwrng, MMIO base, and clock.
- `mxc_rnga_init()` clears sleep, checks `RNGA_STATUS_OSC_DEAD`, and sets `RNGA_CONTROL_GO`.
- `mxc_rnga_data_present()` polls FIFO level in `RNGA_STATUS`.
- `mxc_rnga_data_read()` reads `RNGA_OUTPUT_FIFO`, checks error interrupt, and clears errors.
- `mxc_rnga_probe()` gets the clock, maps MMIO, and manually registers hwrng.

## Control Flow
Probe allocates state, enables the RNG clock, maps registers, and registers. Core init starts the generator after oscillator check. The core uses `data_present` before `data_read`; reads consume a FIFO word and suppress it if an error interrupt is detected. Cleanup clears the GO bit. Remove unregisters the hwrng.

## State and Persistence Behavior
Hardware control state persists while selected. Clock is devm-enabled for device lifetime. There is no software buffer. Manual registration requires remove-time unregister.

## Dependencies and Integration Points
It depends on OF compatibles `fsl,imx21-rnga` and `fsl,imx31-rnga`, platform MMIO, a clock, and hwrng core.

## Risks
`mxc_rnga_probe()` never calls `platform_set_drvdata()`, so `mxc_rnga_remove()` retrieves `NULL` and cannot safely unregister on remove. Error interrupts cause `data_read()` to return zero after already reading the FIFO word. The driver uses raw MMIO accessors.

## Test Signals
Test oscillator-dead init failure, FIFO empty/present polling, error interrupt clearing, remove path driver-data bug, clock/MMIO failures, and manual hwrng unregister.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/mxc-rnga.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/n2-asm.S -->
# sources/distributed-fs/ceph-client/drivers/char/hw_random/n2-asm.S

## Purpose
This SPARC64 assembly file provides low-level Niagara2 RNG hypervisor call wrappers used by the `n2-rng` driver. It invokes fast traps for diagnostic control, control register reads/writes, and random data reads.

## Important APIs, Types, and Functions
- Exported entry points include `sun4v_rng_get_diag_ctl`, `sun4v_rng_ctl_read_v1`, `sun4v_rng_ctl_read_v2`, `sun4v_rng_ctl_write_v1`, `sun4v_rng_ctl_write_v2`, `sun4v_rng_data_read_diag_v1`, `sun4v_rng_data_read_diag_v2`, and `sun4v_rng_data_read`.
- Hypervisor opcodes come from `asm/hypervisor.h`, such as `HV_FAST_RNG_CTL_READ` and `HV_FAST_RNG_DATA_READ`.
- Linkage macros `ENTRY` and `ENDPROC` provide callable kernel symbols.

## Control Flow
Each wrapper places the proper hypervisor function number in `%o5`, arranges argument or output-pointer registers for ABI version differences, executes `ta HV_FAST_TRAP`, stores returned output registers to caller-provided addresses when needed, and returns the hypervisor status in the return register.

## State and Persistence Behavior
The assembly maintains no state. Any persistent state is in the hypervisor RNG facility and in memory locations supplied by the C caller for returned values.

## Dependencies and Integration Points
It depends on SPARC64 Sun4v hypervisor ABI, `n2rng.h`, Linux linkage macros, and the composite `n2-rng` module built by the Makefile.

## Risks
Register calling convention mismatches would corrupt outputs or return status. Version-specific wrappers store different numbers of return registers, so the C driver must call the correct symbol for the negotiated hypervisor RNG API.

## Test Signals
Build on SPARC64, verify symbols link with `n2-drv.o`, test hypervisor API v1/v2 paths, validate returned status propagation, and exercise diagnostic/data reads under a Sun4v environment.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/hw_random/n2-asm.S -->
