## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-msglog.c

### Purpose
`opal-msglog.c` exposes OPAL's in-memory console/message log through `/sys/firmware/opal/msglog` and provides reusable memcons helpers.

### Important APIs, Types, And Functions
The firmware layout is `struct memcons`. Key functions are `memcons_init()`, `memcons_get_size()`, `memcons_copy()`, `opal_msglog_copy()`, `opal_msglog_init()`, and `opal_msglog_sysfs_init()`.

### Control Flow
Initialization reads the `ibm,opal-memcons` physical address from the OPAL node, maps it with `phys_to_virt()`, validates the magic value, and sizes the sysfs binary attribute from input plus output buffer sizes. Reads snapshot `out_pos`, issue an `smp_rmb()`, then copy from the wrapped or linear output buffer with `memory_read_from_buffer()`.

### State, Persistence, And Dependencies
The only Linux state is the global `opal_memcons` pointer and the bin attribute size. The log buffer is firmware-owned persistent memory. The file depends on OPAL DT properties, endian conversion, physical-to-virtual mapping, and sysfs binary attributes.

### Integration Points
`opal_init()` initializes the memory console before creating the sysfs file under `opal_kobj`. `powernv.h` exposes the memcons helpers for other PowerNV code.

### Risks
The code trusts firmware buffer addresses and sizes after validating only the memcons magic. Wrap handling mutates the local `pos` after the first read and depends on `memory_read_from_buffer()` semantics. Corrupt `out_pos` aborts reads, but corrupt buffer pointers cannot be validated here.

### Test Signals
Test absent property, bad magic, wrapped and non-wrapped logs, reads with nonzero offsets and small counts, corrupt `out_pos` greater than buffer size, and sysfs creation after failed initialization.
