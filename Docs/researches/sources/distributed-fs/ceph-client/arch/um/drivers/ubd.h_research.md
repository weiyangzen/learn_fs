<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd.h -->
# sources/distributed-fs/ceph-client/arch/um/drivers/ubd.h

Purpose: declares the user/helper side of the UML block device I/O thread interface.

Important APIs/types/functions: prototypes are `start_io_thread()`, `io_thread()`, `ubd_read_poll()`, and `ubd_write_poll()`. External `kernel_fd` is the helper-thread side of the IPC pipe. `UBD_REQ_BUFFER_SIZE` is 64 request pointers.

Control flow: `ubd_kern.c` starts the helper with `start_io_thread()` and passes request pointers through a pipe; `io_thread()` reads them, performs host I/O, and writes completed pointers back.

State and persistence: no state is defined here beyond external declaration. Runtime state lives in the implementation and host disk image files.

Dependencies and integration points: depends on UML `os.h` helper-thread types and the block driver.

Risks: pointer-passing over a pipe assumes shared address space between UML kernel and helper thread. Buffer size must match bulk read/write logic in both halves.

Test signals: build UBD, start I/O thread, exercise asynchronous request completion, and fall back when helper startup fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/ubd.h -->
