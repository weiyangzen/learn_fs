# sources/distributed-fs/ceph-client/drivers/media/test-drivers/vidtv/vidtv_tuner.h

## Purpose
`vidtv_tuner.h` defines the bridge-provided configuration for the virtual DVB tuner.

## Important APIs, Types, and Functions
The main type is `struct vidtv_tuner_config`. It contains a `struct dvb_frontend *fe`, mock power-up and tune delays, arrays of valid DVB-T, DVB-C, and DVB-S frequencies with `NUM_VALID_TUNER_FREQS` slots each, and `max_frequency_shift_hz`, the tolerated frequency offset for partial signal quality.

## Control Flow
The vidtv bridge fills this structure and passes it as I2C client platform data. `vidtv_tuner_i2c_probe()` copies it into private state and uses `fe` to install tuner callbacks.

## State and Persistence
The header defines configuration, not storage. At runtime the implementation copies the config per tuner instance and can replace it through the DVB tuner `set_config` callback.

## Dependencies and Integration Points
It includes `linux/types.h` and `media/dvb_frontend.h`, tying the tuner to DVB frontend registration. The valid frequency arrays are consumed according to `dtv_frontend_properties.delivery_system`.

## Risks and Edge Cases
`max_frequency_shift_hz` is declared as `u8`, which limits tolerance to 255 Hz despite the name implying Hz-scale tuning offsets. Array termination relies on zero entries; a full array with no zero terminator is valid because iteration is bounded, but zeros cannot represent valid frequency 0.

## Test Signals
Configuration tests should verify bridge-provided valid frequencies are honored for all supported systems and that `set_config` updates runtime behavior without requiring reprobe.
