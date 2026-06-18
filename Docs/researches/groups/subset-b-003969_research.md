# subset-b-003969 research

Grouped research for Linux input misc drivers and mouse Kconfig under the ceph-client source tree. Each source file section is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pmic8xxx-pwrkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/pmic8xxx-pwrkey.c

## Purpose
`pmic8xxx-pwrkey.c` is the Qualcomm PM8058/PM8921 PMIC power-key input driver. It exposes PMIC key press and release interrupts as `KEY_POWER`, configures the PMIC power-on debounce/pull-up register, handles wakeup from suspend, and programs PMIC shutdown/restart behavior so PS_HOLD drop produces the intended reset or shutdown action.

## Important APIs, Types, and Functions
The driver state is `struct pmic8xxx_pwrkey`, holding the press IRQ, parent regmap, and PMIC-specific shutdown callback. `pwrkey_press_irq()` and `pwrkey_release_irq()` report input key state. `pmic8xxx_pwrkey_probe()` parses `debounce` and `pull-up`, obtains the parent regmap, updates `PON_CNTL_1`, requests press/release IRQs, registers the input device, and enables wakeup. `pmic8xxx_pwrkey_shutdown()` chooses reset versus poweroff programming. PM8058-specific helpers `pm8058_disable_smps_locally_set_pull_down()`, `pm8058_disable_ldo_locally_set_pull_down()`, `pm8058_pwrkey_shutdown()`, and `pm8921_pwrkey_shutdown()` write regulator and sleep-control registers.

## Control Flow
Probe validates the requested debounce interval, converts it to the PMIC trigger-delay encoding, modifies `PON_CNTL_1`, registers two rising-edge interrupt handlers, then publishes an input device named `pmic8xxx_pwrkey`. IRQ flow is minimal: press reports `KEY_POWER=1`, release reports `KEY_POWER=0`, and both sync. Suspend/resume only toggles wake on the press IRQ when `device_may_wakeup()` is true. Shutdown first runs the PMIC-specific callback, then updates PON control bits for KPD/CBL pull-ups, USB power, and watchdog-reset behavior based on `system_state == SYSTEM_RESTART`.

## State and Persistence Behavior
Runtime state is small and device-managed except for the PMIC registers it programs. The input device stores key state in input core. The PMIC regmap updates persist in hardware until later firmware/kernel writes or power loss. PM8058 shutdown writes can change regulator enable/pull-down/mode bits and LDO22 voltage programming; this is intentionally persistent for the final shutdown sequence. Wakeup state is tracked by the device core and IRQ subsystem.

## Dependencies and Integration Points
The driver depends on platform/MFD enumeration, a parent regmap, DT compatibles `qcom,pm8058-pwrkey` and `qcom,pm8921-pwrkey`, input core, IRQ core, OF properties, and PM sleep helpers. It integrates with PMIC MFD register maps, system restart/poweroff sequencing, and userspace through evdev power-key events.

## Risks and Edge Cases
Debounce conversion uses `ilog2()` after validating a narrow range; invalid DT values fail probe. PM8058 shutdown ignores return values from several regulator pull-down helper calls before continuing, so partial rail programming can occur. The PM8058 advanced-to-legacy SMPS conversion is register-bank sensitive and can alter regulator state if masks or bank sequencing are wrong. Only the press IRQ is wake-enabled, so release-only wake behavior is not supported. The IRQ trigger is hard-coded as rising for both platform IRQs, assuming the PMIC IRQ parent encodes logical events.

## Test Signals
Useful tests include DT debounce boundary values, pull-up on/off register programming, press and release IRQ reporting, wake from suspend through the press IRQ, restart versus shutdown register writes for PM8058 and PM8921, injected regmap failures, and poweroff on PM8058 boards to verify rail pull-down and LDO22 safety programming.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pmic8xxx-pwrkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/powermate.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/powermate.c

## Purpose
`powermate.c` is a USB input driver for the Griffin PowerMate/SoundKnob and compatible Contour jog device. It reports knob button state as `BTN_0`, rotation as `REL_DIAL`, and exposes the device LED pulse configuration through an `EV_MSC`/`MSC_PULSELED` input event.

## Important APIs, Types, and Functions
`struct powermate_device` owns interrupt and control URBs, coherent input data, a USB control request, input device, LED state, an update bitmask, and a spinlock. `powermate_irq()` parses interrupt data and resubmits the interrupt URB. `powermate_sync_state()` serializes pending LED updates into vendor control transfers. `powermate_config_complete()` chains follow-up LED updates after asynchronous control completion. `powermate_pulse_led()` clamps and marks LED state changes. `powermate_input_event()` decodes `MSC_PULSELED`. `powermate_probe()` allocates USB/input resources and starts polling; `powermate_disconnect()` tears them down.

## Control Flow
Probe validates an interrupt-in endpoint, sends a class control request, allocates coherent buffers and two URBs, configures input capabilities, submits the interrupt URB before input registration, registers the input device, then forces a default LED configuration. Interrupt completions report button and dial values, then resubmit themselves. Userspace LED events update desired state under `pm->lock`; if no control URB is active, a vendor request is submitted. Control completion grabs the same lock and sends the next pending LED update until the bitmask is empty. Disconnect stops both URBs, unregisters input, frees buffers, and releases the state object.

## State and Persistence Behavior
Device state tracks the last desired LED static brightness, pulse speed/table, asleep/awake behavior, and `requires_update` bits. Hardware LED state persists on the USB device until later control requests or disconnect/power reset. Input key/relative state is transient through input core. The interrupt URB is continuously resubmitted while the device is connected; the control URB is single-flight and drains pending updates in priority order.

## Dependencies and Integration Points
The driver integrates with USB core, coherent DMA buffer APIs, input core, and evdev clients. It uses vendor/product IDs for Griffin and Contour devices and USB interrupt/control pipes. The `MSC_PULSELED` convention is the userspace integration point for LED programming.

## Risks and Edge Cases
`powermate_alloc_buffers()` returns `-ENOMEM` for the control request allocation but returns `-1` for coherent data failure, losing a precise errno. Probe submits the interrupt URB before registering the input device, so an unusually fast interrupt could race with input registration state. Payload sizes outside 3 to 6 bytes are warned about and clamped to max, which may mask unsupported devices. LED updates are coalesced, so intermediate user-requested LED states can be skipped. Disconnect relies on URB killing before freeing shared structures.

## Test Signals
Signals include USB probe on each ID, malformed endpoint rejection, button/rotation event delivery, high-rate dial events, LED command decoding for brightness/pulse/table/asleep/awake bits, concurrent LED updates while a control URB is active, disconnect while both URBs are pending, and kmemleak/USB fault-injection for allocation and submit failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/powermate.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pwm-beeper.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/pwm-beeper.c

## Purpose
`pwm-beeper.c` exposes a PWM-driven beeper as an input sound device. It maps `SND_BELL` and `SND_TONE` input events to PWM frequency and optional amplifier regulator control.

## Important APIs, Types, and Functions
`struct pwm_beeper` stores the input device, PWM, amplifier regulator, work item, requested period, bell frequency, suspend flag, and amplifier state. `pwm_beeper_on()` applies a 50 percent duty PWM state and enables the amplifier. `pwm_beeper_off()` disables amplifier then PWM. `pwm_beeper_event()` converts sound events to a nanosecond PWM period. `pwm_beeper_work()` applies the requested state. `pwm_beeper_suspend()` and `pwm_beeper_resume()` coordinate event locking with worker scheduling.

## Control Flow
Probe obtains the PWM, initializes it disabled, obtains the `amp` regulator, reads optional `beeper-hz` with a default of 1000 Hz, registers an input device with `EV_SND/SND_TONE/SND_BELL`, and stores driver data. Event callbacks reject non-sound or negative values, translate bell to configured frequency, write `beeper->period`, and schedule work unless suspended. The worker turns the PWM/regulator on for nonzero period and turns both off for zero. Close and suspend cancel work and force hardware off; resume clears the suspend flag and lets the worker restore any nonzero requested period.

## State and Persistence Behavior
The requested period is the persistent software intent across suspend/resume. `amplifier_on` tracks whether the regulator is enabled to avoid unbalanced regulator calls. Hardware PWM and regulator states persist until changed by the worker, close, suspend, or driver removal.

## Dependencies and Integration Points
The driver depends on platform/OF enumeration, `pwm-beeper` compatible, PWM core, regulator consumer API, input sound events, and device property `beeper-hz`. It integrates with userspace through evdev sound ioctls/events and with board hardware through the PWM and `amp` supply.

## Risks and Edge Cases
`HZ_TO_NANOSECONDS(value)` divides by the requested frequency; negative values are rejected but extremely large values can produce a zero or impractically small period. The period field is written without a dedicated mutex, relying on input event locking plus `READ_ONCE()` in the worker. Regulator enable failure disables the PWM but leaves the requested period intact, so later work may retry. Suspend uses the input `event_lock` specifically to avoid resubmitting work while setting `suspended`.

