# subset-b-005169 grouped research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_vmw.c -->
# sources/distributed-fs/ceph-client/drivers/ptp/ptp_vmw.c

Purpose: implements a read-only PTP hardware clock for VMware's ACPI-advertised precision clock virtual device. It exposes the guest-visible VMware precision clock as a Linux `ptp_clock` named `ptp_vmw`, allowing time consumers to read a hypervisor supplied nanosecond counter.

Important APIs/types/functions: `ptp_vmw_pclk_read()` issues `vmware_hypercall3(VMWARE_CMD_PCLK_GETTIME)` and assembles a 64-bit nanosecond value from high/low words. `ptp_vmw_gettime()` converts that value with `ns_to_timespec64()`. The `ptp_clock_info` table implements only `.gettime64`; `.adjtime`, `.adjfine`, `.settime64`, and `.enable` all return `-EOPNOTSUPP`. `ptp_vmw_acpi_probe()` registers the PTP clock and the ACPI match table binds `VMW0005`.

Control flow: module init refuses to load unless `x86_hyper_type` reports VMware, then registers a platform driver. ACPI/platform probing registers the PTP clock and stores the ACPI companion pointer. Runtime reads go directly through the VMware hypercall. Removal unregisters the PTP clock; module exit unregisters the platform driver.

State and persistence: state is limited to two module globals, the ACPI device pointer and registered `ptp_clock`. There is no persistent configuration, no clock adjustment state, and no suspend/resume handling in this file.

Dependencies and integration: depends on x86 VMware hypervisor detection, VMware hypercall ABI, ACPI platform matching, and the PTP clock framework. It integrates as a virtual device, not as Ceph/distributed-storage logic despite its source-tree location.

Risks and test signals: the driver trusts the hypervisor command ABI and maps any nonzero hypercall return to `-EIO`. It cannot discipline or set time, so consumers must tolerate read-only PTP behavior. Test signals are VMware guest boot with `VMW0005`, `/dev/ptp*` registration, successful `PTP_CLOCK_GETTIME`, graceful absence on non-VMware hosts, and unregister behavior on device removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ptp/ptp_vmw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/pwm/Kconfig

Purpose: defines the Linux PWM subsystem configuration menu and every controller-driver build symbol under `drivers/pwm`. It gates the generic PWM core, debug checks, optional PWM-as-GPIO support, C and Rust controller drivers, and per-platform dependencies.

Important APIs/types/functions: Kconfig symbols include `PWM`, `PWM_DEBUG`, `PWM_PROVIDE_GPIO`, all hardware driver symbols such as `PWM_AB8500`, `PWM_AIROHA`, `PWM_AXI_PWMGEN`, `PWM_DWC`, `PWM_CROS_EC`, and the internal `RUST_PWM_ABSTRACTIONS`. Dependency clauses bind drivers to subsystems including `HAS_IOMEM`, `COMMON_CLK`, `OF`, `ACPI`, `PCI`, `I2C`, `SPI`, `REGMAP_MMIO`, MFD parents, architecture families, and `COMPILE_TEST`.

Control flow: there is no runtime control flow. At configuration time `menuconfig PWM` enables the subtree, and each `tristate` determines whether a driver is built in, built as a module, or omitted. `select` clauses pull shared helpers such as `PWM_DWC_CORE`, `PWM_LPSS`, `REGMAP_MMIO`, or Rust abstractions.

State and persistence: state is the generated kernel `.config` and resulting Kbuild graph. Defaults are mostly explicit architecture defaults or unset symbols; no runtime state is created here.

Dependencies and integration: this is the build-time integration point between the PWM framework core, controller drivers, and platform subsystems. It must stay synchronized with `drivers/pwm/Makefile` object names and each driver's include/runtime dependencies.

Risks and test signals: missing dependencies surface as randconfig/allmodconfig build failures; overbroad dependencies can expose drivers on unsupported platforms. Test signals include `allmodconfig`, `allyesconfig`, `randconfig`, dependency-disabled configs, module/built-in combinations, and checks that selected internal symbols such as `PWM_DWC_CORE` and `PWM_LPSS` link correctly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/Makefile -->
# sources/distributed-fs/ceph-client/drivers/pwm/Makefile

Purpose: maps PWM Kconfig symbols to Kbuild objects for the generic PWM core and all controller drivers in `drivers/pwm`.

Important APIs/types/functions: `obj-$(CONFIG_PWM) += core.o` builds the framework core. Per-driver entries map symbols such as `CONFIG_PWM_AB8500`, `CONFIG_PWM_AXI_PWMGEN`, `CONFIG_PWM_DWC_CORE`, `CONFIG_PWM_DWC`, and `CONFIG_PWM_EP93XX` to their corresponding `.o` files. The file also includes newer entries such as `pwm_th1520.o`.

Control flow: there is no runtime flow. Kbuild evaluates each `obj-$(CONFIG_...)` assignment after Kconfig resolution and compiles/link-selects objects or modules.

State and persistence: state is build output only. This file does not own runtime data and does not persist configuration beyond the generated build graph.

Dependencies and integration: integrates with the adjacent `Kconfig`; every object here assumes its dependency set is sufficient. Shared-core split drivers rely on correct object selection, for example `PWM_DWC` selecting and building `pwm-dwc-core.o`.

