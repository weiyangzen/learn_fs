# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/cn68xx_device.h

## Purpose
This minimal header declares the CN68XX LiquidIO setup entry point.

## Important APIs, Types, And Functions
The single public declaration is `lio_setup_cn68xx_octeon_device(struct octeon_device *oct)`, implemented in `cn68xx_device.c`.

## Control Flow
The generic LiquidIO chip-detection path calls this setup function for CN68XX devices. The function then installs CN68XX/common CN6XXX function pointers into `oct->fn_list`.

## State And Persistence
No state is defined in the header. CN68XX uses the common `struct octeon_cn6xxx` state from `cn66xx_device.h`.

## Dependencies And Integration Points
It depends on `struct octeon_device` being visible to including source files. It is included by the CN68XX implementation and any core code dispatching to CN68XX setup.

## Risks
The header intentionally does not expose CN68XX-specific state; callers needing common state must include the CN66XX/common header too. Missing prototype coverage would break chip dispatch.

## Test Signals
Compile chip dispatch and CN68XX implementation together and verify the setup symbol is exported from the shared LiquidIO core object.