## Test Signals
Test `SND_BELL`, `SND_TONE`, zero stop events, invalid event types/codes, regulator failure paths, PWM apply failures, suspend/resume with an active tone, close while work is pending, and DT/property configurations with and without `beeper-hz`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pwm-beeper.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pwm-vibra.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/pwm-vibra.c

## Purpose
`pwm-vibra.c` implements a force-feedback rumble device driven by one required PWM, an optional direction PWM, an optional enable GPIO, and a `vcc` regulator.

## Important APIs, Types, and Functions
`struct pwm_vibrator` tracks the input device, enable GPIO, main and direction PWMs, regulator, work item, current magnitude, direction duty cycle, and regulator state. `pwm_vibrator_start()` enables power/GPIO and applies PWM duty from rumble strength. `pwm_vibrator_stop()` disables direction/main PWM, GPIO, and regulator. `pwm_vibrator_play_effect()` selects strong or weak rumble magnitude and schedules work. `pwm_vibrator_probe()` configures hardware resources and creates a memless FF device.

## Control Flow
Probe allocates state and input, gets `vcc`, optional `enable` GPIO, main `enable` PWM, initializes it off, optionally obtains a `direction` PWM, initializes it off, and reads `direction-duty-cycle-ns` or defaults to half the direction period. It registers `FF_RUMBLE` through `input_ff_create_memless()`. Playback stores the selected magnitude and schedules work. The worker starts hardware if level is nonzero and stops it otherwise. Close cancels work and stops hardware. Suspend stops active vibration; resume restarts if a nonzero level remains.

## State and Persistence Behavior
The last requested `level` persists in memory and is used to restart after resume. `vcc_on` tracks regulator balance. Hardware PWM duty, enable GPIO, and regulator state persist until `start`, `stop`, suspend, close, or removal changes them.

## Dependencies and Integration Points
The driver depends on PWM, regulator, GPIO descriptor, platform/OF properties, and input force-feedback core. Board integration names the main PWM `enable`, optional PWM `direction`, optional GPIO `enable`, and regulator `vcc`. Userspace sees a memless `pwm-vibrator` FF rumble device.

## Risks and Edge Cases
If applying the main PWM fails after the regulator and GPIO are enabled, `pwm_vibrator_start()` returns without unwinding those resources. If direction PWM apply fails, only the main PWM is disabled, while GPIO/regulator remain on until a later stop. Direction PWM absence is treated as `-ENODATA`; other errors fail probe except defer. Strength updates are not mutex-protected against suspend/close, relying on input and workqueue ordering.

## Test Signals
Tests should cover strong/weak rumble selection, zero stop, optional direction PWM present/absent/deferred, direction duty property, enable GPIO polarity, regulator and PWM error injection, suspend/resume during active rumble, close while work is pending, and repeated playback cycles for regulator balance.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/pwm-vibra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/qnap-mcu-input.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/qnap-mcu-input.c

## Purpose
`qnap-mcu-input.c` exposes QNAP MCU power-button state and MCU-controlled beeper commands through the Linux input subsystem. It polls the MCU for a slow power-key state and accepts `SND_BELL`/`SND_TONE` events to trigger MCU beeps.

## Important APIs, Types, and Functions
`struct qnap_mcu_input_dev` stores the input device, parent `struct qnap_mcu`, device pointer, beep work, and pending beep type. `qnap_mcu_input_poll()` sends `@CV` to read power state. `qnap_mcu_input_event()` validates sound events and schedules work. `qnap_mcu_input_beeper_work()` sends `@C2` for bell or `@C3` for tone through `qnap_mcu_exec_with_ack()`. Probe sets polling interval and input capabilities.

## Control Flow
Probe obtains the parent MCU from driver data, allocates input, configures `KEY_POWER`, `SND_BELL`, and `SND_TONE`, initializes beep work, sets up input polling at 500 ms, and registers the device. Polling sends a command, validates that the first three reply bytes echo the command, converts ASCII state byte `reply[3] - 0x30`, and reports `KEY_POWER`. Sound events reject unsupported or negative values, ignore value zero, remember the beep type, and schedule an asynchronous MCU command.

## State and Persistence Behavior
Persistent state is limited to the pending `beep_type` and the input poller registration. The MCU owns actual beep duration and power-key state. No local debounce or power-key persistence is maintained beyond input core's current key state.

## Dependencies and Integration Points
The driver depends on the QNAP MCU MFD interface, platform child enumeration, input polling, workqueues, and UAPI input event codes. It integrates with MCU command protocol and userspace evdev sound/key consumers.

## Risks and Edge Cases
The poller silently ignores MCU command errors, so userspace may see stale key state. A malformed echo logs an error every poll, potentially noisy on protocol mismatch. `reply[3] - 0x30` is not range-checked, so malformed ASCII can report values outside 0/1. `beep_type` is updated without locking before scheduling work; rapid sound events coalesce to the last type before the worker runs.

## Test Signals
Validate probe with a parent MCU, normal `@CV` replies for press/release, malformed echo handling, MCU errors, bell/tone events, zero/negative sound values, close canceling pending beep work, and polling interval behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/qnap-mcu-input.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/rave-sp-pwrbutton.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/rave-sp-pwrbutton.c

## Purpose
`rave-sp-pwrbutton.c` converts RAVE SP MFD event notifications into `KEY_POWER` input events. It is a small notifier-backed power-button driver for ZII RAVE SP devices.

## Important APIs, Types, and Functions
`struct rave_sp_power_button` contains an input device and notifier block. `rave_sp_power_button_event()` decodes packed RAVE SP actions through `rave_sp_action_unpack_event()` and `rave_sp_action_unpack_value()`. `rave_sp_pwrbutton_probe()` allocates/registers the input device and registers the event notifier with `devm_rave_sp_register_event_notifier()`.

## Control Flow
Probe creates an input device named after the platform device, enables `EV_KEY/KEY_POWER`, registers it, then registers a high-priority notifier. Notifier callbacks check for `RAVE_SP_EVNT_BUTTON_PRESS`, report the provided value as key state, sync, and return `NOTIFY_STOP`; unrelated events return `NOTIFY_DONE`.

## State and Persistence Behavior
The driver stores only the input-device pointer and notifier block. Button state is transient in input core. Notifier lifetime is devm-managed with the platform device.

## Dependencies and Integration Points
It depends on the RAVE SP MFD event-notifier API, OF compatible `zii,rave-sp-pwrbutton`, platform device binding, and input core. It integrates with userspace through evdev `KEY_POWER`.

## Risks and Edge Cases
The driver trusts notifier values as key states without normalization. Registering the input device before the notifier means notifier registration failure leaves a harmless input device with no event source. There is no wakeup setup here, so wake behavior depends on parent MFD/event infrastructure.

## Test Signals
Test notifier delivery of press/release values, unrelated events, notifier registration failure, OF matching, module unload/device removal, and userspace key events from the input node.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/rave-sp-pwrbutton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/rb532_button.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/rb532_button.c

## Purpose
`rb532_button.c` polls the RouterBOARD 532 S1 button and reports it as `BTN_0`. It handles board-specific GPIO/UART alternate-function switching needed to read the shared GPIO pin.

## Important APIs, Types, and Functions
`struct rb532_button` holds the button GPIO descriptor. `rb532_button_pressed()` disables UART through `set_latch_u5()`, switches the pin to GPIO input, reads it, restores alternate function through `rb532_gpio_set_func(GPIO_BTN_S1)`, and reenables UART. `rb532_button_poll()` reports `BTN_0`. `rb532_button_probe()` obtains the GPIO, sets polling, and registers the input device.

## Control Flow
Probe gets the named `button` GPIO, creates an input device named `rb532 button`, enables `BTN_0`, configures input polling every 100 ms, and registers. Each poll temporarily steals the shared pin from UART, reads the GPIO value, restores UART mode, reports the value, and syncs.

## State and Persistence Behavior
The driver persists only the GPIO descriptor and input poller. Hardware state is deliberately restored after every poll. Input core persists current button state between poll reports.

## Dependencies and Integration Points
It depends on the RC32434/RB532 platform headers and helper functions, GPIO descriptors, platform device enumeration, and input polling. Userspace sees a host-bus button input device.

## Risks and Edge Cases
Polling disrupts the UART alternate function briefly on every sample. Comments say the GPIO value is inverted, but the implementation reports the raw `gpiod_get_value()` result, so correctness depends on descriptor polarity or hardware behavior. Errors from direction/read/restore helpers are not handled. The polling interval trades latency for UART disturbance.

## Test Signals
Test button press/release while UART is active, GPIO descriptor polarity, polling interval behavior, platform GPIO acquisition failures, and repeated open/close/removal for mode restoration side effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/rb532_button.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/regulator-haptic.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/regulator-haptic.c

## Purpose
`regulator-haptic.c` presents a voltage-controlled regulator as a force-feedback rumble device. Rumble magnitude is mapped linearly between configured minimum and maximum microvolts, and nonzero magnitude enables the regulator.

