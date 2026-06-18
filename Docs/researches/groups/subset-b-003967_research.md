# Research Report: subset-b-003967

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da7280.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/da7280.c

## Purpose
`da7280.c` is an I2C input force-feedback driver for the Dialog/Renesas DA7280 haptic actuator controller. It exposes a `da7280-haptic` input device with `FF_CONSTANT`, `FF_PERIODIC`, `FF_CUSTOM`, and gain capabilities, then translates uploaded effects into DA7280 direct register, waveform-memory, PWM, RTWM, or external-triggered waveform behavior.

## Important APIs, Types, and Functions
The central state is `struct da7280_haptic`, which owns the regmap, input device, optional PWM device, delayed work state, active/suspended flags, parsed actuator configuration, sequence/GPI configuration, and the 100-byte SNP waveform memory cache. `da7280_haptics_upload_effect()` validates and stores force-feedback effects; `da7280_haptics_playback()` schedules `da7280_haptic_work()`; `da7280_haptic_activate()` and `da7280_haptic_deactivate()` perform mode-specific hardware transitions. `da7280_irq_handler()` handles sequence completion, sequence faults, warnings, and diagnostic details. `da7280_parse_properties()` consumes firmware properties such as actuator type, constant/periodic operation mode, nominal/absolute voltages, impedance/current, resonant frequency, sequence IDs, GPI controls, feature enables, and initial memory data.

## Control Flow
Probe requires an IRQ, allocates driver state, parses properties, optionally acquires and validates PWM timing for PWM constant mode, initializes regmap, applies chip initialization in `da7280_init()`, creates the input FF device, registers upload/playback callbacks, registers the input device, and finally requests the threaded IRQ. Open sets `STANDBY_EN`; close cancels work, deactivates any effect, and clears standby. Playback only records the requested on/off value and queues work unless suspended. Effect upload rejects updates while active, decodes constant effects into DRO level or PWM gain, decodes custom periodic payloads either as waveform memory, playback sequence/loop values, or GPI sequence mapping, and writes the relevant registers.

## State and Persistence Behavior
State is mostly volatile kernel memory plus DA7280 registers. Uploaded waveform memory is cached in `snp_mem` and pushed to chip memory only while inactive, warning-free, and unlocked. `active` mirrors whether a run is believed active and is also cleared by sequence-done IRQs. Suspend marks `suspended` under the input event lock, stops the device, and resume restarts and clears the flag. No filesystem persistence exists.

## Dependencies and Integration Points
The driver integrates with I2C, regmap, input FF, firmware properties/OF compatible `dlg,da7280`, optional PWM, threaded IRQs, and PM sleep callbacks. User space interacts through standard evdev force-feedback upload/playback APIs.

## Risks and Test Signals
Risk centers on invalid custom waveform payloads, user-supplied actuator parameters, PWM period bounds, memory-lock requirements, and races between playback, suspend, IRQ completion, and effect upload. Test signals include successful probe with IRQ, FF effect upload rejection for invalid lengths/values, constant and custom playback register transitions, sequence-done/fault IRQ handling, PWM duty-cycle calculation across `acc_en` modes, suspend ignoring playback requests, and no work remaining after close.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da7280.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9052_onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/da9052_onkey.c

## Purpose
`da9052_onkey.c` is a platform child driver for the Dialog DA9052 PMIC ONKEY pin. It exposes a simple input device named `da9052-onkey` that reports `KEY_POWER` press and release events.

## Important APIs, Types, and Functions
`struct da9052_onkey` stores the parent MFD pointer, input device, and delayed work. `da9052_onkey_query()` reads `DA9052_STATUS_A_REG` through the DA9052 MFD API and derives the pressed state from `DA9052_STATUSA_NONKEY`. `da9052_onkey_irq()` calls the query routine from the PMIC IRQ path, while `da9052_onkey_work()` polls later to synthesize release detection.

## Control Flow
Probe obtains the parent `struct da9052` with `dev_get_drvdata()`, allocates private data and an input device, initializes delayed work, declares `EV_KEY/KEY_POWER`, requests `DA9052_IRQ_NONKEY` through `da9052_request_irq()`, and registers the input device. The IRQ only fires on assertion, so the handler reads the current status, reports it, and if still pressed schedules another query after 50 ms. Remove frees the PMIC IRQ, cancels delayed work, unregisters input, and frees private memory.

## State and Persistence Behavior
The only durable state is the delayed polling loop while the button remains pressed. The input core carries the current key state. No state persists across remove or reboot.

