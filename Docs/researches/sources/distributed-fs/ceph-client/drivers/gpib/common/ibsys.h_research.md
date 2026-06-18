# sources/distributed-fs/ceph-client/drivers/gpib/common/ibsys.h

Purpose: private common header for the GPIB core implementation. It pulls in subsystem, kernel, I/O, IRQ, DMA, and uaccess dependencies needed by `gpib_os.c` and `iblib.c`, and declares shared helper functions for board allocation and serial-poll/status-queue management.

Important APIs and types: declares `gpib_allocate_board`, `gpib_deallocate_board`, `num_status_bytes`, `push_status_byte`, `pop_status_byte`, `get_gpib_status_queue`, `get_serial_poll_byte`, and `autopoll_all_devices`. It also defines the common address bounds `MAX_GPIB_PRIMARY_ADDRESS` and `MAX_GPIB_SECONDARY_ADDRESS`.

Control flow and integration: `gpib_os.c` provides allocation, status-queue, and autospoll implementations; `iblib.c` calls them while performing online/offline, serial poll, and high-level bus operations. Including `gpibP.h` makes the common implementation see GPIB core structures, ioctl definitions, command constants, and provider registration prototypes.

State and persistence: the header itself has no state. Its declarations expose operations that mutate `gpib_board` buffers, event queues, device status queues, and autospoll behavior.

Dependencies: Linux kernel headers for scheduling, errno, major numbers, modules, memory allocation, timers, I/O, uaccess, IRQ, and DMA. It is intentionally not a public user-space ABI header; user ABI lives under Linux GPIB headers.

Risks: broad includes can mask missing direct includes in source files and increase rebuild scope. The address-limit macros are private constants; mismatches with public ioctl validation or adapter assumptions would create inconsistent behavior. Because this header declares non-exported helpers shared only inside `gpib_common.o`, moving files between modules would require export changes.

Test signals: compile `gpib_common.o` with sparse/modpost; ensure prototypes match definitions; exercise address-bound validation through `IBPAD`, `IBSAD`, and serial-poll ioctls.
