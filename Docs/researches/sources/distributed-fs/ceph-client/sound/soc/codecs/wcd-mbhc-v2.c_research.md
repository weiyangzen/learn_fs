# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-mbhc-v2.c

## Purpose

`wcd-mbhc-v2.c` implements the Qualcomm WCD MBHC v2 headset/headphone detection engine. It handles mechanical plug interrupts, ADC-based accessory classification, button press/release reporting, micbias/current-source policy, Type-C analog mux reporting, extension cable/lineout detection, cross-connection checks, over-current interrupts, and impedance reporting. The source was read as a complete 1635-line file.

## Important APIs, Types, and Functions

`struct wcd_mbhc` is the private runtime state: device/component/jack/config pointers, callback and IRQ tables, register-field table, delayed button work, plug-detection work, correction work, mutex, current plug type, jack status, button mask, impedance, headset type, ADC/legacy detection mode, and flags for switch IRQ, recording, force-linein, and Type-C behavior.

Exported functions are `wcd_mbhc_init()`, `wcd_mbhc_deinit()`, `wcd_mbhc_start()`, `wcd_mbhc_stop()`, `wcd_dt_parse_mbhc_data()`, `wcd_mbhc_event_notify()`, `wcd_mbhc_get_impedance()`, `wcd_mbhc_set_hph_type()`, `wcd_mbhc_get_hph_type()`, `wcd_mbhc_typec_report_plug()`, and `wcd_mbhc_typec_report_unplug()`. Important internal paths include `mbhc_plug_detect_fn()`, `wcd_correct_swch_plug()`, `wcd_mbhc_adc_hs_ins_irq()`, `wcd_mbhc_adc_hs_rem_irq()`, `wcd_mbhc_btn_press_handler()`, `wcd_mbhc_btn_release_handler()`, `wcd_check_cross_conn()`, `wcd_measure_adc_once()`, `wcd_measure_adc_continuous()`, and `wcd_mbhc_report_plug()`.

## Control Flow

Initialization validates required callback and register-field tables, allocates `struct wcd_mbhc`, initializes work items and a mutex, and registers seven threaded IRQs: mechanical switch, button press, button release, electrical insert, electrical remove, left OCP, and right OCP. `wcd_mbhc_start()` attaches config/jack pointers and calls `wcd_mbhc_initialise()`, which gets runtime PM, programs pullups, jack switch polarity, debounce, bias/clock, HS_VREF, and button thresholds.

Mechanical switch IRQ schedules `mbhc_plug_detect_work`. The work function toggles mechanical detection type. On insertion it enables micbias ramp, master bias, and starts ADC plug-type correction. On removal it disables FSM/current source, disables insert/remove IRQs, resets electrical detection, and reports removal for the current plug type.

ADC correction runs in `wcd_correct_swch_plug()`: it runtime-resumes the component, disables insert IRQ while classifying, checks ground/mic cross-connection repeatedly, measures IN2P through continuous and one-shot ADC modes, maps voltage to headphone/headset/high-impedance lineout, handles special-headset micbias bumping, optionally swaps ground/mic through a platform callback, runs a three-second stabilization loop, updates BCS and FSM current-source policy, reports the final jack type, sets `DETECTION_DONE` for headset button IRQs, and restores pull-down/runtime PM.

Button press IRQ ignores early presses within 250 ms of headset reporting, ignores non-headset and switch-handler overlap, maps hardware button result to `SND_JACK_BTN_0..5`, and schedules delayed reporting for long press. Release IRQ either reports long-release or short press+release and clears the button mask. Electrical removal validates against fake removals by polling ADC for at least 100 ms before reporting unplug.

## State and Persistence Behavior

Runtime state is in `struct wcd_mbhc`; jack status is reported through ALSA jack APIs and hardware state is programmed through the codec callback/register-field abstraction. Workqueue state persists until canceled by removal/deinit. Impedance values `zl` and `zr` are cached after successful detection and cleared on removal. There is no storage outside memory and hardware registers.

## Dependencies and Integration Points

The module depends on ASoC jack reporting, Linux IRQ/workqueue/mutex/runtime-PM APIs, and codec-provided `struct wcd_mbhc_cb` callbacks. Register access is indirect through `struct wcd_mbhc_field`, allowing different WCD codecs to reuse the algorithm with different register maps. It integrates with codec DAPM/micbias/PA events through `wcd_mbhc_event_notify()` so button current source and micbias state track playback/recording and PA usage.

## Risks and Edge Cases

The code assumes callback tables are complete enough for the selected configuration; some callbacks are optional but others are dereferenced after only the initial `mbhc_bias`/`set_btn_thr` validation. Several paths perform sleeps inside IRQ threads or work while holding `mbhc->lock`, so latency and lock ordering need care. Counter/state changes in micbias, fake removal, Type-C plug reporting, and work cancellation are race-prone if plug events arrive rapidly. `wcd_mbhc_get_impedance()` returns `-EINVAL` until both channels are nonzero. DT parsing only fills button high thresholds and basic polarity/threshold values; missing button thresholds default to 500 mV.

## Test Signals

High-value tests include insertion/removal of headset, headphone, high-impedance lineout, extension cable, Type-C analog accessory, and ground/mic-swapped plug; button short and long press/release; fake insertion/removal rejection; ADC threshold scaling for non-1.8 V micbias; impedance detect success/failure; OCP IRQ recovery; suspend/runtime-PM behavior during delayed correction work; and jack report masks for `SND_JACK_HEADSET`, `SND_JACK_HEADPHONE`, `SND_JACK_LINEOUT`, `SND_JACK_MECHANICAL`, and button bits.