## Dependencies and Integration Points
This driver depends on the DA9052 MFD core/register definitions, Linux input, platform bus binding `platform:da9052-onkey`, workqueues, and PMIC interrupt services. It assumes the PMIC status bit is authoritative for deassertion because the hardware does not emit a release IRQ.

## Risks and Test Signals
Important risks are missed release if register reads fail, polling churn while a key is held, and cleanup ordering around delayed work and IRQ teardown. Tests should exercise press/release through mocked DA9052 status transitions, register-read errors, probe failures at each allocation/request step, and remove while delayed work is pending.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9052_onkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9055_onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/da9055_onkey.c

## Purpose
`da9055_onkey.c` is the DA9055 PMIC ONKEY input driver. It registers an input device that reports `KEY_POWER` and compensates for hardware that interrupts on assertion but not release.

## Important APIs, Types, and Functions
`struct da9055_onkey` carries the parent DA9055 handle, input device, and delayed work item. `da9055_onkey_irq()` reports the press immediately, then calls `da9055_onkey_query()`. The query function reads `DA9055_REG_STATUS_A`, masks `DA9055_NOKEY_STS`, reports release when the bit clears, and reschedules itself after 10 ms while the bit remains set.

## Control Flow
Probe gets the platform IRQ named `ONKEY`, allocates private data and a manually managed input device, initializes `EV_KEY/KEY_POWER`, creates delayed work, requests a threaded high-triggered oneshot IRQ, registers the input device, and stores driver data. Error paths free the IRQ, cancel work, and free input. Remove retrieves the virtual IRQ through `regmap_irq_get_virq()`, frees it, cancels delayed work, and unregisters the input device.

## State and Persistence Behavior
The pressed state is maintained by the input core, while release polling is transient delayed work. The driver does not persist configuration or state.

## Dependencies and Integration Points
It integrates with the DA9055 MFD/regmap IRQ infrastructure, Linux platform devices, threaded IRQs, input, and workqueues. It is bound as `platform:da9055-onkey`.

## Risks and Test Signals
Risk areas include inconsistent IRQ number handling between probe and remove, release latency from 10 ms polling, register-read failures that leave state unchanged, and input allocation not being devm-managed. Test signals include high-level IRQ press reporting, delayed release after status clear, repeated polling while held, probe failure cleanup, and remove with pending work.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9055_onkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9063_onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/da9063_onkey.c

## Purpose
`da9063_onkey.c` supports the ONKEY blocks in Dialog DA9063, DA9062, and DA9061-class PMICs. It reports `KEY_POWER`, handles short-versus-long press behavior, optionally disables long key-power reporting via firmware property, and can command PMIC shutdown when a key-reset fault is observed.

## Important APIs, Types, and Functions
`struct da906x_chip_config` abstracts register and bit differences between DA9063 and DA9062 variants. `struct da9063_onkey` stores delayed work, input device, regmap, config, physical path, and whether `KEY_POWER` long-press reporting is enabled. `da9063_onkey_irq_handler()` classifies presses; `da9063_poll_on()` polls for release, unlocks the key-delay latch, reports release, checks the fault log for key reset, clears it, and writes the shutdown register when needed.

## Control Flow
Probe allocates state, selects chip config from OF match data, gets the parent regmap, reads `dlg,disable-key-power`, allocates input, sets `KEY_POWER`, creates auto-cancel delayed work, gets the `ONKEY` IRQ, requests a low-triggered oneshot threaded IRQ, configures the IRQ as a wake source when possible, and registers input. On IRQ, if long-press reporting is enabled and the nonkey status bit is set, it reports press and starts immediate polling. Otherwise it emits a press-release pair for a short press.

## State and Persistence Behavior
State is held in regmap-controlled PMIC status/control registers and transient delayed work. Wake IRQ configuration persists only for device lifetime. Key reset handling mutates the PMIC fault log and shutdown control register.

## Dependencies and Integration Points
The driver depends on DA9063/DA9062 MFD register definitions, regmap, firmware properties, OF compatibles `dlg,da9063-onkey` and `dlg,da9062-onkey`, input, workqueues, threaded IRQs, and `pm_wakeirq` helpers.