## Important APIs, Types, and Functions
`struct regulator_haptic` stores device/input/regulator pointers, work item, mutex, active/suspended flags, voltage bounds, and current magnitude. `regulator_haptic_set_voltage()` maps 16-bit magnitude to voltage and toggles the regulator. `regulator_haptic_play_effect()` stores strong or weak rumble magnitude. `regulator_haptic_parse_dt()` reads `min-microvolt` and `max-microvolt`. Probe creates an exclusive `haptic` regulator-backed memless FF input device.

## Control Flow
Probe obtains platform data or DT voltage bounds, gets the `haptic` regulator exclusively, registers an `FF_RUMBLE` memless input device, and stores state. Playback records the selected magnitude and schedules work. Work runs under `haptic->mutex` and applies voltage unless suspended. Close cancels work and sets magnitude zero in hardware. Suspend obtains the mutex interruptibly, sets voltage zero, and marks suspended; resume clears suspended and reapplies any nonzero magnitude.

## State and Persistence Behavior
`magnitude`, `active`, and `suspended` are persistent driver state. The regulator voltage/enable state persists in hardware until the next work, close, suspend, or removal. The exclusive regulator handle prevents other consumers from changing the same supply while active.

## Dependencies and Integration Points
The driver depends on regulator consumer APIs, platform data or OF properties, input force-feedback core, workqueues, and PM ops. It integrates with userspace as `regulator-haptic` `FF_RUMBLE`.

## Risks and Edge Cases
There is no validation that `max_volt >= min_volt`; a bad platform/DT config can underflow the voltage range calculation. `regulator_haptic_close()` calls `regulator_haptic_set_voltage()` without taking the mutex, so it can race with suspend/resume work. `regulator_set_voltage()` is called even for zero magnitude before disabling, which may set the regulator to minimum voltage briefly. Suspend can return `-EINTR`, leaving device state unchanged.

## Test Signals
Tests should cover DT and platform-data voltage bounds, strong/weak rumble scaling, zero stop, invalid voltage ordering, regulator enable/disable/set-voltage failures, suspend/resume races with playback, close while work is active, and regulator balance through repeated effects.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/regulator-haptic.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/retu-pwrbutton.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/retu-pwrbutton.c

## Purpose
`retu-pwrbutton.c` exposes the Nokia Retu PMIC power button as `KEY_POWER`. It reads Retu status in a threaded IRQ and reports the inverted `PWRONX` status bit.

## Important APIs, Types, and Functions
The key handler is `retu_pwrbutton_irq()`, which retrieves `struct retu_dev` from input driver data, reads `RETU_REG_STATUS`, tests `RETU_STATUS_PWRONX`, and reports key state. `retu_pwrbutton_probe()` gets the platform IRQ, allocates an input device, stores the Retu parent data, requests a threaded IRQ, and registers input.

## Control Flow
Probe validates the IRQ and parent input resources, sets `EV_KEY/KEY_POWER`, registers a threaded IRQ with `IRQF_ONESHOT`, then registers the input device. On each interrupt, the handler reads the PMIC status register, reports pressed when `PWRONX` is clear, and syncs.

## State and Persistence Behavior
There is no custom runtime state object. The input device holds driver data pointing to the parent Retu MFD object. Hardware state is read-only from this driver.

## Dependencies and Integration Points
It depends on the Retu MFD API, platform child enumeration, IRQ core, and input core. It integrates with userspace through evdev `KEY_POWER`.

## Risks and Edge Cases
`retu_pwrbutton_irq()` does not check `retu_read()` errors separately, so a failed read could be interpreted as a button state depending on return value. There is no wakeup configuration in this file. The driver assumes the parent Retu object is valid for the input device lifetime.

## Test Signals
Test press/release status-bit transitions, Retu read errors, IRQ request failure, input registration failure, module removal, and userspace power-button event observation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/retu-pwrbutton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/rk805-pwrkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/rk805-pwrkey.c

## Purpose
`rk805-pwrkey.c` is a simple Rockchip RK805 PMIC power-key driver. It maps one falling interrupt to `KEY_POWER` press and one rising interrupt to release.

## Important APIs, Types, and Functions
`pwrkey_fall_irq()` reports `KEY_POWER=1`; `pwrkey_rise_irq()` reports `KEY_POWER=0`. `rk805_pwrkey_probe()` allocates the input device, obtains two platform IRQs, requests them with `devm_request_any_context_irq()`, registers input, stores driver data, and marks the device wake-capable.

## Control Flow
Probe creates `rk805 pwrkey`, enables `EV_KEY/KEY_POWER`, obtains IRQ 0 and IRQ 1, requests falling and rising handlers with edge flags and `IRQF_ONESHOT`, registers input, and calls `device_init_wakeup()`. Runtime IRQ flow only reports the corresponding key state and syncs.

## State and Persistence Behavior
State is entirely input-core and IRQ-core state; no custom structure is allocated. Wake capability persists in the device core.

## Dependencies and Integration Points
The driver depends on platform IRQ resources from the RK805 MFD, input core, IRQ core, and platform device binding `rk805-pwrkey`.

## Risks and Edge Cases
No suspend/resume ops explicitly enable IRQ wake despite `device_init_wakeup()`, so wake behavior relies on parent IRQ configuration. Both IRQs are requested against `&pwr->dev` rather than `&pdev->dev`, which ties devm cleanup to the input device lifecycle. The driver assumes IRQ ordering is fall then rise.

## Test Signals
Test IRQ ordering, press/release event delivery, any-context IRQ behavior, wake capability on target boards, error handling for missing IRQs, and repeated probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/rk805-pwrkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/rotary_encoder.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/rotary_encoder.c

## Purpose
`rotary_encoder.c` is a generic GPIO rotary encoder input driver. It decodes gray or binary encoded GPIO phases and reports movement as either a relative axis or bounded absolute position.

## Important APIs, Types, and Functions
`enum rotary_encoder_encoding` selects gray or binary. `struct rotary_encoder` stores input, mutex, step count, axis, relative/rollover flags, encoding, current position, GPIO array, IRQ list, and decoder state. `rotary_encoder_get_state()` samples GPIOs and converts gray encoding. `rotary_encoder_report_event()` reports relative or absolute movement. Three IRQ handlers implement full-period, half-period, and quarter-period decoding. Probe parses device properties and registers IRQs for all GPIOs.

## Control Flow
Probe reads `rotary-encoder,steps`, `rotary-encoder,steps-per-period` or legacy `half-period`, rollover, encoding, `linux,axis`, and relative-axis properties. It obtains a GPIO array, creates an input device, chooses the IRQ handler based on steps-per-period adjusted for the number of GPIOs, registers both-edge threaded IRQs for every GPIO, registers input, and sets wakeup from `wakeup-source`. Runtime IRQs take `access_mutex`, sample state, update decoder state, and report movement when a valid state transition is complete.

## State and Persistence Behavior
The driver persists position for absolute mode, last stable phase, armed flag, direction, and IRQ numbers. Input core stores current absolute/relative state. Wakeup state persists in device and IRQ core; suspend/resume enable or disable IRQ wake on every GPIO IRQ when configured.

## Dependencies and Integration Points
It depends on GPIO descriptor arrays, IRQ conversion, platform/OF/property APIs, input core, and PM wakeup helpers. Device-tree binding properties define axis, encoding, step granularity, rollover, and wake behavior.

## Risks and Edge Cases
If `rotary-encoder,steps` is missing for absolute mode, max may be zero and movement semantics become poor. Multi-GPIO encoders shift `steps_per_period` by `ndescs - 2`; invalid combinations fail probe. GPIO reads are `cansleep` inside a threaded IRQ, which is expected but latency-sensitive. Contact bounce can create extra transitions unless hardware debounce is present. Position clamping in non-rollover mode silently drops movement beyond endpoints.

## Test Signals
Test gray and binary encoders, relative and absolute axes, rollover versus clamped movement, 1/2/4 steps per period, multiple GPIO counts, bounce/noise behavior, wakeup suspend/resume, GPIO-to-IRQ failures, and property validation failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/rotary_encoder.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/rt5120-pwrkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/rt5120-pwrkey.c

## Purpose
`rt5120-pwrkey.c` reports the Richtek RT5120 PMIC power key through the input subsystem. It handles separate press and release IRQ names by reading the PMIC interrupt-status register to derive current key state.

## Important APIs, Types, and Functions
`struct rt5120_priv` stores parent regmap and input device. `rt5120_pwrkey_handler()` reads `RT5120_REG_INTSTAT` and reports `KEY_POWER` pressed when `RT5120_PWRKEYSTAT_MASK` is clear. `rt5120_pwrkey_probe()` obtains the regmap, named IRQs `pwrkey-press` and `pwrkey-release`, allocates input, registers it, and requests both threaded IRQs.

## Control Flow
Probe allocates state, fetches parent regmap, resolves named IRQs, registers an I2C-bus input device, and requests both IRQs with the same threaded handler. On interrupt, the handler reads status, reports the inverted status bit, and syncs.

