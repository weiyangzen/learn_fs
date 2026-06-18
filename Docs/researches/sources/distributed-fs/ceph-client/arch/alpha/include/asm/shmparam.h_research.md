<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/shmparam.h -->
## sources/distributed-fs/ceph-client/arch/alpha/include/asm/shmparam.h

**Purpose:** Defines Alpha SysV shared-memory low-boundary alignment.

**Important APIs/types/functions:** `SHMLBA` equal to `PAGE_SIZE`.

**Control flow:** Generic SysV SHM code uses `SHMLBA` when validating/rounding attach addresses.

**State and persistence behavior:** No state.

**Dependencies and integration points:** Depends on page size definitions and generic IPC memory code.

**Risks:** Changing alignment would affect userspace ABI for `shmat` address placement.

**Test signals:** SysV shared memory attach tests for aligned and unaligned addresses.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/alpha/include/asm/shmparam.h -->
