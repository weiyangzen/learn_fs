<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/acrn.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/acrn.h

## Purpose
Defines the ioctl ABI for `/dev/acrn_hsm`, the ACRN Hypervisor Service Module interface used by service-VM userspace to create/control VMs, handle I/O requests, assign devices, manage memory, inject interrupts, and wire eventfds/irqfds.

## Important APIs, Types, And Functions
Important structures include I/O request variants `acrn_mmio_request`, `acrn_pio_request`, `acrn_pci_request`, aligned `acrn_io_request`, `acrn_io_request_buffer`, VM creation and register structs, memory maps, passthrough device/IRQ structs, virtual device structs, power-management state structs, `acrn_ioeventfd`, and `acrn_irqfd`. Ioctls include create/destroy/start/pause/reset VM, set vCPU regs, inject MSI, monitor interrupts, notify request finish, create/attach/destroy ioreq clients, set/unset memseg, assign/deassign PCI/MMIO devices, create/destroy vdevs, PM state query, ioeventfd, and irqfd.

## Control Flow
Userspace creates a VM, maps an I/O request buffer, starts vCPUs, scans request slots for `PENDING`, marks them `PROCESSING`, emulates PIO/MMIO/PCI config operations, marks requests `COMPLETE`, and notifies the hypervisor. Separate ioctls configure memory, passthrough IRQ routing, virtual devices, and eventfd/irqfd delivery.

## State And Persistence
State is per VM and per HSM client: VM id, vCPU register state, shared ioreq buffer, memory segments, device assignments, interrupt routing, and eventfd registrations. The I/O request lifecycle explicitly cycles `FREE -> PENDING -> PROCESSING -> COMPLETE -> FREE`.

## Dependencies And Integration Points
Depends on `<linux/types.h>` and ioctl definitions. Integrates with the ACRN hypervisor, service VM device model, eventfd, PCI/MMIO passthrough, ACPI power state data, and interrupt injection.

## Risks And Edge Cases
The 256-byte alignment of `acrn_io_request`, strict state ordering, atomic/barrier requirements between hypervisor and HSM, reserved fields, guest physical address trust, passthrough IRQ correctness, and eventfd deassignment flags are high-risk ABI points.

## Test Signals
Test VM lifecycle ioctls, ioreq state machine under concurrency, PIO/MMIO/PCI emulation completion, memory map set/unset, passthrough assignment/deassignment, irqfd/ioeventfd signal delivery, bad reserved-field rejection, and 32/64-bit layout compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/acrn.h -->
