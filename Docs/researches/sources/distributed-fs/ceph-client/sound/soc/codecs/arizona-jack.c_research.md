# sources/distributed-fs/ceph-client/sound/soc/codecs/arizona-jack.c

## Purpose
`arizona-jack.c` implements ASoC jack detection support for Wolfson/Cirrus Arizona codecs. It handles mechanical jack insertion/removal, microphone detection, headset button resistance decoding, headphone/lineout impedance detection, accessory identification, clamp handling, runtime PM, MICVDD regulation, GPIO polarity control, IRQ setup/teardown, and device-property parsing.

## Important APIs, Types, And Functions
The implementation operates on `struct arizona_priv` and `struct arizona` from the Arizona codec/MFD code. Public exported entry points are `arizona_jack_codec_dev_probe()`, `arizona_jack_codec_dev_remove()`, and `arizona_jack_set_jack()`. Internal IRQ/work handlers include `arizona_jackdet()`, `arizona_micdet()`, `arizona_hpdet_irq()`, `arizona_hpdet_work()`, `arizona_micd_detect()`, and `arizona_micd_timeout_work()`.

Important helpers include `arizona_extcon_hp_clamp()`, `arizona_extcon_set_mode()`, `arizona_extcon_pulse_micbias()`, `arizona_start_mic()`, `arizona_stop_mic()`, `arizona_hpdet_read()`, `arizona_hpdet_do_id()`, `arizona_identify_headphone()`, `arizona_start_hpdet_acc_id()`, `arizona_micd_adc_read()`, `arizona_micd_read()`, `arizona_micdet_reading()`, `arizona_button_reading()`, `arizona_micd_set_level()`, and property parsers.

## Control Flow
Codec-device probe parses firmware properties when platform data is absent, gets MICVDD, initializes the mutex and delayed work, chooses device/revision-specific MICD clamp and HPDET IP behavior, selects MICD polarity modes, configures optional GPIOs, and returns without enabling detection. `arizona_jack_set_jack(component, jack, data)` enables detection when a jack is supplied and disables it when `NULL` is supplied.

Enable configures MICD timing/ranges/button key mapping, MICD clamp mode, polarity mode, jack pointer, IRQs for rise/fall jack events, MICDET, and HPDET, enables 32 kHz clock and analog jack detect, and puts MICVDD into bypass. The jack IRQ reports mechanical insertion/removal, starts mic detection or delayed HPDET accessory ID, tears down mic on removal, clears reports, waits for in-flight HPDET, and restores debounce. MICDET IRQ queues or runs detection work; detection work differentiates initial mic/headphone detection from button press/release decoding. HPDET IRQ reads impedance, steps hardware ranges when necessary, optionally performs accessory ID, reports headphone or lineout, unclamps outputs, and restarts MICD if a mic is present.

Disable unwinds IRQ wake, IRQ handlers, delayed work, MICD enable, regulator/runtime PM references, clamp, jack analog detect, and 32 kHz clock.

## State And Persistence
State persists in `arizona_priv`: current jack pointer/status, MICD mode, polarity GPIOs, HPDET ID GPIO, detection flags (`detecting`, `mic`, `hpdet_active`, `hpdet_done`, `hpdet_retried`), previous jackdet value, button mask/ranges, HPDET results, clamp state, work items, and mutex. Persistent hardware state is in Arizona regmap registers for MICD, accessory mode, HPDET, debounce, GPIO5, output clamp, and IRQ wake. MICVDD regulator mode and runtime PM references are carefully paired across start/stop paths.

## Dependencies And Integration Points
The file depends on the Arizona MFD core/register definitions, Arizona codec private header, regulator framework, GPIO descriptors, runtime PM, Linux IRQ/workqueue APIs, input key codes, firmware property APIs, ASoC DAPM, and `snd_soc_jack_report()`. Device properties include `wlf,hpdet-channel`, MICD timing/rate/debounce properties, `wlf,micd-configs`, `wlf,micd-force-micbias`, `wlf,micd-software-compare`, `wlf,jd-invert`, `wlf,gpsw`, `wlf,use-jd2`, and `wlf,use-jd2-nopull`.

## Risks
This file is concurrency-sensitive: IRQ handlers, delayed work, runtime PM, regulator enables, and jack removal races are coordinated by `info->lock` and explicit cancellation. Incorrect PM/regulator pairing can leak references or disable MICVDD while detection is active. HPDET cannot be aborted on removal, so the code waits for completion; failure there can delay unplug handling. Button thresholds require sorted ranges and are limited by `ARIZONA_MAX_MICD_BUTTONS` despite hardware supporting more. Device/revision conditionals mean clamp and HPDET behavior differs substantially across WM5102, WM5110, WM8280, WM8998, and WM1814. Property parsing does not reject `wlf,micd-configs` arrays whose length is not a multiple of three; integer division truncates.

## Test Signals
Test mechanical insertion/removal, duplicate IRQ suppression, mic/headphone/lineout classification, HPDET impedance range stepping for each IP version, slow-insert retry, MICD polarity flipping, button press/release mapping for configured thresholds, runtime suspend interactions, regulator bypass/enable pairing, IRQ wake setup/teardown, clamp output restoration, GPIO5 jack-detect mode, and property validation failures. Stress tests should repeatedly insert/remove during HPDET and MICD debounce windows.
