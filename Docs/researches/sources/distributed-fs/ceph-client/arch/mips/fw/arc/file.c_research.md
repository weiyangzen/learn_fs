<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/file.c -->
## sources/distributed-fs/ceph-client/arch/mips/fw/arc/file.c

**Purpose:** Implements minimal ARC firmware file/device read and write wrappers.

**Important APIs/types/functions:** `ArcRead()` dispatches `read` with file ID, buffer, byte count, and returned count pointer. `ArcWrite()` dispatches `write` similarly.

**Control flow:** Each wrapper creates no state and immediately invokes the ROM vector through `ARC_CALL4`, returning the firmware status code.

**State, dependencies, integration:** Used by `prom_putchar()`, `prom_getchar()`, and early PROM debugging paths. It depends on ARC firmware pointer and integer type conventions.

**Risks and test signals:** Firmware calls may require cache handling and valid low-memory buffers on 64-bit kernels using 32-bit ARC. Test standard handles 0/1 for console input/output and count propagation on partial reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/mips/fw/arc/file.c -->