## Risks and Test Signals
Risks include misconfigured match data, failed unlock of nonkey latch, polling forever after read errors, and unexpected PMIC shutdown if the fault-log bit is stale or misinterpreted. Tests should cover variant register mappings, disabled-key-power short-press behavior, long-press press/release polling, wake IRQ setup failure tolerance, fault-log clear and shutdown path, and work autocancel on driver removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/da9063_onkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/drv260x.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/drv260x.c

## Purpose
`drv260x.c` is an I2C force-feedback haptics driver for TI DRV2604/2604L/2605/2605L devices. It exposes a memless `FF_RUMBLE` input device and translates rumble magnitude into real-time playback register writes.

## Important APIs, Types, and Functions
`struct drv260x_data` stores the input device, I2C client, regmap, work item, optional enable GPIO, regulator, magnitude, selected mode/library, and actuator voltage settings. `drv260x_init()` applies voltage registers and mode-specific LRA/ERM calibration or LRA no-cal initialization. `drv260x_worker()` enables the GPIO, waits for the data-sheet communication delay, sets real-time playback mode, and writes magnitude. `drv260x_haptics_play()` scales strong or weak rumble magnitude into an 8-bit register value.

## Control Flow
Probe reads required `mode` and `library-sel` properties, validates LRA/ERM library combinations, reads optional voltage properties, obtains and enables `vbat`, installs a devm power-off action, obtains optional enable GPIO, allocates and registers a memless FF input device, initializes I2C regmap, runs chip initialization, then registers input. Calibration modes write calibration register patches and poll `GO` for completion with a five-second timeout; no-cal mode writes init registers and returns without setting `GO`.

## State and Persistence Behavior
The current magnitude is stored in memory until the work item writes it to `DRV260X_RT_PB_IN`. Regmap cache is disabled, so hardware registers are the active state. Suspend, resume, and close coordinate with `input_dev->mutex`: suspend enters standby, disables GPIO and regulator; resume reverses that if the input device is enabled; close cancels work, writes standby, and disables the GPIO.

## Dependencies and Integration Points
The driver integrates with I2C IDs, OF/ACPI match tables, regmap, regulator, optional GPIO, input FF memless callbacks, and PM sleep hooks. Device-tree bindings come from `dt-bindings/input/ti-drv260x.h`.

## Risks and Test Signals
Risks include invalid property combinations, failed auto-calibration, regulator/GPIO sequencing, magnitude writes racing with suspend/close, and no explicit stop register write on zero magnitude beyond writing zero RTP. Tests should cover property validation, voltage conversion, calibration timeout, rumble scaling, work execution after zero and nonzero effects, and suspend/resume while enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/drv260x.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/drv2665.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/drv2665.c

## Purpose
`drv2665.c` is a TI DRV2665 piezo haptics I2C driver. It exposes a memless `FF_RUMBLE` input device and responds to any rumble playback request by streaming a fixed 8 kHz sine waveform into the device FIFO when the FIFO is empty.

## Important APIs, Types, and Functions
`struct drv2665_data` owns the input device, client, regmap, work item, and `vbat` regulator. `drv2665_worker()` reads `DRV2665_STATUS` and performs a `regmap_bulk_write()` of `drv2665_sine_wave_form` to `DRV2665_FIFO` if `DRV2665_FIFO_EMPTY` is set. `drv2665_init()` writes initial control registers for idle timeout and 25 Vpp gain. `drv2665_close()` cancels work and places the chip in standby.

## Control Flow
Probe allocates state, gets `vbat`, allocates input, configures `drv2665:haptics` with `FF_RUMBLE`, creates the memless FF callback, initializes work and regmap, writes init registers, and registers input. Playback simply schedules the worker; effect magnitude is ignored. Suspend and resume are gated by `input_device_enabled()` under the input mutex and toggle standby plus regulator state.

## State and Persistence Behavior
No effect data is persisted; the fixed waveform table is static. Hardware register state is not cached. The regulator is not enabled in probe, but suspend paths may disable it if the input device is enabled, and resume enables it before clearing standby.

## Dependencies and Integration Points
The driver binds via I2C ID `drv2665` and OF compatible `ti,drv2665`, uses regmap, regulator, input FF memless APIs, and PM sleep operations.

## Risks and Test Signals
Risks include ignoring requested magnitude/duration, regulator enable-state assumptions, FIFO-only playback without explicit repeated scheduling, and error handling that logs but does not notify input callers. Tests should verify FIFO-empty conditional writes, close standby, register patch application, probe cleanup, and suspend/resume regulator behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/drv2665.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/drv2667.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/drv2667.c

