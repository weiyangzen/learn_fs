<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus.h -->
# sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus.h

Purpose: Shared private header for PCIe/OF Xillybus transport wrappers and the Xillybus core.

Important APIs/types/functions: Defines `struct xilly_buffer` DMA buffer descriptors, `struct xilly_idt_handle` parsed IDT metadata, `struct xilly_channel` per-stream buffer/locking/state for FPGA-write and FPGA-read directions, `struct xilly_endpoint` common endpoint state, and `struct xilly_mapping` DMA unmap metadata. Declares `xillybus_isr()`, `xillybus_init_endpoint()`, `xillybus_endpoint_discovery()`, and `xillybus_endpoint_remove()`.

Control flow: no direct flow; the structures encode the core data path. Naming is FPGA-centric: `wr_*` buffers are written by the FPGA and read by host `read()`, while `rd_*` buffers are read by the FPGA and written by host `write()`.

State and persistence: declares runtime-only endpoint/channel state including DMA buffers, indices, EOF/hangup flags, waitqueues, mutexes/spinlocks, work items, message counters, and fatal error state.

Dependencies and integration: shared by `xillybus_core.c`, `xillybus_pcie.c`, and `xillybus_of.c`; depends on Linux device, DMA, interrupt, cdev, locking, and workqueue APIs.

Risks: this is a tight ABI across modules. The channel lock/index fields are interpreted by ISR, file operations, and workqueue code, so changes require full locking-order review. Direction naming can cause read/write confusion.

Test signals: compile PCIe and OF transports with the core, run endpoint discovery, open every generated node, and stress bidirectional DMA with read/write/poll/seek/close while interrupts arrive.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/xillybus/xillybus.h -->