## State and Persistence Behavior
Only the regmap pointer and input device are persistent. The key state is read from hardware on every IRQ and stored in input core. No register writes are performed.

## Dependencies and Integration Points
It depends on RT5120 MFD regmap setup, named platform IRQs, OF compatible `richtek,rt5120-pwrkey`, input core, and threaded IRQ handling.

## Risks and Edge Cases
If `regmap_read()` fails, the handler returns `IRQ_NONE`, which may interact badly with a shared/threaded interrupt line. Registering the input device before requesting IRQs can expose a device briefly without event source. No wakeup handling is configured. The status bit polarity must match the PMIC specification.

## Test Signals
Test press/release IRQs, regmap read errors, named IRQ absence, input registration failure, status polarity, OF matching, and suspend/wakeup behavior supplied by parent PMIC code.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/rt5120-pwrkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/sc27xx-vibra.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/sc27xx-vibra.c

## Purpose
`sc27xx-vibra.c` exposes Spreadtrum/Unisoc SC27xx PMIC vibrator control as a memless force-feedback rumble device. It turns PMIC LDO power-down bits on or off based on rumble strength and performs variant-specific initialization.

## Important APIs, Types, and Functions
`struct sc27xx_vibra_data` describes per-compatible bit masks. `struct vibra_info` stores input, work, regmap, data, base register, strength, and enabled flag. `sc27xx_vibra_set()` clears or sets LDO power-down and sleep power-down bits. `sc27xx_vibra_hw_init()` clears current-drive calibration bits for variants that need it. `sc27xx_vibra_play()` stores weak rumble magnitude and schedules work.

## Control Flow
Probe gets match data, parent regmap, base register from `reg`, allocates input, initializes hardware, creates a memless `FF_RUMBLE` input device, and registers it. Playback stores the weak magnitude and schedules work. The worker enables hardware only when strength is nonzero and currently disabled, or disables it when strength becomes zero and currently enabled. Close cancels work and disables if needed.

## State and Persistence Behavior
`strength` and `enabled` are persistent driver state. PMIC power-down and calibration bits persist in registers. The driver does not scale amplitude; strength is only on/off. Hardware is left disabled on close but not otherwise automatically on remove unless input close has run.

## Dependencies and Integration Points
It depends on parent PMIC regmap, OF compatibles `sprd,sc2721-vibrator`, `sprd,sc2730-vibrator`, and `sprd,sc2731-vibrator`, input FF core, workqueues, and `reg` property for the base address.

## Risks and Edge Cases
Only weak rumble magnitude is used, ignoring strong magnitude. Regmap update return values in `sc27xx_vibra_set()` are ignored, so state may claim enabled despite failed writes. No suspend/resume handling is present. Missing or wrong `reg` property fails probe. Strength changes are not protected by a mutex against close/work races.

## Test Signals
Test each compatible's bit masks, base-register parsing, weak/strong rumble behavior, zero stop, regmap failure injection, close while active, repeated enable/disable cycles, and suspend/resume on systems using this device.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/sc27xx-vibra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/sgi_btns.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/sgi_btns.c

## Purpose
`sgi_btns.c` polls SGI Indy/O2 volume buttons and reports debounced `KEY_VOLUMEDOWN` and `KEY_VOLUMEUP` events with scan codes.

## Important APIs, Types, and Functions
Architecture-specific `button_status()` implementations read SGI IP22 IOC panel bits or IP32 MACE audio-control bits. `struct buttons_dev` stores keymap and per-button debounce counters. `handle_buttons()` implements threshold-based press/release reporting. `sgi_buttons_probe()` registers a polled input device.

## Control Flow
Probe allocates state/input, copies the two-key map, configures `EV_MSC/MSC_SCAN` and `EV_KEY`, sets polling every 30 ms, and registers. Each poll reads the two-bit hardware status, increments counters until a press threshold of three polls, reports press once, reports release when a previously pressed counter clears, and resets counters.

## State and Persistence Behavior
Persistent state consists of the copied keymap and debounce counters. Hardware state is read-only except IP32 clears the button status bits by writing back masked audio-control state. Input core stores current key state.

## Dependencies and Integration Points
The driver depends on SGI IP22 or IP32 architecture headers/MMIO globals, input polling, platform device enumeration, and input sparse key capabilities. Userspace sees volume keys plus scan codes.

## Risks and Edge Cases
The file relies on exactly one architecture-specific `button_status()` being compiled. Poll debounce assumes 30 ms cadence, producing about 90 ms press threshold. IP32 status read clears bits, so missed polls or concurrent consumers could lose events. There is no explicit remove logic beyond devm/input cleanup.

## Test Signals
Test IP22 and IP32 builds, button press/release debounce, scan-code emission, volume key mapping, polling interval, and behavior with short pulses shorter than the threshold.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/sgi_btns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/soc_button_array.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/soc_button_array.c

## Purpose
`soc_button_array.c` converts Windows-compatible ACPI SoC tablet button descriptors into one or two `gpio-keys` platform devices. It supports fixed ACPI IDs, dynamic ACPI0011 `_DSD` HID-style descriptors, DMI quirks, and separate autorepeat/non-autorepeat groups.

## Important APIs, Types, and Functions
`struct soc_button_info` describes one button's name, ACPI GPIO index, event type/code, autorepeat, wakeup, and polarity. `struct soc_device_data` binds fixed button tables and optional device checks. `soc_button_lookup_gpio()` resolves ACPI-indexed GPIO and IRQ. `soc_button_device_create()` builds `gpio_keys_platform_data` and registers a `gpio-keys` child. `soc_button_get_button_info()` parses ACPI0011 `_DSD` button descriptors. `soc_device_check_MSHW0040()` filters Microsoft Surface generations via `_DSM`.

## Control Flow
Probe obtains match data, runs an optional check, chooses a fixed button table or parses ACPI0011 `_DSD`, verifies GPIO resources exist, then attempts to create two `gpio-keys` children: one for autorepeat and one for non-autorepeat. Creation counts buttons in the requested class, skips DMI-invalid ACPI indexes, resolves each GPIO/IRQ, applies low-level IRQ quirk handling when requested or DMI-matched, fills `gpio_keys_button` records, and registers a child platform device. Remove unregisters all children.

## State and Persistence Behavior
Persistent state is `struct soc_button_data` holding child platform devices. Child `gpio-keys` devices own input state, debounce, IRQ configuration, and wakeup behavior. Dynamically parsed ACPI button info is devm-allocated and freed after child creation. Module parameter `use_low_level_irq` persists for the module lifetime.

## Dependencies and Integration Points
The driver depends on ACPI, DMI, gpiolib, legacy GPIO numbers, IRQ configuration, `gpio-keys`, platform devices, and input event definitions. ACPI IDs include `PNP0C40`, `INT33D3`, `ID9001`, `ACPI0011`, `MSHW0028`, and `MSHW0040`. It integrates indirectly with userspace through the `gpio-keys` input devices it creates.

## Risks and Edge Cases
The low-level IRQ quirk deliberately bypasses `gpio_keys_button.gpio` and programs IRQ type to work around AML that mutates GPIO controller registers; wrong DMI matching can cause stuck IRQs or nonfunctional buttons. `-EPROBE_DEFER` from GPIO lookup is intentionally ignored for virtual GPIO resources, which can also hide real deferral needs. Dynamic `_DSD` parsing accepts only known HID usage combinations and turns unknowns into reserved keys. The platform data is allocated with devm but passed to a child device by copy size only for the base struct, relying on child registration semantics.

## Test Signals
Test fixed ACPI IDs, ACPI0011 descriptor parsing, Surface MSHW0040 `_DSM` filtering, DMI low-level IRQ systems, invalid ACPI index DMI skip, GPIO lookup failures including defer, autorepeat split into two children, wakeup flags, switch events for tablet/rotation/rfkill, and removal unregistering children.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/soc_button_array.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/sparcspkr.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/sparcspkr.c

## Purpose
`sparcspkr.c` provides input `EV_SND` beeper support for SPARC BBC and Grover speaker hardware. It registers platform drivers for two OF-compatible beeper blocks and maps bell/tone events to hardware timer/counter registers.

## Important APIs, Types, and Functions
`struct sparcspkr_state` holds input device, lock, event callback, and BBC/Grover hardware info. `bbc_count_to_reg()` maps PIT-style counts to BBC register codes. `bbc_spkr_event()` and `grover_spkr_event()` program their respective hardware. `sparcspkr_probe()` allocates/registers the shared input device. `bbc_beep_probe()` and `grover_beep_probe()` map OF resources and call the shared probe. Remove/shutdown functions turn the speaker off and unmap resources.

## Control Flow
Module init registers both platform drivers. The BBC probe reads root `clock-frequency`, maps one register range, and registers `Sparc BBC Speaker`. The Grover probe maps frequency and enable registers and registers `Sparc Grover Speaker`. Input sound events accept `SND_BELL` and `SND_TONE`, normalize bell to 1000 Hz, convert valid frequencies to counts, and under a spinlock either enable/program the speaker or disable it. Shutdown and remove force a zero bell event.