Risks and test signals: object-name drift, missing new driver entries, stale entries, or mismatches with Kconfig module names cause compile or link failures. Test signals are clean builds for modular and built-in PWM configurations, plus targeted builds of split drivers like DWC and LPSS.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/core.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/core.c

Purpose: implements the generic Linux PWM framework. It registers PWM chips, arbitrates PWM device requests, applies and reads PWM state, supports the newer waveform API, exposes sysfs and character-device userspace interfaces, provides optional GPIO emulation, and publishes debugfs state.

Important APIs/types/functions: global `pwm_chips` and `pwm_lock` track registered chips. Public exports include `pwm_apply_might_sleep()`, `pwm_apply_atomic()`, `pwm_get_state_hw()`, `pwm_adjust_config()`, `pwm_get()`, `pwm_put()`, `devm_pwm_get()`, `devm_fwnode_pwm_get()`, `pwmchip_alloc()`, `devm_pwmchip_alloc()`, `__pwmchip_add()`, `pwmchip_remove()`, `pwm_add_table()`, and waveform helpers `pwm_round_waveform_might_sleep()`, `pwm_get_waveform_might_sleep()`, and `pwm_set_waveform_might_sleep()`. Internal `pwm_export` backs sysfs exported PWMs, and `pwm_cdev_data` backs PWM waveform ioctls.

Control flow: chip drivers allocate a `pwm_chip`, fill `pwm_ops`, and call `pwmchip_add` or devm variants. Consumers resolve PWMs through Device Tree, ACPI firmware nodes, or static lookup tables, then request and apply states. The apply path validates state, locks the chip with either spinlock or mutex depending on `chip->atomic`, chooses waveform or legacy `.apply` callbacks, updates cached `pwm->state`, and optionally runs debug readback checks. Registration creates class devices, cdevs for waveform-capable chips, and optional gpiochips.

State and persistence: runtime state lives in chip objects, per-PWM flags, cached requested state, labels, sysfs export objects, idr membership, static lookup lists, and optional suspend snapshots for exported sysfs PWMs. It persists only for the driver lifetime; hardware state may survive separately and is sampled on request when callbacks support it.

Dependencies and integration: integrates with the device model, class/cdev infrastructure, OF and ACPI firmware parsing, module refcounts, runtime PM ordering through device links, debugfs, tracepoints, GPIO library when enabled, and UAPI `linux/pwm.h`.

Risks and test signals: concurrency is central: global lookup locks, per-chip locks, requested/exported flags, and remove-time operational transitions must stay coherent. Waveform rounding semantics, legacy polarity conversion, sysfs suspend/resume, cdev ioctl validation, and module lifetime are regression-prone. Test signals include PWM selftests or consumer drivers, sysfs export/unexport, cdev request/free/set/get ioctls, DT/ACPI lookup including probe deferral, debugfs output, `CONFIG_PWM_DEBUG`, atomic-context users, and chip removal with active consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-ab8500.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-ab8500.c

Purpose: implements a single-channel PWM provider for ST-Ericsson/Analog Baseband AB8500 MFD PWM output generators.

Important APIs/types/functions: `struct ab8500_pwm_chip` stores the AB8500 hardware id. `ab8500_pwm_apply()` converts requested period/duty to the AB8500 divisor and 10-bit duty fields, writes `AB8500_PWM_OUT_CTRL1/2`, and toggles `AB8500_PWM_OUT_CTRL7`. `ab8500_pwm_get_state()` reads the same registers back. `ab8500_pwm_probe()` validates platform id, allocates one PWM, and registers it.

Control flow: requests are handled by the PWM core. Apply rejects inverted polarity, computes a supported period divisor from the fixed 9.6 MHz clock, rejects too-short periods, writes low/high duty bytes, and enables the selected output bit. Disable clears the enable bit. State read first checks enable, then reconstructs period and duty from divisor and duty steps.

State and persistence: driver state is only the per-chip `hwid`; hardware registers hold the active PWM configuration. No suspend/resume or persistent software cache is provided.

Dependencies and integration: depends on AB8500 MFD register access through `abx500_*_register_interruptible()`, platform-device ids, and the PWM core. Kconfig restricts it to AB8500 core on U8500.

Risks and test signals: supported period range is narrow and quantized; polarity is fixed normal. The duty calculation clamps with `max_t(..., 1024)`, which can push most nonzero requests to full duty and deserves review against intended rounding. Test signals include MFD register read/write failures, period boundary values, 0/full duty, disable producing low output, and `get_state` consistency.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-ab8500.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-adp5585.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-adp5585.c

Purpose: exposes the PWM function in Analog Devices ADP5585/ADP5589 MFD chips as a one-channel PWM controller.

Important APIs/types/functions: `struct adp5585_pwm_chip` describes variant register offsets; `struct adp5585_pwm` stores the parent regmap and external config register. `pwm_adp5585_request()` muxes pin R3 to PWM output, `pwm_adp5585_free()` restores GPIO4, `pwm_adp5585_apply()` writes off/on 16-bit counters and enables continuous PWM mode, and `pwm_adp5585_get_state()` reads counters and enable state.

