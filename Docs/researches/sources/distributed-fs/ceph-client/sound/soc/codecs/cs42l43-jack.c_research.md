# sources/distributed-fs/ceph-client/sound/soc/codecs/cs42l43-jack.c

## Purpose

`cs42l43-jack.c` implements CS42L43 accessory detection. It configures DT/firmware-defined jack detection parameters, controls headset bias, performs tip/ring/type/load detection, handles button press/release and bias-clamp interrupts, supports manual jack override controls, and reports ALSA jack states.

## Important APIs, Types, and Functions

- `cs42l43_set_jack()` stores the `snd_soc_jack`, parses properties such as button resistance thresholds, detect time, bias ramp/sense, tip/ring debounce/inversion/pullups, programs detection registers, and enables optional ring sense.
- `cs42l43_start_hs_bias()` and `cs42l43_stop_hs_bias()` control headset bias and clamp settings.
- `cs42l43_button_press()` reads the hardware DC detect result, converts it to resistance, maps it against up to six button thresholds, and reports `SND_JACK_BTN_0` through `BTN_5`.
- `cs42l43_button_release()` clears button reports.
- `cs42l43_bias_sense_timeout()` restores automatic bias clamp behavior after a clamp interrupt.
- `cs42l43_start_load_detect()`, `cs42l43_stop_load_detect()`, and `cs42l43_run_load_detect()` temporarily reconfigure ADC/headphone/load-detect hardware to classify headset, headphone, or line-out loads.
- `cs42l43_run_type_detect()` runs automatic CTIA/OMTP/3-pole/open-circuit detection, then invokes load detection when needed.
- `cs42l43_tip_sense_work()` is the delayed worker that performs insertion/removal processing and ALSA jack reporting.
- `cs42l43_jack_get()` and `cs42l43_jack_put()` implement the "Jack Override" ALSA control.

## Control Flow

Jack setup resumes the device, takes `jack_lock`, parses firmware properties, writes debounce/type-detect/bias registers, and stores the jack pointer. Tip-sense IRQs cancel pending work and queue `tip_sense_work` after configured debounce. The worker resumes the device, takes `jack_lock`, reads debounced tip/ring status, and branches between insertion and removal.

On insertion, SoundWire systems keep a runtime PM reference while the jack is present. Ring-sense absence can report optical. Otherwise the worker starts type detection: it enables bias, starts automatic type detect, waits for the `type_detect` completion, disables the mode, and classifies the result. CTIA/OMTP and some type values run load detection as a microphone-bearing headset; 3-pole runs load detection without mic and maps impedance to headphone or line-out; open circuit reports extension. Headsets start bias and button detection before reporting.

On removal, override state is cleared, button/bias and manual switch state are reset through `cs42l43_clear_jack()`, all jack bits are reported cleared, and the SoundWire jack-present PM reference is dropped.

## State and Persistence Behavior

Persistent jack state lives in `struct cs42l43_codec`: `jack_hp`, `use_ring_sense`, debounce/bias/detect properties, button thresholds, delayed work objects, completions for type/load detection, booleans for load/button/jack presence, `jack_override`, and `suspend_jack_debounce`. Load detection temporarily changes headphone, ADC, bias, clamp, volume ramp, adaptive power, and load-detect registers and then restores cached `adc_ena`/`hp_ena`.

## Dependencies and Integration Points

The file depends on the CS42L43 MFD core/regmap, ASoC component/jack/control APIs, runtime PM, firmware properties, completions supplied by IRQ handlers in `cs42l43.c`, and delayed work queues. Its public functions are declared in `cs42l43.h` and used by the main codec component.

## Risks

This code is highly timing-sensitive. Type and load detection depend on completions arriving before fixed timeouts; false insertions after suspend are mitigated by extra debounce. Button resistance conversion can divide around small hardware values and maps thresholds with a first-less-than rule, so malformed `cirrus,buttons-ohms` can misclassify buttons. Load detection temporarily powers down headphones and changes DAPM-protected hardware while holding the DAPM mutex. Manual override bypasses automatic detection and must restore all switch/bias/clamp state on exit. Runtime PM references on SoundWire jack presence must remain balanced.

## Test Signals

Test property parsing with valid, missing, malformed, and too-many button thresholds; plug/unplug debounce including resume; CTIA, OMTP, headphone, line-out, optical, extension, and removal reports; button press/release thresholds; bias clamp recovery; manual jack override modes; load-detect timeout handling; and SoundWire runtime PM reference balance while a jack is inserted.
