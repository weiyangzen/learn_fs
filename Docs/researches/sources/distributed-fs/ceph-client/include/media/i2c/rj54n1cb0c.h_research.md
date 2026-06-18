# sources/distributed-fs/ceph-client/include/media/i2c/rj54n1cb0c.h

## Purpose
Defines platform data for the RJ54N1CB0C camera sensor.

## Important APIs, Types, and Functions
`struct rj54n1_pdata` supplies `mclk_freq` and `ioctl_high`, a boolean controlling the sensor IOCTL signal level.

## Control Flow
Probe/mode setup reads the master clock frequency and IO control polarity, then programs or sequences the sensor accordingly.

## State and Persistence Behavior
Static board data persists indirectly through sensor register and signal programming.

## Dependencies and Integration Points
Used by V4L2 camera sensor integration where board files provide clock and IO-control polarity.

## Risks
Incorrect clock frequency or IOCTL polarity can prevent probe/streaming or leave the sensor in the wrong electrical state.

## Test Signals
Sensor probe, stream start, frame timing, and `ioctl_high` polarity validation.