## Purpose
`drv2667.c` is an I2C input FF driver for the TI DRV2667 haptic/piezo controller. It programs a waveform in RAM page 1 and uses rumble magnitude to update RAM amplitude and trigger playback.

## Important APIs, Types, and Functions
`struct drv2667_data` carries input, client, regmap, work item, regulator, current page, magnitude, and frequency. `drv2667_set_waveform_freq()` converts hertz to the device frequency code, temporarily switches pages, writes `DRV2667_RAM_FREQ`, and restores the previous page. `drv2667_worker()` writes page-1 amplitude and sets `DRV2667_GO` for nonzero magnitude, or clears `GO` for zero. `drv2667_init()` writes base control registers, initializes RAM header/data fields, sets default 195 Hz, and returns to page 0.

## Control Flow
Probe obtains `vbat`, allocates a memless `FF_RUMBLE` input device, creates the playback callback, initializes work and regmap, runs waveform initialization, and registers input. Playback chooses strong magnitude, then weak magnitude, otherwise zero, and schedules work. Close cancels work and enters standby. Suspend/resume use `input_dev->mutex` and `input_device_enabled()` to enter/leave standby and disable/enable the regulator.

## State and Persistence Behavior
The current magnitude and frequency are kept in memory; programmed waveform RAM and control registers reside in hardware. Regmap cache is disabled. The driver does not expose frequency controls after default initialization.

## Dependencies and Integration Points
It binds by I2C ID `drv2667` and OF compatible `ti,drv2667`, and uses input FF memless, regmap, regulator, and PM sleep helpers.

## Risks and Test Signals
Risks include 16-bit rumble magnitude being written to an 8-bit RAM amplitude register through regmap, page-switch errors leaving the chip on the wrong page, regulator enable-state assumptions, and no user-configurable frequency/duration. Tests should cover page restoration, invalid calculated frequency, nonzero and zero playback paths, init RAM layout, close standby, and suspend/resume error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/drv2667.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/e3x0-button.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/e3x0-button.c

## Purpose
`e3x0-button.c` is a platform input driver for the NI Ettus Research USRP E3x0 power button. It reports `KEY_POWER` from separate press and release IRQ lines.

## Important APIs, Types, and Functions
`e3x0_button_press_handler()` reports `KEY_POWER` down, emits a wakeup event, and syncs input. `e3x0_button_release_handler()` reports key up. `e3x0_button_suspend()` and `e3x0_button_resume()` toggle IRQ wake on the named `press` IRQ if the device may wake the system.

## Control Flow
Probe retrieves `press` and `release` IRQs by name, allocates a devm input device, sets name/phys/parent and `EV_KEY/KEY_POWER`, requests both IRQs with devm, registers input, and marks the device wake-capable. Runtime behavior is direct IRQ-to-input reporting with no deferred work.

## State and Persistence Behavior
The input core tracks key state. Wake capability is device-lifetime state managed during suspend/resume. There is no persistent storage or private driver allocation beyond the input device.

## Dependencies and Integration Points
The driver integrates with platform devices, OF compatible `ettus,e3x0-button`, input, IRQ, and PM wake support. Firmware must provide named `press` and `release` IRQ resources.

## Risks and Test Signals
Risks are mostly resource-description errors and wake IRQ enable/disable failures not being checked. Tests should validate missing IRQ handling, press/release event order, wake event generation, input registration failure cleanup, and suspend/resume behavior with wakeup enabled and disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/e3x0-button.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio-beeper.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/gpio-beeper.c

## Purpose
`gpio-beeper.c` is a generic platform driver that maps input sound events to a GPIO-controlled beeper. It exposes `EV_SND/SND_BELL` and toggles an output GPIO asynchronously.

## Important APIs, Types, and Functions
`struct gpio_beeper` stores a work item, GPIO descriptor, and desired `beeping` state. `gpio_beeper_event()` is the input event callback; it accepts only `EV_SND/SND_BELL`, rejects negative values, records the boolean state, and schedules work. `gpio_beeper_work()` applies the state through `gpiod_set_value_cansleep()`. `gpio_beeper_close()` cancels work and forces the GPIO off.

## Control Flow
Probe allocates state, obtains the unnamed GPIO as `GPIOD_OUT_LOW`, allocates a devm input device, initializes work, fills input IDs and callbacks, advertises `SND_BELL`, stores private data, and registers input. User-space sound events enter through evdev and are converted to workqueue GPIO writes.