## State and Persistence Behavior
Runtime state is the mapped I/O pointers, input device pointer, event callback, and spinlock. Hardware timer/enable registers persist until programmed off or platform shutdown. No frequency state is cached beyond the hardware registers.

## Dependencies and Integration Points
The driver depends on SPARC OF platform devices, SBUS I/O accessors, input sound events, and OF resource mapping. Compatible strings are `SUNW,bbc-beep` and `SUNW,smbus-beep`.

## Risks and Edge Cases
Frequency values outside 21 to 32766 Hz are treated as off. BBC count conversion clamps low/high ranges to fixed codes. Register programming is low-level and architecture-specific; wrong resource indexes on Grover fail or program the wrong device. Probe uses non-devm input allocation and must explicitly unregister/free on all paths.

## Test Signals
Build and boot tests on BBC and Grover systems, bell and tone events across valid/invalid frequency ranges, remove/shutdown muting, OF resource mapping failures, and concurrent sound events under the spinlock.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/sparcspkr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/stpmic1_onkey.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/stpmic1_onkey.c

## Purpose
`stpmic1_onkey.c` reports STPMIC1 ONKEY falling/rising interrupts as `KEY_POWER` and programs optional PMIC long-press power-off behavior and pad pull-up behavior from device properties.

## Important APIs, Types, and Functions
`struct stpmic1_onkey` stores input device and falling/rising IRQs. `onkey_falling_irq()` reports press and `onkey_rising_irq()` reports release; both call `pm_wakeup_event()`. `stpmic1_onkey_probe()` parses `power-off-time-sec`, `st,onkey-clear-cc-flag`, and `st,onkey-pu-inactive`, writes PMIC regmap bits, requests named threaded IRQs, and registers input. PM ops enable/disable IRQ wake on both IRQs.

## Control Flow
Probe obtains the parent `struct stpmic1`, named IRQs `onkey-falling` and `onkey-rising`, computes turnoff-control bits from properties, updates `PKEY_TURNOFF_CR`, optionally sets `PADS_PULL_CR`, allocates input, requests both threaded IRQs, registers input, stores state, and enables device wakeup. Runtime IRQs report press/release and sync. Suspend/resume toggles wake for both IRQs when the device is wake-enabled.

## State and Persistence Behavior
The driver persists IRQ numbers and input pointer. PMIC turnoff and pad-control register writes persist in hardware. Wakeup state persists through device core and IRQ wake configuration.

## Dependencies and Integration Points
It depends on STPMIC1 MFD/regmap definitions, platform named IRQs, OF/property APIs, input core, IRQ core, and PM wakeup helpers. Compatible is `st,stpmic1-onkey`.

## Risks and Edge Cases
`power-off-time-sec` accepts only 1 through 16 seconds; zero and out-of-range values fail probe. Both IRQ wake enable calls ignore return values. PMIC register programming happens before input/IRQ registration, so later failures leave configuration changed. IRQ handlers assume the parent IRQ controller has already acknowledged status.

## Test Signals
Test property combinations and boundary values, regmap failures, falling/rising event delivery, wake from suspend by both edges, IRQ wake failure injection, and remove/reprobe after PMIC configuration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/stpmic1_onkey.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/tps65218-pwrbutton.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/tps65218-pwrbutton.c

## Purpose
`tps65218-pwrbutton.c` supports TI TPS65217 and TPS65218 PMIC power buttons. It reads variant-specific status registers on interrupt and reports `KEY_POWER`.

## Important APIs, Types, and Functions
`struct tps6521x_data` stores status register, button mask, and input name. `struct tps6521x_pwrbutton` stores device, regmap, input, data, and phys string. `tps6521x_pb_irq()` reads the status register, reports press or release, and calls `pm_wakeup_event()` on press. `tps6521x_pb_probe()` matches OF data, creates the input device, gets parent regmap, requests an edge-triggered threaded IRQ, and registers input.

## Control Flow
Probe selects TPS65217/TPS65218 data from OF, allocates state/input, configures an I2C input device, initializes wakeup, obtains IRQ 0, requests a rising/falling threaded IRQ, and registers input. The IRQ reads the PMIC status and reports key state based on the variant mask.

## State and Persistence Behavior
Persistent state is the regmap pointer, input device, and variant data. The driver does not write PMIC registers. Device wake capability is persistent in device core.

## Dependencies and Integration Points
Depends on TI TPS65217/TPS65218 MFD regmaps, OF compatibles, platform IRQs, input core, and PM wakeup. It also declares platform IDs for MFD child matching.

## Risks and Edge Cases
If `platform_get_irq()` fails, probe returns `-EINVAL` rather than the original error. `pwr->regmap` is not checked for NULL after `dev_get_regmap()`, so a missing parent regmap can crash in the IRQ. Regmap read failures are logged but still return `IRQ_HANDLED`. There are no suspend/resume IRQ wake hooks despite `device_init_wakeup()`.

## Test Signals
Test both PMIC variants, status mask polarity, missing regmap, missing IRQ, regmap read failures, press wake event, input event delivery, and platform/OF matching.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/tps65218-pwrbutton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/tps65219-pwrbutton.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/tps65219-pwrbutton.c

## Purpose
`tps65219-pwrbutton.c` supports the TI TPS65219 pushbutton. It reports separate push and release IRQs as `KEY_POWER` and configures PMIC registers to unmask the pushbutton interrupt and select pushbutton pin function.

## Important APIs, Types, and Functions
`struct tps65219_pwrbutton` stores device/input and phys string. `tps65219_pb_push_irq()` reports press and wakeup; `tps65219_pb_release_irq()` reports release. `tps65219_pb_probe()` requests IRQs, registers input, clears the interrupt mask, and writes the MFP configuration. `tps65219_pb_remove()` masks the interrupt again.

## Control Flow
Probe gets the parent `struct tps65219`, creates an I2C input device, obtains IRQ 0 and IRQ 1, requests both threaded handlers, registers input, then clears `TPS65219_REG_MASK_INT_FOR_PB_MASK` and configures `TPS65219_REG_MFP_2_CONFIG` for pushbutton mode. Remove sets the interrupt mask and warns on failure.

## State and Persistence Behavior
Driver state is minimal: input pointer, device pointer, phys string. PMIC interrupt-mask and MFP register writes persist after probe until remove or another consumer changes them. Device wake capability is set in the device core.

## Dependencies and Integration Points
Depends on TPS65219 MFD parent data/regmap, platform IDs, platform IRQ resources, input core, and PM wakeup. Userspace observes `KEY_POWER` on the input node.

## Risks and Edge Cases
Return values from post-registration `regmap_clear_bits()` and `regmap_update_bits()` are ignored, so probe can succeed with interrupts still masked or pin function wrong. IRQ get failures collapse to `-EINVAL`. IRQ names use `dev->init_name`, which may be NULL depending on device initialization. No explicit suspend/resume wake management is present.

## Test Signals
Test push/release IRQs, PMIC mask and MFP register writes, ignored regmap failure behavior, remove masking, missing IRQs, wake event delivery, and repeated bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/tps65219-pwrbutton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/tps6594-pwrbutton.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/tps6594-pwrbutton.c

## Purpose
`tps6594-pwrbutton.c` reports TI TPS6594 PMIC push and release interrupts as `KEY_POWER`. It is structurally similar to the TPS65219 power-button driver but without local PMIC register setup.

## Important APIs, Types, and Functions
`struct tps6594_pwrbutton` stores device/input and phys string. `tps6594_pb_push_irq()` reports press and wakeup; `tps6594_pb_release_irq()` reports release. `tps6594_pb_probe()` allocates the input device, obtains two IRQs, requests threaded handlers, and registers the input device.

## Control Flow
Probe creates an I2C input device named from the platform device, enables `EV_KEY/KEY_POWER`, marks the device wake-capable, obtains IRQ 0 and IRQ 1, requests threaded `IRQF_ONESHOT` handlers using resource names, and registers input. Runtime flow is direct press/release event reporting.

## State and Persistence Behavior
No hardware registers are written. State consists of the input device and device pointer. Wake capability persists in the device core.

## Dependencies and Integration Points
Depends on TPS6594 MFD platform child resources, platform IDs, IRQ core, input core, and PM wakeup. It includes TPS6594 and regmap headers but does not use regmap directly.

## Risks and Edge Cases
Missing IRQs return `-EINVAL` rather than specific errors. Handler names use `pdev->resource[0/1].name`, so malformed platform resources can provide NULL or misleading names. There are no explicit wake IRQ suspend/resume ops. The driver assumes IRQ 0 is push and IRQ 1 is release.

## Test Signals
Test correct platform resources, press/release event delivery, missing/misordered IRQs, wake behavior provided by parent PMIC, input registration failure, and module bind/unbind.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/tps6594-pwrbutton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/twl4030-pwrbutton.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/twl4030-pwrbutton.c

