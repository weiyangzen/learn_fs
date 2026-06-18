# sources/distributed-fs/ceph-client/kernel/irq/devres.c

## Purpose
`devres.c` provides device-managed wrappers for requesting/freeing IRQs, allocating IRQ descriptors, setting up generic IRQ chips, and instantiating IRQ domains. It lets driver probe paths register IRQ resources that are automatically released on device detach or probe failure.

## Important APIs, types, and functions
Public APIs include `devm_request_threaded_irq()`, `devm_request_any_context_irq()`, `devm_free_irq()`, `__devm_irq_alloc_descs()`, `devm_irq_alloc_generic_chip()`, `devm_irq_setup_generic_chip()`, and `devm_irq_domain_instantiate()`. Internal resource records are `struct irq_devres`, `struct irq_desc_devres`, and `struct irq_generic_chip_devres`.

## Control flow
Managed request functions allocate a devres record, call the corresponding request API, fill the IRQ/dev_id on success, and attach the record to the device; failures free the resource and return/log via `dev_err_probe()`. `devm_free_irq()` releases the matching resource manually. Descriptor allocation and generic chip setup follow the same pattern: allocate resource, perform core IRQ operation, then register a release callback that frees descriptors or removes the chip. Domain instantiation stores the domain pointer and removes it on release.

## State and persistence
State is the device's devres list plus underlying IRQ subsystem state. Resources persist until manual devm release, driver unbind, probe failure cleanup, or device teardown. No state survives the device lifecycle.

## Dependencies and integration points
The file integrates driver core devres with generic IRQ request/free, descriptor allocation, generic-chip setup, IRQ domains, module ownership, and device error reporting. It is a convenience and safety layer over core APIs in `manage.c`, `irqdesc.c`, `generic-chip.c`, and `irqdomain.c`.

## Risks and test signals
Risks include mismatched `dev_id` preventing `devm_free_irq()` release, double-free warnings when drivers mix managed and unmanaged APIs, release ordering between domains/chips/descriptors, and over-logging if callers add duplicate probe messages. Test signals include probe failure cleanup, manual `devm_free_irq()`, threaded and any-context requests, descriptor allocation release, generic-chip setup removal, and domain instantiate/remove under driver unbind.