## State and Persistence Behavior
`beeping` is the only software state and is not persistent. GPIO state is forced low on close and starts low at probe.

## Dependencies and Integration Points
The driver binds as `gpio-beeper` and OF compatible `gpio-beeper`, using gpiod consumers, input event callbacks, and workqueues.

## Risks and Test Signals
Risks include lack of locking around `beeping` versus scheduled work, unsupported sound codes returning `-ENOTSUPP`, and GPIO sleep requirements necessitating deferred work. Tests should cover event validation, positive/zero bell values, close cancellation, initial low output, and probe failure when GPIO or input allocation fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio-beeper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio-vibra.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/gpio-vibra.c

## Purpose
`gpio-vibra.c` is a simple GPIO/regulator-backed vibrator driver. It exposes a memless `FF_RUMBLE` input device and turns a regulator plus enable GPIO on when rumble magnitude is nonzero.

## Important APIs, Types, and Functions
`struct gpio_vibrator` stores input, enable GPIO, `vcc` regulator, work item, and `running`/`vcc_on` state. `gpio_vibrator_play_effect()` chooses strong magnitude or weak magnitude, converts nonzero to `running`, and schedules work. `gpio_vibrator_start()` enables the regulator if needed and asserts the GPIO. `gpio_vibrator_stop()` deasserts GPIO and disables the regulator if it was enabled.

## Control Flow
Probe allocates state, input, regulator `vcc`, and `enable` GPIO, initializes work, configures `gpio-vibrator` with `FF_RUMBLE`, creates a memless FF handler, registers input, and stores platform data. Work starts or stops hardware based on `running`. Close cancels work, stops hardware, and clears `running`. Suspend cancels work and stops hardware if logically running; resume restarts if it was running.

## State and Persistence Behavior
`running` records the logical desired vibration across suspend/resume, while `vcc_on` prevents unbalanced regulator calls. No persistent storage exists.

## Dependencies and Integration Points
The driver uses platform devices, OF compatible `gpio-vibrator`, input FF memless, gpiod, regulator consumer APIs, and PM sleep callbacks.

## Risks and Test Signals
Risks include races around `running` and `vcc_on`, regulator enable failure leaving requested state true but hardware off, and no duration/magnitude scaling. Tests should cover strong/weak/zero playback, regulator failure on start, repeated starts/stops, close idempotence, and suspend/resume preserving logical running state.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio-vibra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio_decoder.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/gpio_decoder.c

## Purpose
`gpio_decoder.c` reads multiple GPIO input lines as a binary-encoded value and reports changes on an absolute input axis. It is intended for simple hardware selectors or encoded position devices.

## Important APIs, Types, and Functions
`struct gpio_decoder` stores the GPIO array, device, target axis, and last stable value. `gpio_decoder_get_gpios_state()` reads up to 31 GPIOs with `gpiod_get_array_value_cansleep()` into a bitmap and returns the decoded integer with `bitmap_read()`. `gpio_decoder_poll_gpios()` is the input polling callback and emits `input_report_abs()` when the value changes.

## Control Flow
Probe reads optional `linux,axis`, acquires an unnamed GPIO array as inputs, validates at least two and no more than 31 lines, reads optional `decoder-max-value` or defaults to `2^ndescs - 1`, allocates input, sets ABS axis parameters, configures polling with `input_setup_polling()`, and registers input. Polling performs all runtime event generation.

## State and Persistence Behavior
Only `last_stable` is retained to suppress duplicate reports. The driver does not debounce or persist state.

## Dependencies and Integration Points
It binds via OF compatible `gpio-decoder`, uses firmware properties, GPIO descriptor arrays, input polling, and absolute-axis reporting.

## Risks and Test Signals
Risks include no explicit debounce despite the `last_stable` name, default axis value of zero if missing, GPIO ordering assumptions, and max-value mismatch with hardware encoding. Tests should cover GPIO count validation, custom axis and max value, transition reporting only on changes, read errors, and bitmap decoding order.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/gpio_decoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/hisi_powerkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/hisi_powerkey.c

## Purpose
`hisi_powerkey.c` is a Hisilicon HI65xx PMIC power-key platform driver. It reports `KEY_POWER` down/up and toggles `KEY_RESTART` for a long-hold interrupt.