Control flow: probe obtains the parent `adp5585_dev`, selects variant register data from `platform_device_id`, inherits the parent's OF node, and registers one PWM. Apply disables by clearing `ADP5585_PWM_EN`; enabled requests require normal polarity and a minimum period, clamp to hardware maximum, write OFF then ON counts, and set enable/mode bits.

State and persistence: runtime state is parent regmap plus static variant offsets. Hardware registers persist while the MFD device remains powered; the driver does not keep an additional cache.

Dependencies and integration: integrates with the ADP5585 MFD parent, regmap bulk little-endian accesses, platform id matching, and PWM pin mux through the extender config register.

Risks and test signals: only normal polarity is supported and disabling drives the output low immediately. The enable sequence performs an update-bits call followed by `regmap_set_bits()` for enable, which should be verified against hardware latching. Test signals include ADP5585 and ADP5589 variants, request/free pin muxing, min/max period, disabled state, endian counter readback, and MFD regmap failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-adp5585.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-airoha.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-airoha.c

Purpose: implements PWM support for the Airoha EN7581 SoC GPIO/SIPO LED flash hardware, exposing 33 logical PWM channels backed by only eight shared waveform generator buckets.

Important APIs/types/functions: `struct airoha_pwm` holds a regmap, initialized-channel bitmap, per-generator buckets, and channel-to-bucket cache. Helpers convert nanoseconds to 4 ms period ticks and 8-bit duty ticks. `airoha_pwm_get_generator()`, `airoha_pwm_consume_generator()`, and `airoha_pwm_release_bucket_config()` manage shared generators. `airoha_pwm_sipo_init()` programs the serial GPIO shift register path. `airoha_pwm_apply()` and `airoha_pwm_get_state()` are the PWM callbacks.

Control flow: probe gets the parent syscon regmap and registers 33 PWMs. Apply disables by clearing the flash-map enable bit and releasing the assigned bucket. Enabled requests require normal polarity, clamp period to 1 s, quantize to 4 ms ticks, compute duty ticks, select or allocate a generator bucket, program period/duty registers, maps the GPIO/SIPO channel to that bucket, and reinitializes SIPO hardware when needed.

State and persistence: the driver maintains software reference counts for shared buckets plus per-channel initialization state; hardware flash-map and cycle registers hold active output. State is not persisted across driver unload.

Dependencies and integration: depends on parent MFD/syscon regmap, regmap polling, OF platform matching, bitmap helpers, and the PWM core. It integrates GPIO pins and SIPO pins as one PWM namespace.

Risks and test signals: bucket sharing is the main risk: only eight distinct waveforms can run, bucket reuse affects rounding, and failed programming must roll back reference counts correctly. SIPO initialization has polling timeouts. Test signals include more than eight unique waveforms, full-duty bucket reuse, SIPO channel enable/disable, all channels disabled clearing SIPO mode, readback of mapped buckets, and regmap failure injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-airoha.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-apple.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-apple.c

Purpose: implements a one-channel PWM controller for Apple SoC fixed PWM hardware used on ARM Apple platforms.

Important APIs/types/functions: `struct apple_pwm` stores MMIO base and clock rate. `apple_pwm_apply()` converts period/duty to ON and OFF cycle registers and writes `APPLE_PWM_CTRL` with enable/output/update bits. `apple_pwm_get_state()` reads control, ON, and OFF cycles to reconstruct `pwm_state`. Probe maps MMIO, enables the clock, validates rate, and registers the chip.

Control flow: enabled applies reject inverted polarity, compute on cycles from duty and off cycles from period minus on time, clamp each to 32 bits, write shadowed cycle registers, then write control to update and enable output. Disabled applies clear the control register. Reads report enabled only when both enable and output-enable bits are set.

State and persistence: software state is MMIO base and fixed clock rate; hardware registers keep the current PWM configuration while powered. No PM callbacks are implemented here.

Dependencies and integration: depends on platform/OF matching for `apple,s5l-fpwm`, an enabled clock, MMIO accessors, and the PWM core.

Risks and test signals: off-cycle calculation can underflow if duty exceeds period; the PWM core normally validates this for enabled states, but callers and future waveform paths should preserve that invariant. Cycle clamping may silently lengthen/shorten large requests. Test signals include normal/disabled output, readback consistency, clock-rate validation, duty 0/full-period boundaries, and unsupported inverted polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-apple.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-argon-fan-hat.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-argon-fan-hat.c

Purpose: exposes the Argon40 Fan HAT I2C fan controller as a one-channel PWM provider with a fixed about-30 kHz period.

Important APIs/types/functions: this driver uses the PWM waveform API rather than legacy `.apply`. `argon_fan_hat_round_waveform_tohw()` maps requested duty length to an 8-bit percentage value, `argon_fan_hat_round_waveform_fromhw()` maps percentage back to a fixed-period waveform, and `argon_fan_hat_write_waveform()` writes the duty percent to I2C register `0x80`.

Control flow: I2C probe allocates one PWM chip and stores the `i2c_client` as driver data. Users set waveforms through the PWM core; the driver rounds any period to the fixed HAT period and writes only the duty percentage. There is intentionally no read callback because reading from the controller stops the fan.

State and persistence: no software cache is kept. The controller stores the last written duty internally; the PWM core's requested state is the only readable host-side state.

