<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_device.h -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_device.h

## Purpose
Declares the hardware-provider-facing KCS BMC API and operations table.

## Important APIs, Types, and Functions
- `struct kcs_bmc_device_ops` supplies provider callbacks for IRQ mask updates, byte input, byte output, and masked byte updates.
- `kcs_bmc_handle_event()` is called by hardware IRQ handlers.
- `kcs_bmc_add_device()` and `kcs_bmc_remove_device()` publish or unpublish channels.

## Control Flow
Hardware drivers fill `struct kcs_bmc_device` and ops, call `kcs_bmc_add_device()` after hardware setup, dispatch IRQs to `kcs_bmc_handle_event()`, and call `kcs_bmc_remove_device()` before disabling hardware.

## State and Persistence
The header defines no state itself but establishes the provider-owned `kcs_bmc_device` lifecycle.

## Dependencies and Integration Points
Included by `kcs_bmc_aspeed.c`, `kcs_bmc_npcm7xx.c`, and the shared core.

## Risks
Provider callbacks can be invoked under spinlocks and IRQ context; implementations must not sleep in those paths unless the calling path permits it.

## Test Signals
Provider tests should cover add/remove sequencing, IRQ dispatch, register callback correctness, and mask update behavior for IBF/OBE.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_device.h -->
