# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/stb6100_cfg.h

## Purpose
`stb6100_cfg.h` is a small static wrapper layer for board or demodulator code that wants separate get/set frequency and get/set bandwidth helpers while the real tuner API exposes a combined `.set_params` operation.

## Important APIs, Types, and Functions
- `stb6100_get_frequency()` calls `fe->ops.tuner_ops.get_frequency` if present.
- `stb6100_set_frequency()` writes `dtv_property_cache.frequency`, temporarily clears `bandwidth_hz`, calls tuner `.set_params`, then restores bandwidth.
- `stb6100_get_bandwidth()` calls tuner `.get_bandwidth` if present.
- `stb6100_set_bandwidth()` writes `dtv_property_cache.bandwidth_hz`, temporarily clears `frequency`, calls tuner `.set_params`, then restores frequency.

## Control Flow
Each helper reaches through `struct dvb_frontend_ops` to the installed `dvb_tuner_ops`. Setters mutate the frontend property cache before invoking `.set_params` so that the STB6100 driver changes only one dimension. Getters are simple pass-throughs.

## State and Persistence Behavior
State changes are limited to temporary edits of `fe->dtv_property_cache`. On successful `.set_params`, the original untouched field is restored. If `.set_params` returns an error, restoration has already occurred in this header's implementation for both setters.

## Dependencies and Integration Points
The wrapper depends on DVB frontend core headers and is meant to be included into C files rather than compiled as a standalone translation unit. It assumes the frontend already has tuner ops installed, commonly by `stb6100_attach()`.

## Risks and Edge Cases
The functions are `static`, so every includer gets private copies and names may collide with other static helpers in the same C file. There is no I2C gate control here; boards that require the demodulator repeater must use `stb6100_proc.h` or gate externally. Missing tuner callbacks are silently treated as success.

## Test Signals
Unit-style tests can use a fake `dvb_frontend` with stub tuner ops to verify cache mutation/restoration and error propagation. Hardware tests should confirm this wrapper is not used on boards that need explicit I2C repeater enablement.