## Important APIs, Types, and Functions
Three ISR functions map named IRQs to input events: `hi65xx_power_press_isr()` reports power down and calls `pm_wakeup_dev_event()`, `hi65xx_power_release_isr()` reports power up and calls `pm_wakeup_event()`, and `hi65xx_restart_toggle_isr()` flips the current `KEY_RESTART` state based on the input key bitmap. `hi65xx_irq_info[]` maps firmware IRQ names `down`, `up`, and `hold 4s` to handlers.

## Control Flow
Probe allocates a devm input device, sets phys/name, advertises `KEY_POWER` and `KEY_RESTART`, loops over the three named IRQs with `platform_get_irq_byname()`, requests them with `devm_request_any_context_irq()` and `IRQF_ONESHOT`, registers input, and enables device wakeup. Runtime event flow is direct IRQ-to-input reporting.

## State and Persistence Behavior
The input key bitmap stores current key states. The restart key is toggled rather than emitted as a press/release pair. No persistent state exists.

## Dependencies and Integration Points
The driver depends on platform IRQ resources, input, PM wake events, and wakeup configuration. Binding is by platform driver name `hi65xx-powerkey`.

## Risks and Test Signals
Risks include long-hold toggle semantics leaving `KEY_RESTART` asserted until the next hold, all IRQs being mandatory, and no explicit remove logic beyond devm cleanup. Tests should cover all three IRQ paths, wake event durations, missing named IRQs, registration failure, and repeated hold toggles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/hisi_powerkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/hp_sdc_rtc.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/hp_sdc_rtc.c

## Purpose
`hp_sdc_rtc.c` is a legacy HP i8042 System Device Controller plus MSM-58321 battery-backed RTC module. It exposes RTC-like diagnostics through `/proc/driver/rtc` and uses HP SDC transactions to read the BBRTC and several i8042 timers.

## Important APIs, Types, and Functions
The code uses `hp_sdc_transaction`, `hp_sdc_enqueue_transaction()`, `hp_sdc_request_timer_irq()`, and `hp_sdc_release_timer_irq()` from the HP SDC subsystem. `hp_sdc_rtc_do_read_bbrtc()` constructs a long command sequence to read BCD RTC fields; `hp_sdc_rtc_read_bbrtc()` reads twice until stable because the MSM-58321 has no read latch. `hp_sdc_rtc_read_i8042timer()` serializes timer register access through semaphore `i8042tregs` and reads real-time, handshake, match, delay, and cycle timers. `hp_sdc_rtc_proc_show()` formats all data for procfs.

## Control Flow
Module init optionally gates on HP300 for m68k, initializes the timer semaphore, requests an SDC timer IRQ with a no-op ISR, creates `/proc/driver/rtc`, and logs module load. Proc reads synchronously issue SDC transactions, sleep on semaphores until results arrive, convert raw timer ticks into `timespec64`, and print failures if reads fail. Module exit removes procfs and releases the timer IRQ.

## State and Persistence Behavior
Global `epoch` defaults to 2000 and `i8042tregs` serializes timer output register use. There is no set-time path or persistent kernel state; hardware RTC/timer state is read-only from this module.

## Dependencies and Integration Points
It depends on HP SDC platform support, procfs/seq_file, semaphores, and RTC formatting constants. Despite living under input misc, it is not an input device.

## Risks and Test Signals
Risks include long synchronous proc reads, fragile hard-coded transaction sequence offsets, interruptible semaphore waits returning generic failures, proc entry collision with other RTC implementations, and limited architecture/platform coverage. Tests should validate stable double-read behavior, nonpresence detection, timer conversion, SDC enqueue failure paths, proc output for partial read failures, and init/exit resource pairing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/hp_sdc_rtc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ibm-panel.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/ibm-panel.c

## Purpose
`ibm-panel.c` implements an I2C slave input driver for an IBM operation panel. It receives fixed-length panel commands over I2C slave callbacks, validates them, and reports one of three configurable button keycodes.

## Important APIs, Types, and Functions
`struct ibm_panel` stores the current receive index, 11-byte command buffer, three keycodes, a spinlock protecting receive state, and input device. `ibm_panel_i2c_slave_cb()` handles slave events and accumulates writes. `ibm_panel_process_command()` validates command header and checksum, extracts the button number from byte 2, and reports key press/release based on bit 7. `ibm_panel_calculate_checksum()` implements the panel checksum over the command bytes.

## Control Flow
Probe allocates state and input, reads optional `linux,keycodes` array or defaults to `BTN_NORTH`, `BTN_SOUTH`, and `BTN_SELECT`, registers input capabilities, registers the input device, stores client data, and registers as an I2C slave. During an I2C write, `WRITE_REQUESTED` resets the index, `WRITE_RECEIVED` stores bytes up to the fixed command size, and `STOP` processes only exactly 11-byte commands. Read requests return `0xff`. Remove unregisters the slave callback.

