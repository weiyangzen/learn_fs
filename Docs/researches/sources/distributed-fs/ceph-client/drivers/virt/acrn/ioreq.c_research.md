# sources/distributed-fs/ceph-client/drivers/virt/acrn/ioreq.c

## Purpose
Implements ACRN Hypervisor Service Module I/O-request dispatch. It pins the shared I/O request page supplied by userspace, registers an ACRN interrupt handler, walks every live VM for pending hypervisor requests, converts special PCI config-port traffic, and routes work either to the default userspace client or to kernel ioreq clients such as ioeventfd.

## APIs, Types, and Functions
Important exported helpers are `acrn_ioreq_init()`, `acrn_ioreq_deinit()`, `acrn_ioreq_intr_setup()`, `acrn_ioreq_intr_remove()`, `acrn_ioreq_client_create()`, `acrn_ioreq_client_destroy()`, `acrn_ioreq_range_add()`, `acrn_ioreq_range_del()`, `acrn_ioreq_client_wait()`, `acrn_ioreq_request_clear()`, and `acrn_ioreq_request_default_complete()`. Internal control centers include `ioreq_dispatcher()`, `acrn_ioreq_dispatch()`, `find_ioreq_client()`, `ioreq_task()`, and `handle_cf8cfc()`. It depends on `struct acrn_vm`, `struct acrn_ioreq_client`, and `struct acrn_io_request` from the ACRN HSM headers and hypercall ABI.

## Control Flow and State
`acrn_ioreq_intr_setup()` registers `ioreq_intr_handler()` and creates a high-priority ordered workqueue. Interrupts queue `ioreq_work`; `ioreq_dispatcher()` takes `acrn_vm_list_lock`, scans VMs, and calls `acrn_ioreq_dispatch()` for each VM with an `ioreq_buf`. Dispatch uses acquire/release barriers around `req->processed`, handles CF8/CFC PCI config pairing in-place, finds a matching client by protected range lists, marks kernel-vs-userspace ownership with `kernel_handled`, sets the processing state, records the vCPU bit in `client->ioreqs_map`, and wakes the client. Kernel clients run `ioreq_task()` in a kthread; the default client is consumed by userspace through waits and completion ioctls. Persistent runtime state is the pinned `vm->ioreq_page`, `vm->ioreq_buf`, per-client range lists, pending bitmaps, and global workqueue/interrupt handler.

## Dependencies and Integration
Integrates with ACRN hypercalls `hcall_set_ioreq_buffer()` and `hcall_notify_req_finish()`, the ACRN VM list in `vm.c`, ioctl paths in `hsm.c`, and client modules such as ioeventfd. It uses `pin_user_pages_fast(FOLL_WRITE | FOLL_LONGTERM)`, waitqueues, kthreads, rwlocks, spinlocks, and workqueues.

## Risks and Test Signals
Risk is concentrated in shared-page ordering, client teardown races, stale default-client requests during reset, and long-term page pin lifetime. `ioreq_pause()` removes the interrupt handler and drains work before client removal, which is the main teardown guard. Tests should exercise multiple vCPUs, default and kernel clients, CF8/CFC reads and writes, reset-time clearing, client destroy while requests are pending, and failure paths for page pinning and `hcall_set_ioreq_buffer()`.