## Purpose
`twl4030-pwrbutton.c` supports TWL4030 and TWL6030 PMIC power buttons. It reads a PM_MASTER status register on IRQ and reports the power-button bit as `KEY_POWER`, with TWL6030-specific manual interrupt unmask/mask handling.

## Important APIs, Types, and Functions
`struct twl_pwrbutton_chipdata` describes the status register and whether manual IRQ unmasking is required. `powerbutton_irq()` reads the status register through `twl_i2c_read_u8()` and reports `KEY_POWER`. `twl4030_pwrbutton_probe()` matches chipdata, requests a threaded IRQ, registers input, optionally unmasks TWL6030 interrupts, and marks wakeup. `twl4030_pwrbutton_remove()` masks TWL6030 interrupts.

## Control Flow
Probe gets match data, stores it as platform data, allocates input, requests a rising/falling threaded IRQ, registers input, and then for TWL6030 unmasks line and status interrupt bits. IRQ reads the configured status register, reports key state if the read succeeds, calls `pm_wakeup_event()`, and syncs. Remove masks the manual TWL6030 interrupt bits.

## State and Persistence Behavior
Chipdata is stored as platform driver data. Input core persists key state. TWL6030 interrupt mask register updates persist until remove or another TWL consumer changes them. Device wake capability is recorded but no local suspend wake ops are present.

## Dependencies and Integration Points
Depends on TWL MFD I2C helpers, TWL6030 interrupt mask helpers, OF compatibles `ti,twl4030-pwrbutton` and `ti,twl6030-pwrbutton`, platform IRQs, and input core.

## Risks and Edge Cases
`platform_get_irq()` is called before checking its return and the result is passed to IRQ request without explicit negative handling. If the second TWL6030 unmask fails after the first succeeds, probe returns error with partial unmasking. Remove ignores mask errors. The IRQ reports `value & BIT(0)` directly, which is nonzero rather than normalized to 1.

## Test Signals
Test both compatibles, TWL status read success/failure, TWL6030 unmask/mask paths including partial failure, press/release events, IRQ resource absence, wakeup behavior, and removal cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/twl4030-pwrbutton.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/twl4030-vibra.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/twl4030-vibra.c

## Purpose
`twl4030-vibra.c` exposes the TWL4030 vibrator H-bridge as a memless force-feedback rumble device. It programs TWL audio/vibra registers, manages audio power/APLL resources, and disables LEDs that share the vibra PWM resource.

## Important APIs, Types, and Functions
`struct vibra_info` stores device/input, work item, enabled flag, speed, direction, and codec coexistence flag. `vibra_disable_leds()` clears LEDA/LEDB enable bits. `vibra_enable()` powers audio resource and H-bridge, then enables APLL. `vibra_disable()` powers down H-bridge and resources. `vibra_play_work()` applies speed/direction and `TWL4030_REG_VIBRA_SET`. `vibra_play()` maps FF magnitudes/direction to speed and direction.

## Control Flow
Probe requires the parent TWL4030 OF node, detects whether a codec child coexists, initializes work, creates a memless `FF_RUMBLE` input device, registers it, disables shared LEDs, and stores state. Playback stores speed from strong or weak magnitude and direction from effect direction, then schedules work. The worker checks whether audio routing owns vibra when coexistence is present, enables resources if needed, writes direction and PWM strength, or disables if speed is zero. Close and suspend cancel/disable active vibration; resume disables LEDs again.

## State and Persistence Behavior
`enabled`, `speed`, `direction`, and `coexist` persist in driver memory. TWL audio/vibra/LED registers persist in hardware. The driver intentionally disables LEDA/LEDB because they cannot coexist with vibra PWM.

## Dependencies and Integration Points
Depends on TWL MFD I2C helpers, TWL4030 audio resource APIs, input FF core, OF parent node, workqueues, and platform driver binding `twl4030-vibra`. It may coexist with TWL4030 codec/audio routing.

## Risks and Edge Cases
Most TWL I2C read/write return values are ignored, so hardware failures can desynchronize `enabled`. If codec coexistence indicates `TWL4030_VIBRA_SEL`, playback stops to avoid conflicting with audio. Strength mapping produces `256 - pwm`, with 1 as max and 255 as min per hardware comments. Explicit `input_ff_destroy()` on registration failure must stay consistent with input core ownership.

## Test Signals
Test rumble strength/direction mapping, coexistence with codec route, LED disable on probe/resume, suspend/close while active, TWL I2C failure injection, audio resource enable/disable balance, and repeated play/stop cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/twl4030-vibra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/twl6040-vibra.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/twl6040-vibra.c

## Purpose
`twl6040-vibra.c` controls the TWL6040 dual vibrator outputs as a memless force-feedback device. It handles left/right motor supplies, motor/driver resistance properties, overcurrent IRQs, errata sequencing, and amplitude code calculation.

## Important APIs, Types, and Functions
`struct vibra_info` stores device/input, work, IRQ, enabled flag, weak/strong speeds, direction, resistance values, two bulk regulators, and parent `struct twl6040`. `twl6040_vib_irq_handler()` handles overcurrent status. `twl6040_vibra_enable()` enables regulators, powers TWL6040, and enables vibra drivers with ES1.1 errata delay. `twl6040_vibra_code()` calculates VIBDAT codes from voltage/resistance/speed/direction. `twl6040_vibra_set_effect()` writes left/right VIBDAT registers. `vibra_play_work()` applies or disables effects.

## Control Flow
Probe locates the parent `vibra` OF child, reads resistance and optional supply voltage properties, requests the vibra IRQ, gets parent-device regulators `vddvibl` and `vddvibr`, optionally sets fixed regulator voltages, creates a memless `FF_RUMBLE` input device, and registers it. Playback stores weak/strong magnitudes and direction sign, then schedules work. The worker refuses to run when vibra routing is configured for audio, enables hardware if needed, writes amplitude codes, or disables when both strengths are zero. IRQ handling clears left/right vibra enable bits on overcurrent.

## State and Persistence Behavior
Driver state persists motor parameters, regulator handles, speeds, direction, enabled flag, and IRQ. Hardware state includes TWL6040 power, VIBCTL/VIBDAT registers, and regulator voltages/enables. Suspend and close cancel work and disable hardware if active.

## Dependencies and Integration Points
Depends on TWL6040 MFD APIs, regulator bulk APIs, OF properties under the parent `vibra` node, platform IRQs, input FF core, and workqueues. It integrates with TWL6040 audio/vibra routing through `twl6040_get_vibralr_status()`.

## Risks and Edge Cases
Resistance validation rejects only pairs where both driver and motor values are zero; a single zero can still cause divide-by-zero or unrealistic amplitude math. `regulator_get_voltage()` return values are not checked before division/scaling. Overcurrent handling disables registers but does not update `info->enabled`, so software may believe hardware is still active. Audio routing prevents effects but does not clear requested speeds.

## Test Signals
Test OF resistance/voltage parsing, divide-by-zero edge values, regulator enable/voltage failures, ES1.1 errata path, overcurrent IRQs for both channels, audio-route refusal, weak/strong/direction scaling, suspend/close cleanup, and repeated playback cycles.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/twl6040-vibra.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/uinput.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/uinput.c

## Purpose
`uinput.c` implements `/dev/uinput`, the userspace interface for creating virtual input devices, injecting input events, and servicing force-feedback upload/erase requests from the kernel input core back to userspace.

## Important APIs, Types, and Functions
`struct uinput_device` stores the virtual `input_dev`, lifecycle state, mutex, event ring buffer, wait queues, FF request slots, and locks. `struct uinput_request` represents pending FF upload/erase requests. Core paths are `uinput_open()`, `uinput_write()`, `uinput_read()`, `uinput_poll()`, `uinput_ioctl_handler()`, `uinput_create_device()`, and `uinput_destroy_device()`. Setup helpers include `uinput_dev_setup()`, `uinput_abs_setup()`, legacy write setup, and validation helpers. FF callbacks include `uinput_dev_upload_effect()`, `uinput_dev_erase_effect()`, and request submit/flush helpers.

## Control Flow
Opening `/dev/uinput` allocates a fresh `uinput_device`. Userspace either configures capabilities with ioctls plus `UI_DEV_SETUP`/`UI_ABS_SETUP` or writes legacy `struct uinput_user_dev`, then calls `UI_DEV_CREATE`. Creation validates abs/MT/FF configuration, installs input callbacks, registers the virtual input device, and marks state `UIST_CREATED`. After creation, writes inject one or more `struct input_event` records into the virtual device. Input-core output events and FF requests are queued into the small ring or request table so userspace can read events and complete FF ioctls. `UI_DEV_DESTROY`, close, or release tears the device down and flushes outstanding requests.

