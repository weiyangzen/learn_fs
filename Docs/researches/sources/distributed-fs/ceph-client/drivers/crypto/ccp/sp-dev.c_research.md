# sources/distributed-fs/ceph-client/drivers/crypto/ccp/sp-dev.c

## Purpose

`sp-dev.c` is the common AMD Secure Processor core used by both PCI and platform bus frontends. It tracks SP devices, multiplexes shared interrupts between CCP and PSP subdevices, initializes/destroys CCP and PSP feature blocks, and provides module entry/exit.

## Important APIs, Types, And Functions

Public functions include `sp_alloc_struct()`, `sp_init()`, `sp_destroy()`, `sp_suspend()`, `sp_resume()`, `sp_restore()`, `sp_request_ccp_irq()`, `sp_request_psp_irq()`, `sp_free_ccp_irq()`, `sp_free_psp_irq()`, and `sp_get_psp_master_device()`. Static state includes `sp_units`, `sp_unit_lock`, and `sp_ordinal`. `sp_irq_handler()` calls registered CCP and PSP handlers when both subdevices share an IRQ.

## Control Flow

Bus probes allocate and populate `struct sp_device`, then call `sp_init()`. The core appends the device to the global list, initializes CCP if vdata exists, then initializes PSP if vdata exists. IRQ request helpers either install a shared top-level handler or request a subdevice-specific IRQ. Suspend/resume delegate to CCP, while restore first restores PSP TEE state then resumes CCP. Module init registers the PCI driver on x86 or platform driver on arm64; x86 PSP PCI post-init starts SEV firmware setup.

## State And Persistence Behavior

The global SP list persists while devices are bound and is protected by a rwlock. Each `sp_device` stores subdevice data pointers, IRQ handlers, master-selection callbacks, and bus-specific data. Ordinals monotonically assign device names.

## Dependencies And Integration Points

It depends on bus frontends `sp-pci.c` and `sp-platform.c`, CCP and PSP subdevice APIs, kernel module initialization, and KVM SEV built-in init when configured.

## Risks And Test Signals

Risks include shared IRQ lifetime races, ignoring subdevice init errors in `sp_init()`, master lookup under write lock, and partial teardown ordering between CCP/PSP. Test with devices that have CCP-only, PSP-only, shared IRQ, and separate IRQ layouts; suspend/resume/restore; and module unload or PCI remove.