## State and Persistence Behavior
Partial I2C command state lives in memory under a spinlock and is reset on stop or new write. Key states live in the input core. No data persists across driver lifetime.

## Dependencies and Integration Points
The driver depends on I2C slave support, input, OF compatible `ibm,op-panel`, firmware keycode property parsing, and spinlock guards.

## Risks and Test Signals
Risks include command rejection caused by any size mismatch, checksum/header assumptions, holding a spinlock while calling `input_report_key()`/`input_sync()`, and only three button slots. Tests should cover valid press/release commands, checksum failures, overlong and short commands, custom keycodes, and slave registration failure after input registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ibm-panel.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ideapad_slidebar.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/ideapad_slidebar.c

## Purpose
`ideapad_slidebar.c` supports the Lenovo IdeaPad Y550/Y550P slidebar. It installs an i8042 filter to intercept slidebar scancodes, reports `BTN_TOUCH` and `ABS_X`, and exposes a sysfs `slidebar_mode` control for the device's LED/input mode byte.

## Important APIs, Types, and Functions
Global state includes `slidebar_input_dev`, `slidebar_platform_dev`, `force`, and `io_lock`. `slidebar_pos_get()`, `slidebar_mode_get()`, and `slidebar_mode_set()` perform direct I/O port access at `0xff29..0xff2b`. `slidebar_i8042_filter()` tracks extended `0xe0` scancodes, consumes `e03b/e0bb` slidebar events, passes unrelated extended scancodes back with `serio_interrupt()`, and reports touch/position. Sysfs show/store call the mode accessors.

## Control Flow
Module init checks DMI unless `force` is set, allocates a platform device with the sysfs group, adds it, then probes a platform driver. Probe requests the I/O port range, allocates and configures input, installs the i8042 filter, registers input, and returns. Remove removes the filter, unregisters input, and releases ports. Module exit unregisters platform device and driver.

## State and Persistence Behavior
The slidebar mode byte resides in hardware and can be changed through sysfs. Driver state is global and single-device. The filter uses a static `extended` flag to track multi-byte scancodes.

## Dependencies and Integration Points
The driver depends on x86-style I/O ports, i8042 filter infrastructure, serio, DMI matching, platform devices, sysfs attribute groups, and input absolute/key reporting.

## Risks and Test Signals
Risks include global single-instance state, direct hard-coded I/O ports, scancode filter interference with keyboard traffic, static filter state races, and permissive `force` loading on unsupported systems. Tests should cover DMI gating, port busy failure, filter pass-through for non-slidebar extended scancodes, position reporting, sysfs mode read/write, and cleanup after probe failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ideapad_slidebar.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ims-pcu.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/ims-pcu.c

## Purpose
`ims-pcu.c` is a USB driver for IMS Passenger Control Unit devices. In application mode it creates button and optional gamepad input devices plus a keyboard-backlight LED; in bootloader mode it can request and flash Intel HEX firmware. It also exposes sysfs attributes for device identity, reset, firmware update, firmware status, and OFN sensor configuration.

## Important APIs, Types, and Functions
`struct ims_pcu` is the main state container: USB device/interfaces/endpoints/URBs, protocol framing buffers, command/response completions, firmware address range, sysfs-visible identity strings, LED/input subdevices, and mode flags. Input setup is split across `ims_pcu_setup_buttons()`, `ims_pcu_setup_gamepad()`, and report helpers. The byte-stuffed packet protocol is handled by `ims_pcu_process_data()`, `ims_pcu_send_command()`, `__ims_pcu_execute_command()`, and bootloader wrappers. Firmware flashing uses `request_ihex_firmware()`, `ihex_validate_fw()`, `ims_pcu_flash_firmware()`, and `ims_pcu_verify_block()`. USB lifecycle is handled by `ims_pcu_probe()`, `ims_pcu_disconnect()`, `ims_pcu_suspend()`, and `ims_pcu_resume()`.