## State and Persistence Behavior
State transitions are `UIST_NEW_DEVICE`, `UIST_SETUP_COMPLETE`, and `UIST_CREATED`. Device name/phys strings are heap-owned and freed on destroy. Event output uses a 16-entry circular buffer protected by the input device event lock. FF requests use 16 slots, completions, and 30-second timeouts. The virtual input device persists in input core only between `UI_DEV_CREATE` and destroy/close.

## Dependencies and Integration Points
The file depends on the input core, miscdevice registration, UAPI `linux/uinput.h`, compat input conversion helpers, multitouch helpers, poll/read/write/ioctl file operations, and force-feedback core. It registers misc minor `UINPUT_MINOR` and devname `uinput`, consumed by libevdev, libinput tests, compositors, and other userspace virtual-device creators.

## Risks and Edge Cases
The output ring overwrites old unread events when full because head advances without tail management. State changes require careful lock ordering between `mutex`, `state_lock`, input `event_lock`, and request locks. FF requests time out after 30 seconds and must be completed or flushed during teardown to avoid hung input-core callers. Legacy and modern setup paths must keep abs validation consistent. Timestamp injection accepts only recent nonfuture timestamps, silently ignoring invalid ones. Compat FF upload copies truncated compat structures and intentionally does not support custom periodic waveforms.

## Test Signals
Test modern and legacy device creation, all `UI_SET_*BIT` ioctls, `UI_ABS_SETUP` size variants, invalid abs ranges and MT slot counts, event injection/read/poll, nonblocking behavior, timestamp acceptance/rejection, `UI_GET_SYSNAME`, FF upload/erase begin/end/timeout/flush, compat ioctls, destroy during pending requests, and close without explicit destroy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/uinput.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/wistron_btns.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/wistron_btns.c

## Purpose
`wistron_btns.c` supports legacy Wistron/Acer/Fujitsu/Medion laptop hotkeys and LEDs through a BIOS call interface. It selects a DMI/keymap, maps BIOS memory, polls a BIOS event queue, reports sparse-keymap input events, and optionally controls Wi-Fi, Bluetooth, mail, and Wi-Fi LEDs through BIOS calls.

## Important APIs, Types, and Functions
BIOS access is built around `struct regs`, `call_bios()`, `map_bios()`, `bios_pop_queue()`, `bios_attach()`, `bios_detach()`, `bios_get_cmos_address()`, `bios_get_default_setting()`, and `bios_set_state()`. DMI/keymap selection uses many `struct key_entry` arrays, `dmi_matched()`, `select_keymap()`, and `copy_keymap()`. Runtime input flow uses `handle_key()`, `poll_bios()`, `wistron_poll()`, and `setup_input_dev()`. LED integration uses `led_classdev` callbacks and PM hooks.

## Control Flow
Module init selects a keymap from module parameter or DMI, copies it out of init memory, maps BIOS code/data, registers a platform driver, and creates a platform device. Probe attaches to BIOS, gets the CMOS queue-length address, initializes Wi-Fi/Bluetooth state from BIOS defaults, registers LEDs when present, and sets up a polled input device. Polling reads queue length from CMOS, repeatedly pops BIOS queue entries, and handles key codes unless flushing. Key handling toggles BIOS Wi-Fi/Bluetooth state for special entries or reports sparse-keymap events. Suspend disables radios and suspends LEDs; resume restores saved radio state, resumes LEDs, and flushes stale BIOS events.

## State and Persistence Behavior
Global state includes BIOS mapping pointers, selected keymap, platform device, input device, CMOS queue address, radio availability/enabled flags, LED presence, and last keypress jiffies. BIOS radio/LED state is persistent platform firmware state. Poll interval changes dynamically between 500 ms idle and 100 ms burst after recent keys.

## Dependencies and Integration Points
The driver is x86 BIOS-specific and depends on DMI, sparse-keymap, input polling, LED class, CMOS RTC access, ioremap, inline x86 assembly, platform devices, and preemption/IRQ control. It integrates with userspace through an input device and LED class devices `wistron:green:mail` and `wistron:red:wifi`.

## Risks and Edge Cases
Calling firmware through inline assembly with interrupts disabled is inherently fragile and architecture-specific. BIOS signature detection and mapping can match unsupported systems; `force=1` can load with an empty keymap only for discovery. DMI tables are large and legacy; wrong matches can toggle radios or LEDs incorrectly. BIOS queue polling uses CMOS length and firmware pop calls without locking against firmware. LED and radio toggles are stateful BIOS side effects, and suspend powers radios off even if userspace expected them to remain active.

## Test Signals
Test known DMI matches, `keymap=` overrides, `force=1`, BIOS signature absence, queue polling and unknown key logging, sparse-keymap event delivery, Wi-Fi/Bluetooth toggle behavior, LED registration and brightness callbacks, suspend/resume radio restoration, and safe module unload unmapping BIOS resources.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/wistron_btns.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/wm831x-on.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/wm831x-on.c

## Purpose
`wm831x-on.c` reports the WM831x PMIC ON pin as `KEY_POWER`. The PMIC only interrupts on assertion, so the driver polls a status bit until the pin is released.

## Important APIs, Types, and Functions
`struct wm831x_on` stores input device, delayed work, and parent `struct wm831x`. `wm831x_on_irq()` schedules immediate polling. `wm831x_poll_on()` reads `WM831X_ON_PIN_CONTROL`, reports key state from `WM831X_ON_PIN_STS`, and reschedules while pressed. Probe allocates input, requests the mapped WM831x IRQ, and registers input; remove frees IRQ and cancels work.

## Control Flow
Probe resolves the MFD IRQ through `wm831x_irq()`, initializes delayed work, creates an input device with `EV_KEY/KEY_POWER`, requests a rising threaded IRQ, registers input, and stores state. On interrupt, work runs immediately. The worker reads ON-pin status, reports pressed/released, and if still pressed schedules itself again after 100 jiffies. Remove frees the IRQ and cancels delayed work.

## State and Persistence Behavior
Persistent state is the input pointer, parent PMIC pointer, and delayed work item. Key state is stored by input core. Hardware is read-only from this driver.

## Dependencies and Integration Points
Depends on WM831x MFD core/IRQ/register APIs, platform child enumeration, input core, threaded IRQs, and workqueues. It integrates with userspace through a `wm831x_on` input device.

## Risks and Edge Cases
Probe requests the translated IRQ but remove frees `platform_get_irq(pdev, 0)` without translating through `wm831x_irq()`, which can mismatch depending on IRQ mapping. The poll reschedule delay uses raw `100` jiffies rather than `msecs_to_jiffies()`. If status reads fail, the worker logs and continues polling by treating the key as pressed. No wakeup handling is configured.

## Test Signals
Test assertion IRQ, polling until release, register read errors, IRQ mapping/freeing correctness, remove while delayed work is pending, long press behavior, and userspace `KEY_POWER` delivery.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/wm831x-on.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/xen-kbdfront.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/xen-kbdfront.c

## Purpose
`xen-kbdfront.c` is the Xen paravirtual keyboard/pointer/multitouch frontend. It creates virtual input devices based on backend-advertised features, maps a shared ring page through a grant reference, binds an event channel, and translates Xen input ring events into Linux input events.

## Important APIs, Types, and Functions
`struct xenkbd_info` stores keyboard, pointer, multitouch input devices, shared `xenkbd_page`, grant reference, IRQ, xenbus device, phys string, and current MT contact. Event handlers include `xenkbd_handle_motion_event()`, `xenkbd_handle_position_event()`, `xenkbd_handle_key_event()`, `xenkbd_handle_mt_event()`, and dispatcher `xenkbd_handle_event()`. `input_handler()` drains the ring. Backend setup/teardown is handled by `xenkbd_connect_backend()` and `xenkbd_disconnect_backend()`. Xenbus lifecycle uses probe/remove/resume/backend-changed callbacks.

## Control Flow
Probe allocates state and a zeroed shared page, reads backend feature flags, optionally requests absolute pointer and multitouch support in xenstore, creates keyboard/pointer/multitouch input devices as enabled, then connects to the backend. Connection grants the ring page to the backend, allocates an event channel, binds it to `input_handler()`, writes ring ref/gref/event channel to xenstore in a transaction, and switches state to Initialised. IRQ handling drains all produced ring entries with memory barriers, dispatches events, advances `in_cons`, and notifies the backend. Resume reconnects with a fresh zeroed ring.

## State and Persistence Behavior
Persistent frontend state includes registered input devices, shared ring page, grant reference, bound IRQ/event channel, xenbus state, and current multitouch slot. The ring producer/consumer indices persist in the shared page and are reset on resume. Keyboard autorepeat state is inferred from input core's current key bitmap.

## Dependencies and Integration Points
The driver depends on Xen PV environment, xenbus, event channels, grant tables, Xen kbd/fb interface headers, input core, and multitouch helpers. It registers only for non-dom0 Xen PV devices and exposes standard Linux input devices to guests.

