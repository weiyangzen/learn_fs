# sources/distributed-fs/ceph-client/drivers/base/platform-msi.c

## Purpose
Provides MSI domain setup and teardown helpers for platform devices using the generic MSI parent-domain model, with migration compatibility for older platform MSI users.

## Important APIs, Types, And Functions
Exports `platform_device_msi_init_and_alloc_irqs()` and `platform_device_msi_free_irqs_all()`. The local `platform_msi_template` supplies an irq chip named `pMSI`, parent mask/unmask operations, `platform_msi_write_msi_msg()` as the write-message indirection, a descriptor setter, and `DOMAIN_BUS_DEVICE_MSI`.

## Control Flow
Initialization validates that the device has a parent MSI domain and a write-message callback, creates a managed child MSI domain with fixed vector count, stores the write callback as domain data, and allocates interrupts over the range `0..nvec-1`. Freeing releases all interrupts from `MSI_DEFAULT_DOMAIN` and removes the device IRQ domain.

## State And Persistence
State is device-managed MSI domain state and allocated MSI descriptors/interrupt mappings. Hardware IRQ numbers are derived from `desc->msi_index`, and message programming is delegated through the stored callback.

## Dependencies And Integration
Depends on generic MSI domain APIs, irqdomain, `struct msi_desc`, irq chip parent operations, and platform device parent MSI domains installed by architecture or firmware-specific code.

## Risks And Test Signals
Risks include failing when no parent domain exists, leaking device IRQ domains if allocation succeeds partially, incorrect vector range handling when `nvec` is zero, and callback mismatch during message writes. Test signals are platform MSI allocation/free tests, interrupt delivery on all allocated vectors, devres/device removal cleanup, and platforms migrated from legacy platform MSI.
