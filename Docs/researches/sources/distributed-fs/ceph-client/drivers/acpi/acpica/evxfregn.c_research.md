# sources/distributed-fs/ceph-client/drivers/acpi/acpica/evxfregn.c

## Purpose
`evxfregn.c` exposes address-space operation-region handler registration and `_REG` execution APIs. It connects host region handlers to namespace devices and disconnects regions when handlers are removed.

## Important APIs, Types, And Functions
Exports are `acpi_install_address_space_handler`, `acpi_install_address_space_handler_no_reg`, `acpi_remove_address_space_handler`, and `acpi_execute_reg_methods`. The shared helper `acpi_install_address_space_handler_internal` controls whether `_REG` methods are run. It uses namespace nodes, attached operand objects, address-space handler objects, and region lists.

## Control Flow
Installation validates a device handle under the namespace mutex, calls `acpi_ev_install_space_handler`, and optionally executes `_REG(..., Connect)` methods beneath the node. The `_no_reg` variant deliberately skips `_REG` so callers can delay method execution until hardware initialization is complete. Removal validates the device/root/processor/thermal handle, locates the matching handler object by `space_id` and callback pointer, detaches every region on the handler's region list with `_REG(..., Disconnect)`, unlinks the handler object from the attached object's handler list, and drops its reference. `acpi_execute_reg_methods` validates the node and runs connect `_REG` methods to a caller-provided depth.

## State And Persistence
Handlers are stored in namespace-attached object handler chains. Regions point back to active handlers and are detached during removal. `_REG` execution informs firmware AML of region availability but does not persist data beyond interpreter and firmware side effects.

## Dependencies And Integration Points
The file integrates namespace locking, `acpi_ev_install_space_handler`, `acpi_ev_execute_reg_methods`, `acpi_ev_detach_region`, and region access dispatch used later by field I/O. Default handler setup and host driver region handlers rely on these APIs.

## Risks
Running `_REG` too early can execute AML before hardware/default handlers are ready; the no-reg variant exists to avoid that. Removal requires exact handler pointer matching and can reject otherwise valid space IDs if the callback differs. Detaching regions can invoke AML and must stay under correct namespace synchronization.

## Test Signals
Tests should validate handler install with and without `_REG`, removal of existing and non-existing handlers, mismatched callback rejection, root/device/processor/thermal validation, region detachment list draining, and deferred `_REG` execution depth limits.
