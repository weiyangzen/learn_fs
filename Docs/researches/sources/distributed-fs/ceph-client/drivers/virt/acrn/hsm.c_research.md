# sources/distributed-fs/ceph-client/drivers/virt/acrn/hsm.c

Purpose: main ACRN HSM miscdevice implementation. It exposes `/dev/acrn_hsm`, associates one `struct acrn_vm` with each open file, dispatches management ioctls to hypercalls and internal VM/ioreq helpers, and provides a sysfs CPU-removal hook for the Service VM.

Important APIs, types, and functions: file operations are `acrn_dev_open`, `acrn_dev_ioctl`, and `acrn_dev_release`. Module lifecycle is `hsm_init`/`hsm_exit`. `pmcmd_ioctl` handles power-management queries. Sysfs path uses `remove_cpu_store`, `DEVICE_ATTR_WO(remove_cpu)`, visibility callback, and `acrn_dev` miscdevice. Ioctl dispatch covers VM create/start/pause/reset/destroy, vCPU regs, memseg map/unmap, MMIO/PCI/vdev assign/deassign, ptdev interrupts, irqline, MSI injection, interrupt monitor page, default ioreq client lifecycle, request completion, ioreq clearing, PM CPU state, ioeventfd, and irqfd.

Control flow: open allocates a zeroed `acrn_vm` with invalid VMID. All ioctls except create require a valid VMID. Create copies and validates user creation data, delegates to `acrn_vm_create`, and copies resulting data back. Most device-assignment and interrupt ioctls `memdup_user` a fixed structure, call the corresponding hypercall wrapper with physical address, then free it. Memory and ioreq paths delegate to internal helpers. Interrupt monitor pins one long-term user page and passes its physical address to the hypervisor. Release destroys the VM and frees the `acrn_vm`. Init checks that the kernel runs under ACRN and is the privileged VM, registers the miscdevice, then sets up ioreq interrupts.

State and persistence: per-file VM state persists from open to release; monitor pages may remain pinned until replaced or VM destruction; miscdevice and sysfs state persist while module is loaded. No disk persistence.

Dependencies and integration points: depends on x86 ACRN hypervisor CPUID/hypercall ABI, miscdevice, user-copy APIs, pin_user_pages, CPU hotplug, internal VM/MM/ioreq/ioeventfd/irqfd code, and UAPI ioctl structures from `<linux/acrn.h>`.

Risks: HSM relies on the hypervisor for most parameter sanity checks, so kernel-side validation is selective. `ACRN_IOCTL_SET_IRQLINE` passes `ioctl_param` directly as a hypercall GPA-style argument, making UAPI semantics important. Long-term pinned pages must be correctly unpinned by VM teardown. Open creates an object even before VM creation, so invalid-state checks are critical. CPU removal sysfs can offline CPUs and must roll back on hypercall failure.

Test signals: run in privileged ACRN Service VM; ioctl ABI tests for invalid VM state, reserved fields, create/destroy lifecycle, all hypercall wrappers, user-copy faults, monitor page replacement/unpinning, ioeventfd/irqfd delegation, PM queries, and module init rejection outside ACRN or outside privileged VM.