## Risks and Edge Cases
`xenkbd_handle_key_event()` tests `info->ptr->keybit` before checking `info->ptr`, so a backend sending key events when pointer creation is disabled can dereference NULL. Ring handling trusts backend event types and contact IDs; out-of-range MT contact IDs rely on input core behavior. Grant/event-channel cleanup must run on every error/resume/remove path. Feature negotiation writes can fail and downgrade abs/multitouch support. Memory barriers around ring producer/consumer indices are correctness-critical.

## Test Signals
Test keyboard-only, pointer-only, abs pointer, relative pointer, and multitouch configurations; backend feature-disable flags; xenstore write failures; event ring wraparound; key autorepeat; wheel direction; MT down/motion/shape/orient/up/sync; resume reconnect; backend close states; and malformed key events with disabled pointer to catch NULL dereference risk.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/xen-kbdfront.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/yealink.c -->
# sources/distributed-fs/ceph-client/drivers/input/misc/yealink.c

## Purpose
`yealink.c` drives the Yealink USB-P1K VoIP phone. It registers keypad input events, manages the phone LCD/LED/dialtone/ringtone through sysfs, and runs an asynchronous USB control/interrupt polling loop over Yealink control packets.

## Important APIs, Types, and Functions
`struct yld_status` mirrors device-visible LCD/icon/sound/key state. `struct yealink_dev` owns USB/input devices, interrupt and control URBs, coherent packet buffers, LCD map cache, sysfs mutex, shutdown flag, and master/copy status. LCD helpers include `setChar()`, `show_line*()`, `store_line*()`, icon handlers, and ringtone upload. Key helpers include `map_p1k_to_key()` and `report_key()`. USB flow uses `yealink_cmd()`, `yealink_set_ringtone()`, `yealink_do_idle_tasks()`, `urb_irq_callback()`, and `urb_ctl_callback()`. Probe/disconnect are `usb_probe()` and `usb_disconnect()`.

## Control Flow
USB probe validates an interrupt-in endpoint, allocates input and DMA buffers/URBs/control request, configures interrupt and control URBs, registers input keys for all mapped phone scancodes, stores interface data, clears LCD/icons, and writes the driver version to line 3. Input open forces a full status refresh, uploads the default ringtone, sends `CMD_INIT`, and starts the control/interrupt state machine. Control completion either submits the interrupt URB for key responses or asks `yealink_do_idle_tasks()` for the next LCD/icon/sound update. Interrupt completion records key-number changes or maps scancodes to Linux keys, then continues the state machine. Sysfs writes update `master` state under `sysfs_mutex`; idle tasks copy differences to the device.

## State and Persistence Behavior
`master` is the desired state for LCD bytes, LED, dialtone, ringtone, and key request; `copy` is the last sent state. `lcdMap[]` tracks display characters/icons. `key_code` records the currently pressed key so new scancodes release the old key first. USB URBs persist while the input device is open; `shutdown` prevents callbacks from resubmitting during close. Device LCD/ringtone/LED state persists on hardware until updated or disconnected.

## Dependencies and Integration Points
The driver depends on USB HID-interface matching for vendor/product `0x6993:0xb001`, input core, USB coherent DMA/control/interrupt URBs, seven-segment mapping, and the local Yealink packet definitions. Sysfs attributes under the USB interface expose line display, icon control, character map, and ringtone upload.

## Risks and Edge Cases
Sysfs writes update desired state but do not directly start URBs when the input device is closed, so changes may not reach hardware until open. `yealink_set_ringtone()` ignores command errors and sysfs ringtone passes a `const char *` as mutable `u8 *`. The async USB state machine has shared `ctl_data` and `master/copy` state with only sysfs-side mutexing; callbacks are not serialized by that mutex. `get_icons()` starts output at index 1, leaving `buf[0]` uninitialized. Disconnect cleanup unregisters input before clearing interface data and relies on input close killing URBs.

## Test Signals
Test probe with endpoint size validation, input open/close URB sequencing, keypad scancode mapping including shifted `#`, LCD line writes/reads, icon show/hide, ringtone upload, LED/dialtone/ringtone state updates, disconnect while URBs are active, sysfs writes while closed/open, and USB submit/control error injection.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/yealink.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/yealink.h -->
# sources/distributed-fs/ceph-client/drivers/input/misc/yealink.h

## Purpose
`yealink.h` defines the Yealink USB-P1K control-packet ABI and the macro-expanded LCD segment/icon map used by `yealink.c`.

## Important APIs, Types, and Functions
`struct yld_ctl_packet` is the packed 16-byte USB control payload with command, size, big-endian offset, 11 data bytes, and checksum. Command constants include `CMD_INIT`, `CMD_KEYPRESS`, `CMD_SCANCODE`, `CMD_LCD`, `CMD_LED`, `CMD_RING_VOLUME`, `CMD_RING_NOTE`, `CMD_RINGTONE`, and `CMD_DIALTONE`. When included with `_SEG` and `_PIC` defined, the header emits LCD segment and pictogram map entries plus line offsets and sizes.

## Control Flow
There are no functions. The first include provides packet and command definitions. The second include from inside `lcdMap[]` in `yealink.c` expands the LCD layout into map entries, then undefines `_SEG` and `_PIC`. Packet commands are filled by `yealink.c` and sent over USB control transfers.

## State and Persistence Behavior
The header owns no runtime state. It defines the wire layout for state that persists on the phone: LCD bytes, LED state, ringtone/dialtone state, ringtone notes, and key polling/scancode requests.

## Dependencies and Integration Points
It depends on Linux integer types, big-endian annotation, and compile-time `_SEG`/`_PIC` macro definitions. Its constants are tightly coupled to `struct yld_status`, `lcdMap[]`, and `yealink_cmd()` checksum/control-transfer logic in `yealink.c`.

## Risks and Edge Cases
The header is intentionally dual-use: ordinary include guard covers packet definitions, while the LCD map is outside the guard and only expands when macros are defined. Moving the map inside the guard would break the second include. The packed packet layout and checksum size must remain exactly aligned with device firmware. LCD offsets and masks must match `struct yld_status` byte layout.

## Test Signals
Test compile expansion of both include modes, `sizeof(struct yld_ctl_packet) == 16`, command packet formation, LCD line offsets/sizes, all icon names, and visible LCD updates for representative segment characters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/misc/yealink.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/input/mouse/Kconfig

## Purpose
`drivers/input/mouse/Kconfig` defines the build-time configuration menu for Linux mouse and touchpad drivers. It gates PS/2 protocol extensions, serial/USB/I2C/SMBus/GPIO/platform mouse drivers, and architecture-specific mouse support.

## Important APIs, Types, and Functions
The top-level `menuconfig INPUT_MOUSE` controls visibility but does not itself affect the kernel. Key symbols include `MOUSE_PS2` and its protocol extensions (`ALPS`, `BYD`, `LOGIPS2PP`, `SYNAPTICS`, `ELANTECH`, `TRACKPOINT`, etc.), companion SMBus helpers, `MOUSE_SERIAL`, Apple USB touchpad drivers, `MOUSE_CYAPA`, `MOUSE_ELAN_I2C` plus transport suboptions, Amiga/Atari/RiscPC/DEC/GPIO/Maple/Synaptics variants. Dependencies and selects wire these options to SERIO, I2C, USB, DMI, platform architecture, and helper libraries.

## Control Flow
There is no runtime flow. Kconfig evaluation exposes options under `INPUT_MOUSE`, enforces dependencies, applies defaults, and sets `CONFIG_*` symbols. Kbuild then includes or omits driver objects/modules according to the selected symbols. Boolean PS/2 protocol extensions are built into the `psmouse` driver when enabled.

## State and Persistence Behavior
The file persists configuration state in `.config`. Tristate options determine built-in/module/disabled driver builds; boolean extension options alter compiled feature sets inside composite drivers. It has no runtime driver state.

## Dependencies and Integration Points
The menu integrates the input subsystem with SERIO, I8042/GSC PS/2 controllers, I2C/SMBus, USB host support, architecture symbols (`AMIGA`, `ATARI`, `ARCH_ACORN`, `MAPLE`), DMI, hypervisor guest support, and helper selections such as `CRC_ITU_T`, `SERIO_LIBPS2`, and `MOUSE_PS2_SMBUS`.

## Risks and Edge Cases
Defaults enable many PS/2 extensions, so build/test matrices must cover both expert-disabled and default-enabled combinations. Transport suboptions such as `MOUSE_ELAN_I2C_I2C`/`SMBUS` can create partially enabled drivers if dependencies change. `select` statements force lower-level support and can expose unmet dependency bugs. Help text includes legacy URLs and may lag current userspace recommendations.

## Test Signals
Test Kconfig resolution for `y/m/n` where applicable, dependency-disabled visibility, allmodconfig/allnoconfig/randconfig builds, PS/2 extension combinations, I2C/USB dependency matrices, architecture-specific build coverage, and expected module names such as `psmouse`, `sermouse`, `appletouch`, `bcm5974`, `cyapa`, `elan_i2c`, `gpio_mouse`, and `synaptics_usb`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/input/mouse/Kconfig -->
