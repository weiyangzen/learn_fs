# sources/distributed-fs/ceph-client/drivers/virt/acrn/hypercall.h

Purpose: private ACRN HSM hypercall wrapper header. It defines ACRN hypercall IDs and provides typed inline wrappers around `acrn_hypercall1`/`acrn_hypercall2`.

Important APIs, types, and functions: hypercall IDs cover Service VM CPU removal, VM lifecycle, vCPU register setup, MSI/interrupt monitor/irqline, ioreq buffer and completion, memory region mapping, PCI/MMIO/vdev assignment, ptdev interrupts, and PM CPU state. Inline wrappers include `hcall_sos_remove_cpu`, `hcall_create_vm`, `hcall_start_vm`, `hcall_pause_vm`, `hcall_destroy_vm`, `hcall_reset_vm`, `hcall_set_vcpu_regs`, `hcall_inject_msi`, `hcall_vm_intr_monitor`, `hcall_set_irqline`, `hcall_set_ioreq_buffer`, `hcall_notify_req_finish`, `hcall_set_memory_regions`, `hcall_create_vdev`, `hcall_destroy_vdev`, `hcall_assign_mmiodev`, `hcall_deassign_mmiodev`, `hcall_assign_pcidev`, `hcall_deassign_pcidev`, `hcall_set_ptdev_intr`, `hcall_reset_ptdev_intr`, and `hcall_get_cpu_state`.

Control flow: wrappers are direct one- or two-argument calls with no validation or marshalling beyond hypercall ID selection. Callers must allocate and pass Service VM physical addresses for structure arguments where required.

State and persistence: no state.

Dependencies and integration points: depends on `<asm/acrn.h>` for low-level hypercall functions. Included by `acrn_drv.h` and used throughout the ACRN HSM implementation.

Risks: thin wrappers mean ABI mismatches, wrong physical addresses, or missing validation propagate directly to the hypervisor. Hypercall ID constants must match the hypervisor exactly.

Test signals: compile-time coverage through ACRN HSM; runtime ioctl tests that exercise each wrapper and validate expected hypervisor return codes; ABI synchronization checks against ACRN hypervisor headers.
