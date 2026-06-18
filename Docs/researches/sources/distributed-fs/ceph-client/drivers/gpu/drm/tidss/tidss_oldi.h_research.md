# sources/distributed-fs/ceph-client/drivers/gpu/drm/tidss/tidss_oldi.h

## Purpose

`tidss_oldi.h` defines the OLDI bridge public lifecycle API and DT/control-register constants used by `tidss_oldi.c`.

## Important APIs, Types, and Definitions

- `OLDI_INPUT_PORT` and `OLDI_OUTPUT_PORT` define graph port indices used to connect OLDI transmitters to DSS and downstream sinks.
- `OLDI_PD_CTRL` and `OLDI_LB_CTRL` are control-MMR register offsets.
- `OLDI_PWRDOWN_TX(n)` and `OLDI_PWRDN_BG` define IO power-down bits.
- `enum tidss_oldi_link_type` distinguishes unsupported, single-link, clone, secondary clone, dual-link, and secondary dual-link modes.
- Declares `tidss_oldi_init()` and `tidss_oldi_deinit()`.

## Control Flow

The platform driver calls `tidss_oldi_init()` before modeset setup and `tidss_oldi_deinit()` on error/remove. The implementation uses these constants while parsing DT and toggling IO power around bridge enable/disable.

## State and Persistence Behavior

The header has no state. Link-type values persist inside each `struct tidss_oldi` allocated by the implementation.

## Dependencies and Integration Points

It includes `tidss_drv.h` for `struct tidss_device` and driver limits. It is consumed by the platform driver and the OLDI implementation.

## Risks and Edge Cases

- Control-MMR offsets and power bits are SoC ABI; incorrect values can power the wrong OLDI transmitter or bandgap.
- Link-type enum values are used in switches; adding a mode requires updates in init, power, config, and bridge callbacks.

## Test Signals

Build tests should cover the lifecycle prototypes. Runtime tests should verify DT graph port numbers, power bit mapping for transmitter 0/1, and correct handling of each link-type switch case.
