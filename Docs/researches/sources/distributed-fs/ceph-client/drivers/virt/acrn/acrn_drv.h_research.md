# sources/distributed-fs/ceph-client/drivers/virt/acrn/acrn_drv.h

Purpose: shared private header for the ACRN Hypervisor Service Module. It defines VM, memory mapping, I/O request client, ioeventfd/irqfd integration state, and cross-file function prototypes.

Important APIs, types, and functions: key structures are `vm_memory_region_op`, `vm_memory_region_batch`, `vm_memory_mapping`, `acrn_ioreq_buffer`, `acrn_ioreq_range`, `acrn_ioreq_client`, and `acrn_vm`. Constants include `ACRN_NAME_LEN`, `ACRN_MEM_MAPPING_MAX`, memory operation types, `ACRN_INVALID_VMID`, VM flags, and ioreq client flags. It declares global `acrn_dev`, `acrn_vm_list`, `acrn_vm_list_lock`, and APIs for VM creation/destruction, memory map/unmap, ioreq lifecycle, MSI injection, ioeventfd, and irqfd.

Control flow: not executable by itself; it codifies the in-kernel object graph. `struct acrn_vm` owns lifecycle state for one User VM associated with an open `/dev/acrn_hsm` file, including mapping arrays, ioreq clients, shared pages, eventfd lists, and workqueues.

State and persistence: declares in-memory state only. VM state is per open file and destroyed on release; no disk persistence.

Dependencies and integration points: depends on UAPI `<linux/acrn.h>`, miscdevice, hypercall wrappers, lists, locks, pages, eventfd-driven components, and companion source files `hsm.c`, `vm.c`, `mm.c`, `ioreq.c`, `ioeventfd.c`, and `irqfd.c`.

Risks: fixed `ACRN_MEM_MAPPING_MAX` limits mapped regions. Locking responsibilities are spread across mutexes, spinlocks, rwlocks, waitqueues, and bitmaps, so contract drift can cause races. Flexible array batches require correct allocation sizing. Header-level prototypes expose a broad internal API.

Test signals: compile all ACRN objects; static analysis for lock pairing and flexible-array sizing; VM lifecycle tests covering create, memory map, ioreq, ioeventfd, irqfd, destroy, and release cleanup.
