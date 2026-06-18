# sources/distributed-fs/ceph-client/include/trace/events/pwm.h

Purpose: Defines PWM framework tracepoints for waveform conversion, waveform read/write, and state get/apply operations. It exposes period, duty, offset, polarity, and enable state for PWM chips.

Important APIs/types/functions: Events include `pwm_round_waveform_tohw`, `pwm_round_waveform_fromhw`, `pwm_read_waveform`, `pwm_write_waveform`, and event-class `pwm` used by `pwm_apply` and `pwm_get`. Fields capture PWM device/chip identifiers and `struct pwm_waveform` or `struct pwm_state` values.

Control flow: PWM core or drivers emit conversion events when translating generic waveforms to/from hardware representations, read/write events when accessing hardware, and apply/get events around public state APIs.

State and persistence: No state is owned. It observes PWM device runtime state and hardware-facing waveform data; persistent behavior is in device registers and consumer configuration.

Dependencies and integration points: Depends on `linux/pwm.h` and tracepoints. It integrates with PWM consumers such as backlight, fans, haptics, regulators, and SoC PWM drivers.

Risks and test signals: Risks include unit conversion mistakes, overflow in period/duty/offset arithmetic, polarity confusion, and traces diverging from hardware state if drivers round differently. Test apply/get, disabled state, inverse polarity, edge periods/duties, waveform round-trip, and multiple PWM chips.

Source-read signal: read `sources/distributed-fs/ceph-client/include/trace/events/pwm.h` completely for this pass (178 lines, 3939 bytes). Final split target: `Docs/researches/sources/distributed-fs/ceph-client/include/trace/events/pwm.h_research.md`.
