# sources/distributed-fs/ceph-client/drivers/virt/acrn/vm.c

## Purpose
Owns ACRN VM lifecycle and MSI injection plumbing for the HSM driver.

## APIs, Types, and Functions
Defines global `acrn_vm_list` and `acrn_vm_list_lock`. Exports `acrn_vm_create()`, `acrn_vm_destroy()`, and `acrn_msi_inject()`.

## Control Flow and State
`acrn_vm_create()` calls `hcall_create_vm()`, initializes region and ioreq client locks/lists, stores VMID/vCPU count, initializes the shared ioreq page, adds the VM to the global list, and initializes ioeventfd and irqfd subsystems. `acrn_vm_destroy()` is idempotent via `ACRN_VM_FLAG_DESTROYED`, destroys the hypervisor VM first, removes the VM from the global list, deinitializes ioeventfd, irqfd, ioreq, monitor-page, and RAM mappings, then invalidates `vmid`. `acrn_msi_inject()` allocates an MSI entry with `GFP_ATOMIC`, fills address/data, and calls `hcall_inject_msi()`.

## Dependencies and Integration
This file coordinates with all ACRN HSM submodules and hypercalls. It is invoked from the `/dev/acrn_hsm` ioctl lifecycle in `hsm.c`.

## Risks and Test Signals
Creation can leak submodule state if `acrn_ioeventfd_init()` or `acrn_irqfd_init()` were to fail because return values are not checked. Destruction order matters because request dispatch walks the global list. Tests should validate repeated destroy, failure after ioreq init, VM list visibility during dispatch, MSI injection from irqfd context, and resource cleanup after mapped RAM and active clients.