Dependencies and integration: depends on I2C SMBus byte writes, OF compatible `argon40,fan-hat`, and the PWM core waveform callbacks. It can also participate in the framework's character-device waveform path.

Risks and test signals: absence of hardware readback limits diagnostics and resume validation. Rounding is coarse to integer percent and ignores requested offset or period. Test signals include I2C write failures, 0/100 percent duty, fixed-period roundtrip through `PWM_IOCTL_ROUNDWF`, and verifying that no read path is attempted on hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-argon-fan-hat.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel-hlcdc.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel-hlcdc.c

Purpose: implements the PWM output embedded in Atmel/Microchip HLCDC display controllers, commonly used for LCD backlight control.

Important APIs/types/functions: `struct atmel_hlcdc_pwm` tracks the parent `atmel_hlcdc`, currently selected PWM clock, and SoC errata flags. `atmel_hlcdc_pwm_apply()` selects slow or system clock, computes prescaler and 8-bit duty value, programs `ATMEL_HLCDC_CFG(6)`, and enables/disables `ATMEL_HLCDC_PWM`. PM callbacks reapply state across suspend/resume.

Control flow: probe obtains the parent HLCDC data, enables the peripheral clock, matches parent SoC errata, registers one PWM, and stores the chip as driver data. Apply chooses a clock according to requested period and errata, switches clock mux when necessary, clamps duty to 255/256, sets polarity bit, writes enable/disable commands, and polls status.

State and persistence: state includes the current clock pointer and parent HLCDC register state. During suspend the driver leaves the peripheral clock on if PWM is active; resume reenables it if needed and reapplies cached PWM state.

Dependencies and integration: depends on the HLCDC MFD parent, regmap, clock framework, OF matching on both parent and child compatible strings, and PWM core cached state.

Risks and test signals: clock switching has an error path where a newly enabled clock may remain enabled if the mux update fails. Duty cannot reach true 100 percent. Polling has no delay timeout value other than immediate-poll semantics. Test signals include errata-specific SoCs, slow/sys clock selection, polarity changes, suspend/resume with PWM on and off, and status-poll failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel-hlcdc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel-tcb.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel-tcb.c

Purpose: exposes an Atmel Timer Counter Block channel as two PWM outputs, one driven by RA and one by RB, sharing the same RC period.

Important APIs/types/functions: `struct atmel_tcb_pwm_chip` owns clocks, regmap, channel number, counter width, per-output duty/period/divisor state, and suspend backup. `atmel_tcb_pwm_request()` initializes CMR wave mode and imports existing hardware state. `atmel_tcb_pwm_config()` selects divisors and enforces shared period constraints. `atmel_tcb_pwm_enable()` and `atmel_tcb_pwm_disable()` program compare actions and trigger/start/stop the timer. PM callbacks save/restore CMR/RA/RB/RC.

Control flow: probe reads the child `reg` channel, obtains the parent syscon regmap and clocks, handles optional generic clock support, locks clock rates exclusively, initializes a spinlock, marks the chip atomic, and registers two PWMs. Apply runs under the spinlock, disabling or configuring then enabling the selected output.

State and persistence: per-output software state tracks selected divisor, duty, and period because both outputs share the timer period. Suspend stores channel registers and restores them on resume. Hardware registers persist while the block is powered.

Dependencies and integration: depends on AT91 TCB register definitions, syscon/regmap, OF clock names, clocksource headers, and the PWM core. It integrates tightly with parent TCB binding semantics.

Risks and test signals: both PWM outputs must use the same period when the peer output is active; this is a visible functional constraint. Atomic marking must remain valid for regmap and clock usage paths. Resume writes the CCR arguments in a suspicious order (`regmap_write(regmap, ATMEL_TC_CLKEN | ATMEL_TC_SWTRG, ATMEL_TC_REG(...))`) that merits review. Test signals include shared-period rejection, zero/full duty polarity behavior, slow clock fallback, 16/32-bit variants, suspend/resume restore, and concurrent RA/RB users.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel-tcb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel.c

Purpose: implements the main Atmel/Microchip PWM controller driver for SoCs with dedicated PWM channel registers.

Important APIs/types/functions: `struct atmel_pwm_chip` stores clock, MMIO base, variant register layout, and an `update_pending` bitmask. Variant data describes v1/v2 duty/period/update registers and period width. Helpers calculate period/prescaler (`atmel_pwm_calculate_cprd_and_pres()`), duty (`atmel_pwm_calculate_cdty()`), pending-update handling, disable waits, and clock enable restoration. `atmel_pwm_apply()` and `atmel_pwm_get_state()` are the callbacks.

Control flow: probe allocates four PWMs, maps registers, gets a prepared clock, enables the clock once for already-running hardware channels, and registers the chip. Apply can update duty in-place when enabled polarity and period are unchanged; otherwise it disables a running channel, enables the clock for a stopped one, programs CMR/CPRD/CDTY, and enables the channel. Disable waits for pending duty updates and hardware disable before optionally disabling the clock.

State and persistence: requested state is cached by the PWM core; driver state tracks pending hardware update events and variant layout. Hardware state may be inherited at boot, and probe keeps clocks enabled for channels already active.

Dependencies and integration: depends on MMIO, clock framework, OF match data for Atmel/SAMA5/SAM9x60 variants, and PWM core debug/state callbacks.

