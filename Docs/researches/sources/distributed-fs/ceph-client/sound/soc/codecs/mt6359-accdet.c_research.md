# sources/distributed-fs/ceph-client/sound/soc/codecs/mt6359-accdet.c

## Purpose

This file implements the MT6359 PMIC accessory detector ASoC component. It detects headset/headphone plug state through PMIC EINT/ACCDET hardware, classifies headset buttons by calibrated voltage thresholds, reports jack and button state to ALSA jack core, and initializes ACCDET analog/digital debounce, micbias, EINT, and fast-discharge settings from device tree.

## Important APIs, types, and functions

`struct mt6359_accdet` is declared in the companion header and holds the ALSA jack pointer, device/regmap, parsed DTS data, capability flags, IRQ numbers, lock, plug/button state, calibration voltage, jack-detect status, and two single-thread workqueues. Capability bits in this C file describe PMIC EINT versus AP GPIO EINT, EINT0/EINT1/BI EINT routing, trigger type, key-count mode, and fast-discharge features.

Important functions include `mt6359_accdet_parse_dt()`, `mt6359_accdet_init()`, `config_eint_init_by_mode()`, `config_digital_init_by_mode()`, `accdet_set_debounce()`, `mt6359_accdet_irq()`, `mt6359_accdet_work()`, `mt6359_accdet_jd_work()`, `check_jack_btn_type()`, `check_button()`, `mt6359_accdet_jack_report()`, `mt6359_accdet_enable_jack_detect()`, and `mt6359_accdet_probe()`. EINT transition helpers are `adjust_eint_analog_setting()`, `adjust_eint_digital_setting()`, `mt6359_accdet_jd_setting()`, `recover_eint_analog_setting()`, `recover_eint_digital_setting()`, and `mt6359_accdet_recover_jd_setting()`.

## Control flow

Probe allocates private state, DTS data, and PWM/debounce storage, takes the parent MT6397 regmap, parses the `accdet` child node, initializes `res_lock`, requests the main ACCDET IRQ and the selected PMIC EINT IRQ, creates dedicated workqueues for ACCDET state and jack-detect state, registers an ASoC component, sets initial state to unplugged, then calls `mt6359_accdet_init()`.

Initialization toggles ACCDET sequence init and reset, programs ACCDET and EINT debounce values, configures PWM width/threshold/rise/fall delay, configures micbias voltage and headset mode, optionally enables analog fast discharge, and initializes PMIC EINT analog/digital detection when DTS selected PMIC EINT. Runtime IRQ handling reads `ACCDET_IRQ_ADDR`: an ACCDET interrupt is acknowledged and queues `accdet_work`; an EINT interrupt is acknowledged, EINT memory state is read into `jd_sts`, jack-detection settings are adjusted, and `jd_work` is queued.

`mt6359_accdet_work()` re-reads ACCDET state memory and classifies state 0 as headphone or pressed headset button, state 1 as headset or button release, and state 3/default as unplugged. It reports changes only while `jack_plugged` is true. `mt6359_accdet_jd_work()` handles plug-in by setting `jack_plugged`, pulsing sequence init, and enabling ACCDET; plug-out disables ACCDET, restores debounce/EINT settings, clears jack/button state, and reports unplug. `mt6359_accdet_enable_jack_detect()` maps ALSA button bits to input key codes and stores the jack pointer.

## State and persistence behavior

Runtime state is protected by `res_lock` across IRQ and workqueue operations. `jack_plugged`, `jack_type`, `btn_type`, `accdet_status`, `pre_accdet_status`, `cali_voltage`, and `jd_sts` are the in-memory state used to decide what to report. Parsed device-tree settings persist in `struct dts_data`, including mic voltage/mode, plugout debounce, EINT polarity/detection mode, key thresholds, EINT comparator settings, and PWM/debounce values. Hardware state persists in PMIC registers: IRQ clear/status bits, debounce registers, EINT analog switches/resistors/inverters, ACCDET enable, micbias, PWM, and fast-discharge configuration.

The code creates workqueues with `create_singlethread_workqueue()` but has no remove callback to destroy them on normal unbind after successful probe. Error paths destroy the first queue when the second creation fails.

## Dependencies and integration points

The driver depends on Linux OF parsing, regmap, IRQ, workqueue, mutex, input key codes, ASoC component registration, ALSA jack reporting, the MT6397 MFD parent, MT6359 register definitions from `mt6359.h`, and public types/macros from `mt6359-accdet.h`. It registers as platform driver `pmic-codec-accdet` and exposes exported `mt6359_accdet_enable_jack_detect()` for the main MT6359 codec or board integration to attach an `snd_soc_jack`.

The device-tree contract is the `accdet` child under the parent PMIC node with properties such as `mediatek,mic-vol`, `mediatek,plugout-debounce`, `mediatek,mic-mode`, `mediatek,pwm-deb-setting`, `mediatek,eint-level-pol`, `mediatek,eint-use-ap`, `mediatek,eint-detect-mode`, `mediatek,eint-num`, `mediatek,eint-trig-mode`, `mediatek,eint-use-ext-res`, `mediatek,eint-comp-vth`, `mediatek,key-mode`, and threshold arrays for three-key/four-key/tri-key modes.

## Risks and test signals

Risks include DTS array size/type assumptions, missing default threshold values when threshold properties are absent, incomplete support paths for AP GPIO EINT or bi-EINT capabilities, IRQ storms if clear/poll sequences fail, stale `cali_voltage` because this file classifies buttons from it but does not show an AUXADC update path, no successful-probe workqueue cleanup callback, and subtle races from queuing work while holding `res_lock` and then re-taking it in the worker. The interrupt handler returns `IRQ_NONE` on poll timeout after partially clearing hardware state, which can affect shared IRQ diagnostics.

Useful test signals are probe with all expected IRQs, correct parsed `caps` for EINT0 and EINT1 boards, plug-in and plug-out reports through `snd_soc_jack_report()`, headset versus headphone classification, button key events for all configured thresholds, no duplicate reports during debounce, EINT mode 1 through 4 behavior, interrupt clear poll success, repeated plug cycles without stuck ACCDET enable, and module unbind/load testing for workqueue lifetime issues.
