# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/drx39xyj/drx39xxj.h

## Purpose
`drx39xxj.h` is the Linux-facing public header for the Micronas DRX39xxJ frontend driver. It defines the per-device wrapper state used by the frontend implementation and exposes the attach entry point.

## Important APIs, Types, and Functions
`struct drx39xxj_state` stores the parent `i2c_adapter`, a generic `struct drx_demod_instance`, embedded `struct dvb_frontend`, an `i2c_gate_open` bit, and a firmware handle. `drx39xxj_attach(struct i2c_adapter *i2c)` returns a DVB frontend when `CONFIG_DVB_DRX39XYJ` is reachable; otherwise the inline stub returns `NULL`.

## Control Flow
Bridge drivers include this header and call `drx39xxj_attach()` with an I2C adapter. The implementation allocates and initializes the state, then exposes the embedded `frontend`. Disabled builds compile to a no-op attach path.

## State and Persistence
The state structure tracks runtime I2C, demod core, frontend, gate state, and firmware object lifetime. No durable storage is represented.

## Dependencies and Integration Points
It includes Linux DVB frontend headers and `drx_driver.h`, binding the Linux media layer to the generic DRX driver abstraction. It is controlled by `CONFIG_DVB_DRX39XYJ`.

## Risks and Edge Cases
The header exposes the state layout, so implementation and any users must stay synchronized. The trailing comment says `DVB_DUMMY_FE_H`, which is stale and can mislead include-guard audits. Callers must check for `NULL` when the driver is disabled or attach fails.

## Test Signals
Compile enabled/disabled configurations, attach on hardware or emulated I2C, firmware request/release paths, and I2C gate open/close behavior through tuner interactions.
