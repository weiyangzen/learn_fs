# sources/distributed-fs/ceph-client/drivers/soc/pxa/ssp.c

## Purpose
Registers PXA/Marvell SSP controller instances and provides a simple global request/free API for client drivers needing exclusive SSP port access.

## Important APIs, Types, And Functions
Exports `pxa_ssp_request()`, `pxa_ssp_request_of()`, and `pxa_ssp_free()`. Platform-driver functions are `pxa_ssp_probe()`, `pxa_ssp_remove()`, `pxa_ssp_init()`, and `pxa_ssp_exit()`. Global state is `ssp_list` protected by `ssp_lock`.

## Control Flow
Probe allocates `struct ssp_device`, obtains the clock, claims and maps MMIO, reads IRQ, determines controller type from OF match data or platform device ID, sets port ID for non-DT PXA devices, adds the device to the global list, and stores drvdata. Clients request a port by numeric port or OF node; if a matching entry has `use_count == 0`, it is marked in use and labeled. Free decrements use count and clears the label. Remove deletes the controller from the global list.

## State And Persistence
Global list entries persist while platform devices are bound. Each `ssp_device` stores MMIO base, physical base, IRQ, clock, type, OF node, label, and use count. No filesystem persistence.

## Dependencies And Integration Points
Depends on platform bus, clocks, IO resources, IRQ resources, OF match table, legacy platform IDs, and external clients using `linux/pxa2xx_ssp.h`.

## Risks
`pxa_ssp_request()` and `pxa_ssp_request_of()` initialize `ssp` to NULL and then test `&ssp->node == &ssp_list` after the loop; if the list is empty this pattern depends on list iteration semantics and can be unsafe. There is no module reference taken for clients holding an SSP. Remove does not reject active users. OF compatible strings include historical `mvrl` typos that may be ABI-preserving but surprising.

## Test Signals
SSP clients should successfully acquire one controller, fail concurrent acquisition, release cleanly, and operate with expected MMIO/IRQ/clock resources. Empty-list and active-remove behavior deserve targeted tests or review.
