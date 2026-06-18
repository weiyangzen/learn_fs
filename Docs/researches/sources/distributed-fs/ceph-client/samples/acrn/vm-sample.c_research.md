# sources/distributed-fs/ceph-client/samples/acrn/vm-sample.c

Purpose: userspace example that creates and runs a simple User VM through the ACRN HSM device.

Important APIs/types/functions: uses `/dev/acrn_hsm`, `ACRN_IOCTL_CREATE_VM`, `ACRN_IOCTL_SET_MEMSEG`, `ACRN_IOCTL_SET_VCPU_REGS`, `ACRN_IOCTL_CREATE_IOREQ_CLIENT`, `ACRN_IOCTL_START_VM`, `ACRN_IOCTL_ATTACH_IOREQ_CLIENT`, `ACRN_IOCTL_NOTIFY_REQUEST_FINISH`, pause/destroy ioctls, `struct acrn_vm_creation`, `acrn_vm_memmap`, `acrn_vcpu_regs`, `acrn_io_request`, and embedded `guest16` payload symbols.

Control flow: allocates aligned guest memory, opens the HSM device, creates a VM, maps a 1 MiB RAM segment, copies guest code, initializes real-mode vCPU registers, creates an IO request client, starts the VM, then loops attaching to IO requests and printing port I/O operations until SIGINT sets `is_running` false and pauses/destroys the client. Finally it destroys the VM, closes the device, and frees memory.

State and persistence: process globals track guest memory, VM ID, vCPU count, HSM FD, and shared IO request page. Guest state lives in ACRN and the allocated memory during process lifetime only.

Dependencies and integration: requires ACRN Service VM privileges, `CONFIG_ACRN_HSM`, `/dev/acrn_hsm`, Linux ACRN UAPI headers, and the assembled guest payload.

Risks: many ioctl return values are printed but not enforced before later steps, so failures can cascade. `open` failure is not checked before ioctl use. Signal handler performs ioctl calls, which are not async-signal-safe. The VM setup is intentionally minimal and only suitable as a sample.

Test signals: compile against current headers, run on an ACRN Service VM, observe VM creation/start messages and PIO logging, and verify SIGINT cleanup leaves no stale VM/client.
