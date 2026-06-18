# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd-mbhc-v2.h

## Purpose

`wcd-mbhc-v2.h` defines the public contract for Qualcomm WCD MBHC v2 headset detection. It contains register-field identifiers, configuration structures, callback tables, IRQ tables, plug/button/micbias enums, and exported APIs with stubs when `CONFIG_SND_SOC_WCD_MBHC` is disabled. The source was read as a complete 343-line file.

## Important APIs, Types, and Functions

`enum wcd_mbhc_field_function` enumerates every abstract register field the algorithm may read/write, including detection enables, plug type, FSM, debounce, button result/source, electrical result, micbias control, PA/OCP fields, ADC fields, and moisture fields. `struct wcd_mbhc_config` stores DT/platform policy: button thresholds, headset/headphone thresholds, micbias selections, Type-C mux flag, ground/mic swap callback, line-in threshold, moisture options, and switch polarity. `struct wcd_mbhc_intr` names all IRQ numbers required by the implementation. `struct wcd_mbhc_cb` is the codec callback surface for bias, clock, threshold, impedance, micbias, pullup/pulldown, ground detection, ANC, and moisture operations.

The public functions are `wcd_dt_parse_mbhc_data()`, `wcd_mbhc_init()`, `wcd_mbhc_deinit()`, `wcd_mbhc_start()`, `wcd_mbhc_stop()`, `wcd_mbhc_event_notify()`, `wcd_mbhc_get_impedance()`, `wcd_mbhc_set_hph_type()`, `wcd_mbhc_get_hph_type()`, `wcd_mbhc_typec_report_plug()`, and `wcd_mbhc_typec_report_unplug()`.

## Control Flow

This header has no executable control flow beyond inline disabled-configuration stubs. With MBHC enabled, the implementation owns init/start/IRQ/workqueue flow. With MBHC disabled, parsing and most operations return `-ENOTSUPP` or `-EINVAL`, while `wcd_mbhc_start()` is a no-op success stub.

## State and Persistence Behavior

The header defines caller-provided config, callback, field, and IRQ state. The opaque `struct wcd_mbhc` runtime object is allocated by `wcd_mbhc_init()` and freed by `wcd_mbhc_deinit()`. All persistence is in memory, ALSA jack state, and codec registers.

## Dependencies and Integration Points

The header includes `<sound/jack.h>` and relies on ASoC component types through callback signatures. It is meant for codec drivers that map their register addresses into `WCD_MBHC_FIELD()` entries and provide hardware-specific callbacks around the common MBHC state machine.

## Risks and Edge Cases

The callback surface is broad and partially optional, so codec integrations must document which callbacks are mandatory for each feature. Disabled stubs are not all strict failures, which can hide missing MBHC support if callers do not check feature availability carefully. Field IDs and callback expectations must stay synchronized with `wcd-mbhc-v2.c`; adding a field without updating codec field tables silently reads/writes zero because missing fields are treated as absent.

## Test Signals

Build tests should cover both `CONFIG_SND_SOC_WCD_MBHC=y/m` and disabled configurations. Integration tests should verify each codec field table, IRQ table, and callback set against the common implementation, including button thresholds, Type-C path, impedance detection, and optional moisture hooks.
