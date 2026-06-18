
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/tda665x.h

## Purpose
`tda665x.h` defines board configuration and attach declarations for the TDA665x tuner driver.

## Important APIs, Types, and Functions
`struct tda665x_config` provides tuner display name, I2C address, min/max frequency, frequency offset, reference multiplier, and reference divider. `tda665x_attach()` attaches tuner ops to an existing frontend when the driver is reachable; otherwise an inline stub logs disabled Kconfig and returns `NULL`.

## Control Flow
The header contributes only compile-time attach selection. The config is consumed by `tda665x.c` during attach and frequency programming.

## State and Persistence Behavior
No runtime state is declared here; config data is board-owned and read by the tuner implementation.

## Dependencies and Integration Points
The header is used by bridge drivers and `tda665x.c`; it expects DVB frontend and I2C types from the build context.

## Risks and Edge Cases
Min/max and offset semantics must match the implementation, which has suspicious validation and buffer behavior. Name length is fixed at 128 and copied into tuner info.

## Test Signals
Compile tests should include enabled/disabled Kconfig paths; runtime config tests should validate frequency limits, offset/divider math, and name propagation.
