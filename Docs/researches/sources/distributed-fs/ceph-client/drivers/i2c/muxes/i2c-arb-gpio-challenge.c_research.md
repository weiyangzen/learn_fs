# sources/distributed-fs/ceph-client/drivers/i2c/muxes/i2c-arb-gpio-challenge.c

Purpose: single-channel I2C arbitrator using two GPIO lines in a challenge/response protocol for two masters sharing a bus.

Important APIs/types: `struct i2c_arbitrator_data` stores our claim GPIO, their claim GPIO, slew delay, retry interval, and total wait time. The mux callbacks are `i2c_arbitrator_select()` and `i2c_arbitrator_deselect()`.

Control flow: probe requires OF, allocates an `I2C_MUX_ARBITRATOR` mux core, gets `our-claim` output and one `their-claim` input, rejects more than one peer, reads timing properties, resolves `i2c-parent`, and adds one child adapter. Select asserts our claim, waits for GPIO slew, polls for the other master to deassert, retries by dropping our claim, and times out with `-EBUSY`. Deselect drops our claim and waits slew delay.

State and persistence: runtime state is only GPIO output state and mux adapter lifetime. Timing values persist in driver data.

Dependencies and integration: depends on OF, gpiolib, platform driver core, and `i2c_mux_add_adapter()`.

Risks: only two-master topologies are supported. Timing values directly affect fairness and latency. Busy timeout prevents transfers rather than queuing. GPIO polarity/configuration must match the binding.

Test signals: claim/release GPIO traces, contention with a peer master, timing property defaults, probe defer for missing GPIO/parent, and child adapter removal.
