
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda826x.h

## Purpose
`tda826x.h` declares the legacy attach interface for Philips TDA8262/TDA8263 DVB-S tuners.

## Important APIs, Types, and Functions
The public API is `tda826x_attach(struct dvb_frontend *fe, int addr, struct i2c_adapter *i2c, int has_loopthrough)`. When `CONFIG_DVB_TDA826X` is not reachable, an inline stub logs disabled Kconfig and returns `NULL`.

## Control Flow
The header gates the attach function at compile time. The real attach mutates the provided frontend by installing tuner ops and private state.

## State and Persistence Behavior
No state is declared here; runtime tuner state is allocated in the implementation and stored under `fe->tuner_priv`.

## Dependencies and Integration Points
It includes Linux I2C and DVB frontend headers and is consumed by satellite board/bridge drivers.

## Risks and Edge Cases
The in-place attach API requires callers to handle partial tuner setup ordering carefully. The `has_loopthrough` integer affects power state in sleep and should match board RF wiring.

## Test Signals
Compile tests should cover both Kconfig paths. Runtime tests should verify attach mutation of frontend ops, loop-through configuration, and caller handling of `NULL` attach.
