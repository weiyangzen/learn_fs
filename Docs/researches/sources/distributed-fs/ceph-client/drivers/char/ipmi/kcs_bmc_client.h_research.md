<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_client.h -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_client.h

## Purpose
Declares the client-facing KCS BMC API used by consumers that attach to a hardware KCS channel.

## Important APIs, Types, and Functions
- `struct kcs_bmc_driver_ops` supplies `add_device()` and `remove_device()` callbacks for consumer drivers.
- `struct kcs_bmc_driver` is registered globally.
- `struct kcs_bmc_client_ops` supplies the IRQ/event callback for an active client.
- `struct kcs_bmc_client` binds ops to a `kcs_bmc_device`.
- Declares register/unregister, enable/disable, event-mask update, and data/status access helpers.

## Control Flow
Consumer modules register a `kcs_bmc_driver`, receive every available `kcs_bmc_device`, create per-channel client state, and call `kcs_bmc_enable_device()` when opened or activated.

## State and Persistence
Consumer state embeds `kcs_bmc_client`, and active ownership is stored in the shared `kcs_bmc_device`.

## Dependencies and Integration Points
Included by KCS BMC consumers such as `kcs_bmc_cdev_ipmi.c` and `kcs_bmc_serio.c`.

## Risks
The API permits only one active client per channel. Consumers must balance enable/disable and avoid using device pointers after remove callbacks.

## Test Signals
Compile and module-load coverage with multiple consumers, exclusive enable tests, and remove while inactive/active.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/kcs_bmc_client.h -->