Risks and test signals: pending-update waiting uses polling with a two-second timeout; missed ISR-clearing semantics can affect disable correctness. Disabled polarity changes are documented as not honored. Clock reference counting across already-on channels must match channel activity. Test signals include v1/v2 variants, duty-only update path, zero/full duty, disable after pending update, `get_state` after bootloader configuration, and clock-count balance on probe failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-atmel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-axi-pwmgen.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-axi-pwmgen.c

Purpose: implements a waveform-capable PWM driver for the Analog Devices AXI PWM generator soft IP.

Important APIs/types/functions: `struct axi_pwmgen_ddata` stores regmap and PWM clock rate. `struct axi_pwmgen_waveform` is the hardware waveform representation. The driver implements `.round_waveform_tohw`, `.round_waveform_fromhw`, `.read_waveform`, and `.write_waveform`. `axi_pwmgen_setup()` verifies the core magic and ADI pcore major version, enables the core, enables force-align, and returns the channel count.

Control flow: probe maps MMIO into a regmap, validates hardware, allocates a PWM chip with the reported `NPWM`, enables AXI and optional external clocks, locks clock rate, validates the rate, marks the chip atomic, and registers it. Writes program period, duty, and offset registers for one channel, then write `LOAD_CONFIG`, which resynchronizes enabled channels.

State and persistence: software stores only regmap and clock rate. Hardware channel registers store period/duty/offset counts. The framework caches requested state; readback is available via hardware waveform registers.

Dependencies and integration: depends on ADI AXI common version macros, regmap-mmio, clocks, OF compatible `adi,axi-pwmgen-2.00.a`, and the PWM waveform API including character-device users.

Risks and test signals: `LOAD_CONFIG` can resynchronize all channels, so one consumer can glitch another unless periods are coordinated. Readback contains a FIXME about duty offset behavior when offset exceeds period. Test signals include core magic/version failure, channel count, clock-rate bounds, exact and rounded waveform ioctls, duty-offset programming, and multi-channel resynchronization behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-axi-pwmgen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm-iproc.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm-iproc.c

Purpose: implements a four-channel PWM driver for Broadcom iProc PWM hardware.

Important APIs/types/functions: `struct iproc_pwmc` stores MMIO base and clock. `iproc_pwmc_apply()` computes prescaler, period count, and duty count, disables the channel, programs prescale/period/duty/polarity, and conditionally reenables. `iproc_pwmc_get_state()` reads enable, polarity, prescale, period, and duty registers. Probe maps registers, enables the clock, initializes full-drive normal polarity, and registers four PWMs.

Control flow: apply iterates prescale from 0 to 63 until count values fit 16-bit ranges and period is at least 2. It enforces the hardware's 400 ns enable-toggle delay around disable/enable. State read reconstructs nanoseconds from counts, prescaler, and clock rate.

State and persistence: no extra software cache beyond MMIO base and clock. Hardware registers hold active settings; the PWM core caches requested state.

Dependencies and integration: depends on common clock, MMIO, OF compatible `brcm,iproc-pwm`, and PWM core callbacks.

Risks and test signals: arithmetic uses `rate * state->period` in `u64`, so very high rates or periods deserve overflow review. The driver disables before every apply, which may cause visible glitches. Test signals include prescale boundary periods, polarity readback, clock rate zero handling in `get_state`, 400 ns delay compliance, and all four channels.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm-iproc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm-kona.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm-kona.c

Purpose: implements the six-channel Broadcom Kona PWM controller, whose hardware lacks a conventional disable bit and applies settings via trigger edges.

Important APIs/types/functions: `struct kona_pwmc` stores MMIO base and clock. `kona_pwmc_prepare_for_settings()` and `kona_pwmc_apply_settings()` handle smooth/trigger sequencing and required 400 ns delays. `kona_pwmc_config()` computes prescale, period count, and duty count. `kona_pwmc_set_polarity()`, `kona_pwmc_enable()`, `kona_pwmc_disable()`, and `kona_pwmc_apply()` implement the PWM operations.

Control flow: probe briefly enables the clock, configures push/pull type bits for all channels, disables the clock, and registers six PWMs. Apply handles polarity changes by disabling first if needed, simulates disable by programming zero duty/period, enables the clock for active channels, and configures requested duty/period through the trigger sequence.

State and persistence: the driver relies on PWM core cached state for enabled/polarity decisions and hardware registers for output. It does not implement `get_state` or PM save/restore.

Dependencies and integration: depends on clock framework, MMIO, OF compatible `brcm,kona-pwm`, and the PWM core.

Risks and test signals: hardware semantics are unusual: disabling by zero duty, trigger/smooth timing, and clock disable can leave the line high or low depending on instant. Enabling before configuration is preserved for compatibility but may glitch. Test signals include enable-from-disabled glitches, polarity changes, zero duty disable, long-period smooth behavior, and clock enable/disable balancing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm-kona.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm2835.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm2835.c

Purpose: implements the two-channel BCM2835/Raspberry Pi PWM controller.

Important APIs/types/functions: `struct bcm2835_pwm` stores MMIO base, clock, and exclusive clock rate. `bcm2835_pwm_apply()` validates period bounds, converts period and duty to clock cycles, writes range/data registers, and updates per-channel control bits for mode, polarity, and enable. PM callbacks disable and reenable the clock.

