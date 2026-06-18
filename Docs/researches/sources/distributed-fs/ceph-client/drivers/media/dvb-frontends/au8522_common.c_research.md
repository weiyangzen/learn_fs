# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/au8522_common.c

## Purpose
`au8522_common.c` provides shared register access, state sharing, I2C gate control, LED control, and basic digital init/sleep helpers for AU8522 digital and analog modules.

## Important APIs, Types, And Functions
Exported functions include `au8522_writereg()`, `au8522_readreg()`, `au8522_i2c_gate_ctrl()`, `au8522_analog_i2c_gate_ctrl()`, `au8522_get_state()`, `au8522_release_state()`, `au8522_led_ctrl()`, `au8522_init()`, and `au8522_sleep()`. The file uses a global `hybrid_tuner_instance_list` and `au8522_list_mutex` with media hybrid-tuner helpers to share one `struct au8522_state` between DTV and V4L clients.

## Control Flow
Register writes send 16-bit register addresses with a write marker and one byte of data; reads send a read marker and receive one byte. Digital I2C gate control is suppressed when analog mode owns the chip, while analog gate control always writes the gate register. State acquisition/release is serialized through the global mutex. LED control enables GPIO output, clears previous LED bits, sets selected state, records `state->led_state`, and disables GPIO output when off. Digital init marks digital mode, clears cached frequency/modulation, powers/reset-writes register `0xa4`, and opens the gate. Sleep ignores requests if analog mode is active, otherwise turns off LED, powers down, and clears current frequency.

## State And Persistence
Shared runtime state lives in `au8522_state` from `au8522_priv.h` and is reference-managed through hybrid-tuner helpers. Important fields touched here include operational mode, current frequency, current modulation, LED state, config, and I2C adapter. No persistent storage exists.

## Dependencies And Integration Points
The file depends on Linux I2C, DVB frontend core, AU8522 private state, and exported-symbol linkage for `au8522_dig.c` and `au8522_decoder.c`. It mediates analog/digital coexistence on the same chip.

## Risks
Register helpers return `-1` instead of standard negative errno in some failures. Read failures still return the received byte buffer value. Operational-mode checks are race-sensitive because DVB and V4L paths can switch modes while frontend threads are shutting down. Shallow LED config pointers require parent lifetime care.

## Test Signals
Exercise simultaneous analog/digital open/close paths, state reuse counts, gate writes in both modes, LED transitions, and error handling under I2C transfer failure. Logs from `debug` parameter help confirm common helper sequencing.
