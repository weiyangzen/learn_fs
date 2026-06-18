# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/siena/mcdi_port.h

## Purpose

`mcdi_port.h` is the narrow public header for MCDI-backed Siena port services. It exposes only MAC fault checking and port probe/remove lifecycle hooks to the rest of the driver.

## Important APIs, Types, and Functions

The header includes `net_driver.h` for `struct efx_nic` and declares `efx_siena_mcdi_mac_check_fault()`, `efx_siena_mcdi_port_probe()`, and `efx_siena_mcdi_port_remove()`. There are no local types, constants, or inline helpers.

## Control Flow and Integration

NIC-type implementations include this header when they need a firmware-backed port implementation. The usual control flow is probe via `efx_siena_mcdi_port_probe()`, runtime fault checks through `efx_siena_mcdi_mac_check_fault()`, and cleanup through `efx_siena_mcdi_port_remove()`. The declarations bridge device-specific probe code to `mcdi_port.c` and then to the richer PHY/MAC routines in `mcdi_port_common.c`.

## State and Persistence Behavior

The header itself stores no state. Its functions mutate `struct efx_nic` port fields, MDIO callbacks, `phy_data`, link state, and stats buffer state via their implementations. Callers should treat these as lifecycle and hardware/firmware operations, not pure queries.

## Dependencies and Risks

The main contract risk is that the header hides the fact that probe allocates multiple resources through delegated helpers. Callers must use the matching remove path and must handle probe failure according to the implementation's unwind behavior. Compile tests should catch prototype drift between this header and `mcdi_port.c`; integration tests should cover NIC type tables that reference these hooks.
