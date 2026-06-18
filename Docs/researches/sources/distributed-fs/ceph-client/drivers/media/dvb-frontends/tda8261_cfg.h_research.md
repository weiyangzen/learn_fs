
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda8261_cfg.h

## Purpose
`tda8261_cfg.h` provides small static wrapper callbacks around frontend tuner ops, likely for demodulator configurations that expect separate get/set frequency and get bandwidth helpers.

## Important APIs, Types, and Functions
It defines `tda8261_get_frequency()`, `tda8261_set_frequency()`, and `tda8261_get_bandwidth()` as static functions. The first calls `fe->ops.tuner_ops.get_frequency` when present; the second calls `set_params` using the frontend property cache; the third returns a fixed `40000000` Hz bandwidth.

## Control Flow
Callers include this header into a C file and use the static functions as callbacks. Frequency set ignores its `frequency` argument and relies on `fe->dtv_property_cache.frequency` already being populated before calling tuner `set_params()`.

## State and Persistence Behavior
The header owns no state. It delegates to the tuner's own `tuner_priv` state and returns a constant bandwidth placeholder.

## Dependencies and Integration Points
It depends on DVB frontend ops and Linux logging macros from the include context. It is not a standalone public API; it is intended for inclusion in driver code that needs these callback symbols.

## Risks and Edge Cases
Because the set wrapper ignores its explicit `frequency` parameter, callers that do not update the property cache first will tune the wrong frequency. `get_bandwidth()` is a FIXME constant and may mislead demods that need actual tuner bandwidth. Static definitions in a header can create multiple private copies and naming conflicts if included broadly.

## Test Signals
Tests should cover delegation when tuner callbacks exist or are absent, error propagation from tuner callbacks, cache-dependent set frequency behavior, and consumers that rely on the fixed 40 MHz bandwidth.