Control flow: probe maps MMIO, enables the clock, gets an exclusive rate, stores the rate, marks the chip atomic, and registers two PWMs. Apply computes a maximum safe period to avoid 32-bit count overflow, rejects periods below two cycles, writes period and duty, then rewrites the control byte for the selected channel.

State and persistence: software state is clock rate and MMIO base. Hardware registers store current output; no `get_state` callback is implemented, so framework state is request-based after registration.

Dependencies and integration: depends on MMIO, common clock exclusive-rate API, OF compatible `brcm,bcm2835-pwm`, PM sleep ops, and the PWM core.

Risks and test signals: no readback means bootloader-initialized state is not imported. Applying one channel rewrites the shared control register and must preserve the other channel's byte. Test signals include both channels independently, period overflow limit, too-small period rejection, polarity bit behavior, suspend/resume clock restoration, and atomic apply assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-bcm2835.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-berlin.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-berlin.c

Purpose: implements the four-channel Marvell Berlin PWM controller.

Important APIs/types/functions: `struct berlin_pwm_chip` stores clock, MMIO base, and per-channel suspend backups. `berlin_pwm_config()` converts period/duty into timer count and optional 4096 prescale. `berlin_pwm_set_polarity()`, `berlin_pwm_enable()`, `berlin_pwm_disable()`, and `berlin_pwm_apply()` implement the PWM operations. PM callbacks save and restore enable/control/duty/count registers.

Control flow: probe maps MMIO, enables the clock, registers four PWMs, and stores the chip for PM. Apply disables when changing polarity, programs duty/period, then enables if the channel was previously off. Suspend saves all channel registers and disables the clock; resume reenables and restores them.

State and persistence: suspend state is cached in `channel[]`. Runtime output configuration lives in hardware registers and PWM core requested state. There is no `get_state` callback.

Dependencies and integration: depends on common clock, MMIO, OF compatible `marvell,berlin-pwm`, and PM sleep callbacks.

Risks and test signals: comments document misleading hardware prescaler behavior; only no-prescale and 4096-prescale are useful. There is no explicit guard for zero period before dividing duty by period. Test signals include prescale boundary, polarity changes while active, suspend/resume restore, disabled channel behavior, and period zero validation through the core.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-berlin.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-brcmstb.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-brcmstb.c

Purpose: implements the two-channel Broadcom STB/BCM7038 PWM controller.

Important APIs/types/functions: `struct brcmstb_pwm` stores MMIO base and clock. Endian-aware `brcmstb_pwm_readl/writel()` support big-endian MIPS. `brcmstb_pwm_config()` calculates variable-frequency control word, period, and on-time registers. `brcmstb_pwm_enable_set()` toggles start, output-enable, and open-drain bits. `brcmstb_pwm_apply()` restricts polarity and coordinates config/enable.

Control flow: probe gets the clock, maps MMIO, and registers two PWMs. Apply rejects inverted polarity, disables output if requested, otherwise computes configuration and enables the channel if it was previously off. Suspend disables the clock; resume reenables it.

State and persistence: no software cache beyond MMIO and clock. Hardware registers keep configuration while powered, but suspend only gates the clock and does not save registers.

Dependencies and integration: depends on common clock, platform/OF matching for `brcm,bcm7038-pwm`, MMIO, endian conditionals for MIPS, and PWM core callbacks.

Risks and test signals: duty equal to period uses a special 100 percent path. The variable-frequency control word search halves powers of two and can reject long periods. No readback callback exists. Test signals include normal-only polarity, 0/100 percent duty, long period rejection, big-endian register access, suspend/resume clock behavior, and two-channel independence.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-brcmstb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-clk.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-clk.c

Purpose: adapts a clock with rate and duty-cycle control into a one-channel PWM provider.

Important APIs/types/functions: `struct pwm_clk_chip` stores the underlying clock and whether this driver has enabled it. `pwm_clk_apply()` enables/disables the clock, sets clock rate from requested period, inverts duty for inverted polarity, and calls `clk_set_duty_cycle()`. Probe gets a prepared clock and registers the PWM chip; remove unregisters and disables any active clock.

Control flow: enabled applies first enable the clock if previously disabled, then set rate and duty cycle through the clock API. Disabled applies disable only if the previous PWM state was enabled. The driver has no readback because the clock API does not expose enough state.

State and persistence: `clk_enabled` is a local software guard for cleanup. Requested PWM state is cached by the framework; actual clock state belongs to the clock provider.

Dependencies and integration: depends on the common clock framework, compatible `clk-pwm`, platform devices, and PWM core. Behavior is largely defined by the underlying clock provider.

Risks and test signals: enabling before programming creates a window with stale clock settings, and rate/duty programming is not atomic. Error after enabling may leave the clock enabled because apply returns without rollback. Test signals include enable failure, `clk_set_rate` failure, duty-cycle failure, inverted polarity mapping, remove while enabled, and clock providers that cannot produce 0 or 100 percent duty.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-clk.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-clps711x.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-clps711x.c

Purpose: implements PWM support for Cirrus Logic CLPS711X/EP7209 style hardware with two fixed-period outputs controlled by PMP configuration bits.

