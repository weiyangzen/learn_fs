# sources/distributed-fs/ceph-client/arch/um/drivers/vector_user.c Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_user.c -->
## sources/distributed-fs/ceph-client/arch/um/drivers/vector_user.c

### Purpose
This file is the userspace side of UML vector networking. It parses interface specifications and opens host TAP, raw packet, GRE, L2TPv3, BESS Unix socket, inherited-fd, and VDE transports for vector net devices.

### Important APIs, Types, And Functions
Key APIs include `uml_parse_vector_ifspec()`, `uml_vector_fetch_arg()`, `uml_vector_user_open()`, transport-specific `user_init_*_fds()` helpers, vnet-header helpers, batched I/O wrappers, and BPF creation/attach/detach helpers. `struct arglist` and `struct vector_fds` are the main data carriers.

### Control Flow
The config string is split in place into token/value pairs. `uml_vector_user_open()` dispatches on `transport=` and each initializer allocates fd state, opens/binds/connects host resources, optionally runs an ifup helper, and returns RX/TX descriptors. I/O wrappers retry `EINTR` and normalize nonblocking no-progress cases to zero.

### State, Persistence, And Dependencies
State persists as host fds, socket addresses, attached filters, TAP devices, and helper processes. Dependencies include host networking syscalls, Linux tun/packet/socket UAPI, UML `os_*` wrappers, `run_helper()`, and `um_malloc`.

### Integration Points And Risks
Risks include unchecked `MAXVARGS` parser capacity, in-place config mutation, prefix transport matching, partial cleanup paths, inherited fd ownership surprises, and unvalidated BPF file sizing. Integration is with the kernel vector network driver and host-side packet batching.

### Test Signals
Exercise malformed specs, every transport, dynamic TAP naming, helper failure, vnet-header setup, nonblocking EAGAIN/ENOBUFS paths, BPF load/attach/detach, and partial initialization cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/um/drivers/vector_user.c -->