## Control Flow
Probe allocates state, detects application versus bootloader from USB ID, parses the CDC union to locate control/data interfaces and endpoints, claims the data interface, allocates URBs/buffers, submits interrupt and bulk IN URBs, sets CDC line coding/state, and then initializes mode-specific features. Application mode queries identity, firmware/bootloader versions, reset reason, device ID, registers LED, buttons, and optional gamepad, then sets `setup_complete` so unsolicited button packets are reported. Bootloader mode queries flash bounds and starts an asynchronous firmware request. Disconnect from the control interface stops I/O, tears down mode-specific resources, frees buffers, and frees state.

## State and Persistence Behavior
Command state is serialized by `cmd_mutex` and matched by response type plus `ack_id`. Packet receive state tracks STX/DLE/checksum and is reset after ETX. Device identity strings are cached and can be updated through sysfs using `SET_INFO`. Firmware update status is a percentage or error code. `setup_complete` gates event reporting during teardown, with a memory barrier before input destruction.

## Dependencies and Integration Points
The driver integrates with USB CDC descriptors, USB core interface claiming, URBs, input, LED class, firmware loader, Intel HEX parser, sysfs attribute groups, unaligned helpers, and PM callbacks. User space sees evdev devices, LED class device `pcuN::kbd_backlight`, and USB-interface sysfs controls.

## Risks and Test Signals
Risks include complex protocol framing/chunking, command timeouts, response ID wrap rules, firmware address correction (`addr / 2`), bootloader disconnect/reconnect flow, sysfs writes racing with disconnect, and a notable cleanup risk where `ims_pcu_buffers_free()` frees `urb_in_buf` using `max_out_size` instead of `max_in_size`. Tests should cover packet escaping/checksum, unsolicited button/gamepad reports, command completion matching, CDC descriptor validation, firmware flashing/verify failure cases, sysfs visibility in both modes, suspend/resume URB restart, and disconnect during async firmware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/ims-pcu.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/iqs269a.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/iqs269a.c

## Purpose
`iqs269a.c` is an I2C input driver for the Azoteq IQS269A capacitive/inductive touch controller. It can register a keypad device for channel events and Hall switches, plus up to two slider devices that either emit gesture keycodes or raw `BTN_TOUCH`/`ABS_X` events.

## Important APIs, Types, and Functions
`struct iqs269_private` stores regmap, lock, switch descriptors, version info, cached system/channel register image, ATI completion, input devices, keycode maps, OTP option, selected channel, Hall mode, and ATI freshness. `iqs269_parse_prop()` and `iqs269_parse_chan()` translate device and child-node firmware properties into the cached `struct iqs269_sys_reg`. ATI sysfs helpers adjust channel tuning fields. `iqs269_dev_init()` writes the full configuration and triggers ATI. `iqs269_report()` reads flags, handles unexpected reset reinitialization, reports slider/keypad events, and completes ATI. `iqs269_irq()` wraps report handling and waits for RDY deassertion.

## Control Flow
Probe allocates state, initializes regmap/mutex/completion, reads OTP option from OF match data, validates product number, parses properties and child channels, writes device configuration, creates input devices, requests a threaded IRQ, waits up to two seconds for ATI completion and initial reports, then registers the keypad. Slider inputs are registered earlier during input init if enabled. Sysfs attributes allow reading counts and Hall bin values, toggling Hall enable, selecting a channel, editing RX/ATI fields, and triggering ATI reinitialization.

## State and Persistence Behavior
The driver maintains a cached big-endian image of IQS269 system/channel registers and marks ATI stale when tuning state changes. `ati_done` synchronizes probe and manual ATI triggers. Suspend/resume write the general settings register to enter/leave configured low-power modes while disabling the IRQ around unsolicited I2C accesses. Unexpected device reset in runtime reports causes the cached configuration to be rewritten.

## Dependencies and Integration Points
It binds to OF compatibles `azoteq,iqs269a`, `azoteq,iqs269a-00`, and `azoteq,iqs269a-d0`; uses I2C regmap with 8-bit registers and 16-bit values; consumes firmware properties and child nodes; exposes sysfs groups; and integrates with input key, switch, and absolute reporting plus PM sleep hooks.

## Risks and Test Signals
Risks include broad property surface with many bounds, endian-sensitive raw register images, IRQ disable windows for sysfs reads, raw slider versus gesture mode selection, Hall channel repurposing, and input reports for `KEY_RESERVED` entries if mappings are absent in some paths. Tests should cover product validation, each property bound failure, channel parsing, Hall-enabled and Hall-disabled reporting, slider raw/gesture behavior, ATI timeout, reset reinitialization, sysfs tuning invalidation, and suspend/resume register writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/iqs269a.c -->
