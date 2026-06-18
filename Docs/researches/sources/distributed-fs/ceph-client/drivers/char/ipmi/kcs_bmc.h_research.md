<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.h -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.h

## Purpose
Defines the shared BMC-side KCS device model, register layout, event bits, and status bits used by hardware providers and client drivers.

## Important APIs, Types, and Functions
- `KCS_BMC_EVENT_TYPE_OBE` and `KCS_BMC_EVENT_TYPE_IBF` identify output-buffer-empty and input-buffer-full event classes.
- `KCS_BMC_STR_OBF`, `KCS_BMC_STR_IBF`, and `KCS_BMC_STR_CMD_DAT` define KCS status bits.
- `struct kcs_ioreg` maps input data, output data, and status registers.
- `struct kcs_bmc_device` holds list linkage, Linux device, channel number, register offsets, hardware ops, spinlock, and active client pointer.

## Control Flow
This header has no executable flow, but the structures define how hardware-specific drivers expose registers to generic client logic.

## State and Persistence
`struct kcs_bmc_device` is the durable per-channel state object owned by hardware providers and registered through `kcs_bmc_add_device()`.

## Dependencies and Integration Points
Included by `kcs_bmc.c`, `kcs_bmc_client.h`, `kcs_bmc_device.h`, and hardware/client modules.

## Risks
The header establishes a single active-client model. Any future multi-client behavior would need changes to `client` ownership and event-mask semantics.

## Test Signals
Compile coverage across all KCS BMC providers/consumers and event/status bit tests in client state machines.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc.h -->