Important APIs/types/functions: `struct clps711x_chip` stores the PMP control MMIO address and clock. `clps711x_pwm_request()` computes and stores the fixed period from the clock rate in `pwm->args.period`. `clps711x_pwm_apply()` checks period/polarity, converts duty to a 4-bit level, and updates the proper bitfield.

Control flow: probe maps the control register, gets the clock, and registers two PWMs. On request the fixed period is derived. Apply rejects inverted polarity and any period different from the fixed argument; disabled output writes a zero duty nibble.

State and persistence: no private runtime cache besides MMIO and clock. Hardware bitfields hold duty levels. The fixed period is stored in per-PWM args during request.

Dependencies and integration: depends on MMIO, clock framework, OF compatible `cirrus,ep7209-pwm`, and PWM core request/apply callbacks.

Risks and test signals: duty resolution is only 4 bits, and there is no `get_state`. Clock rate zero is rejected only at request time. Test signals include both channels, fixed-period enforcement, disabled output level, duty quantization from 0 to 15, and invalid polarity.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-clps711x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-crc.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-crc.c

Purpose: implements the Intel Crystal Cove PMIC PWM, commonly used for backlight control on Intel SoC platforms.

Important APIs/types/functions: `struct crystalcove_pwm` stores the parent PMIC regmap. `crc_pwm_calc_clk_div()` converts period to divider. `crc_pwm_apply()` writes duty, clock divisor/output-enable, and `BACKLIGHT_EN` in an order that handles enable/disable and divisor changes. `crc_pwm_get_state()` reads clock divisor and duty registers to reconstruct period, duty, polarity, and enable.

Control flow: probe obtains the parent `intel_soc_pmic` regmap and registers one PWM. Apply rejects periods above `PWM_MAX_PERIOD_NS` and inverted polarity. Disable first clears `BACKLIGHT_EN`; divisor changes while enabled clear output-enable before reprogramming; enabling writes the clock divider with enable and finally sets `BACKLIGHT_EN`.

State and persistence: no software cache beyond regmap. PMIC registers hold hardware state and are readable through `get_state`.

Dependencies and integration: depends on Intel SoC PMIC MFD, regmap, platform device matching, and the PWM core.

Risks and test signals: period divider math is integer and limited to about 183 Hz minimum frequency. Sequencing between `PWM_OUTPUT_ENABLE` and `BACKLIGHT_EN` is hardware-sensitive. Test signals include max-period rejection, duty update without period change, period change while enabled, disable/enable ordering, get-state accuracy, and PMIC regmap errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-crc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-cros-ec.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-cros-ec.c

Purpose: exposes PWM outputs controlled by a ChromeOS Embedded Controller to the host kernel.

Important APIs/types/functions: `struct cros_ec_pwm_device` stores the EC pointer and whether indexes are typed. `cros_ec_pwm_set_duty()` sends `EC_CMD_PWM_SET_DUTY`; `cros_ec_pwm_get_duty()` sends `EC_CMD_PWM_GET_DUTY`; `cros_ec_dt_type_to_pwm_type()` maps DT typed indexes to EC PWM types. `cros_ec_num_pwms()` probes generic channel count by reading sequential duties. `cros_ec_pwm_apply()` and `cros_ec_pwm_get_state()` translate between PWM state and EC duty values.

Control flow: probe gets the parent EC, chooses generic or typed mode based on compatible string, determines channel count, allocates the chip, seeds each PWM's fixed period argument to `EC_PWM_MAX_DUTY`, and registers it. Apply requires that period, rejects inverted polarity, maps disabled to duty zero, and sends the EC command.

State and persistence: driver state is only EC pointer and mode. Duty and enable state live in EC firmware; host-side requested state is cached by the PWM core and readable through EC commands.

Dependencies and integration: depends on ChromeOS EC protocol structures, EC command transport, OF bindings for `google,cros-ec-pwm` and `google,cros-ec-pwm-type`, and PWM core abstractions.

Risks and test signals: generic channel enumeration treats `-EINVAL` as end-of-list and other EC errors as fatal. The EC has fixed period and no separate enable bit, so consumers expecting period changes will fail. Test signals include generic and typed bindings, invalid type index, EC command errors, zero/nonzero duty enable translation, max channel enumeration, and get-state during probe/request.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-cros-ec.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc-core.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc-core.c

Purpose: provides the shared PWM core for Synopsys DesignWare timer/PWM controllers, used by bus-specific frontends such as the PCI driver.

Important APIs/types/functions: `__dwc_pwm_set_enable()` toggles timer enable. `__dwc_pwm_configure_timer()` converts duty and period into low/high load counts and programs PWM user mode. `dwc_pwm_apply()` requires inverted polarity and manages runtime PM around enabled state. `dwc_pwm_get_state()` reads load counts and control register. `dwc_pwm_alloc()` allocates an eight-channel PWM chip, sets `clk_ns = 10`, and exports the helper in namespace `dwc_pwm`.

Control flow: frontend drivers call `dwc_pwm_alloc()`, set `dwc->base`, and register the chip. Apply enables runtime PM when starting from disabled, programs timer registers by disabling, writing low/high load counts, setting mode/PWM bits, and conditionally enabling. Disable clears enable and drops runtime PM.

