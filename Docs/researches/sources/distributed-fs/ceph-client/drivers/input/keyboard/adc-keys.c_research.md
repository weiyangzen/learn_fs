# sources/distributed-fs/ceph-client/drivers/input/keyboard/adc-keys.c

Purpose: implements a polled input driver for buttons wired through a resistor ladder to an IIO voltage ADC channel.

Important APIs/types/functions: `struct adc_keys_button` maps threshold voltage to keycode. `struct adc_keys_state` stores the IIO channel, number of keys, last reported key, key-up voltage, and keymap. `adc_keys_poll` reads and reports state. `adc_keys_load_keymap` parses firmware child nodes. `adc_keys_probe` wires the platform device to input polling.

Control flow: probe obtains the `"buttons"` IIO channel, validates it is `IIO_VOLTAGE`, reads `keyup-threshold-microvolt`, loads child-node `press-threshold-microvolt` and `linux,code` entries, allocates input, declares key bits, enables autorepeat if requested, sets up polling, optionally applies `poll-interval`, and registers the input device. Polling reads processed millivolts, selects the closest configured key threshold, treats the key-up threshold as no key when closer, releases the previous key if it changed, reports the current key, syncs, and remembers it.

State and persistence: `last_key` persists between polls to emit releases. Firmware properties define the keymap and thresholds; no runtime settings persist outside memory.

Dependencies and integration: depends on platform devices, firmware properties/OF matching `"adc-keys"`, IIO consumer APIs, and input polling helpers.

Risks: nearest-threshold matching can misreport when voltages overlap or drift. Failed ADC reads force release by substituting key-up voltage. Multiple simultaneous buttons on a resistor ladder are not represented. Unit conversion divides microvolts by 1000, matching processed millivolt expectations.

Test signals: device-tree/property tests for missing thresholds/keycodes, IIO mock reads near each threshold and key-up voltage, ADC error injection, autorepeat flag checks, and `evtest` validation of press/release transitions.