State and persistence: shared state is the MMIO base, fixed input clock period, and optional context stored by frontend code. Hardware timer registers hold active configuration.

Dependencies and integration: depends on the PWM core, runtime PM, exported namespace `dwc_pwm`, and register definitions in `pwm-dwc.h`.

Risks and test signals: hardware cannot represent 0 percent or 100 percent duty because both low and high counts must be at least one clock. Runtime PM get/put return values are not checked. Test signals include invalid normal polarity, min/max load counts, enable/disable PM balancing, get-state in PWM and non-PWM modes, and frontend allocation/register sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc-core.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc.c

Purpose: implements the PCI frontend for Synopsys DesignWare PWM controllers, currently matching Intel Elkhart Lake hardware.

Important APIs/types/functions: `struct dwc_pwm_info` data for Elkhart Lake describes two 4 KiB controller blocks. `dwc_pwm_init_one()` allocates a shared-core chip and assigns the per-block base address. `dwc_pwm_probe()` enables the PCI device, maps BAR0, creates all PWM chips, stores driver data, and enables runtime PM. Suspend/resume save and restore every timer's load and control registers.

Control flow: PCI probe uses managed PCI enable and iomap helpers, then loops over controller instances. Remove forbids runtime PM and wakes the device. Suspend refuses to proceed if any PWM state is enabled, otherwise snapshots context; resume restores registers for each chip and timer.

State and persistence: `dwc_pwm_drvdata` stores frontend info, BAR base, and chip pointers. `dwc->ctx[]` persists timer registers across system sleep only. Runtime PM state is delegated to the device core.

Dependencies and integration: depends on PCI, managed MMIO mapping, runtime PM, the `pwm-dwc-core.c` exported allocator, and Intel PCI device id `0x4bb7`.

Risks and test signals: suspend rejects active consumers with `-EBUSY`, which can block system suspend. The source defines `DEFAULT_MOUDLE_NAMESPACE` with a typo, while namespace import is handled in the header. Test signals include PCI probe with two chips, BAR mapping failure, active-PWM suspend rejection, inactive context restore, runtime PM transitions, and module namespace/link checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc.h -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc.h

Purpose: defines the shared register map, data structures, inline MMIO helpers, and allocator prototype for Synopsys DesignWare PWM support.

Important APIs/types/functions: register macros cover load count, current value, control, interrupt, EOI, and component version offsets. Control bits define enable, free/user mode, interrupt mask, and PWM mode. `struct dwc_pwm_info`, `struct dwc_pwm_drvdata`, `struct dwc_pwm_ctx`, and `struct dwc_pwm` form the shared frontend/core contract. `to_dwc_pwm()`, `dwc_pwm_readl()`, and `dwc_pwm_writel()` are inline helpers; `dwc_pwm_alloc()` is declared for frontends.

Control flow: no runtime flow occurs in the header. It is included by both the shared core and bus frontend so they agree on register offsets and state layout.

State and persistence: declares context storage for suspend/resume snapshots and per-controller MMIO base/clock period. Actual allocation and persistence are handled by C files.

Dependencies and integration: imports namespace `dwc_pwm` and assumes Linux bitops/MMIO definitions are already available through including files. It is the internal ABI between `pwm-dwc-core.c` and `pwm-dwc.c`.

Risks and test signals: offset macros encode hardware layout; mistakes break every frontend. `DWC_TIM_LD_CNT2` lives in a separate register range, so channel indexing should be tested for all eight timers. Test signals include compile coverage of both C files, namespace import/export checks, suspend context arrays sized to `DWC_TIMERS_TOTAL`, and register write/read smoke tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-dwc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-ep93xx.c -->
# sources/distributed-fs/ceph-client/drivers/pwm/pwm-ep93xx.c

Purpose: implements PWM support for Cirrus Logic EP93xx SoCs, exposing one PWM channel per platform device instance.

Important APIs/types/functions: `struct ep93xx_pwm` stores MMIO base and `pwm_clk`. `ep93xx_pwm_apply()` handles polarity changes, clock gating, period/duty conversion to 16-bit cycles, ordered register updates while running, and enable/disable. Probe maps the channel registers, gets the PWM clock, and registers one PWM.

Control flow: apply disables the output before changing polarity, enables the clock for register access, writes the invert register, then handles disabled requests. Enabled configuration enables the clock if needed, calculates `TERM_COUNT` and `DUTY_CYCLE`, writes in an order chosen to avoid transient duty greater than period, disables the clock again if the channel was not already enabled, and finally enables output when transitioning from disabled.

State and persistence: no software cache beyond base and clock. The driver relies on PWM core cached state for previous polarity/enabled decisions and hardware registers for output.

Dependencies and integration: depends on platform or OF matching `cirrus,ep9301-pwm`, MMIO word accesses, the clock framework, and PWM core callbacks.

Risks and test signals: no `get_state` means boot state is not imported. The clock is toggled multiple times in one apply path; failures after partial configuration need careful observation. Period/duty must fit 16 bits. Test signals include polarity changes while enabled, period/duty boundary fit, register-write ordering while running, enable/disable clock balance, and single-channel platform instances for SoC variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pwm/pwm-ep93xx.c -->
