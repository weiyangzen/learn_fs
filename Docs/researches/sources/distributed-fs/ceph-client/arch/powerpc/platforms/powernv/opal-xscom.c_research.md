## sources/distributed-fs/ceph-client/arch/powerpc/platforms/powernv/opal-xscom.c

### Purpose
`opal-xscom.c` exposes OPAL XSCOM access through debugfs for each chip with a `scom-controller` node.

### Important APIs, Types, And Functions
Important functions are `opal_scom_unmangle()`, `opal_scom_read()`, `opal_scom_write()`, `scom_debug_read()`, `scom_debug_write()`, `scom_debug_init_one()`, and `scom_debug_init()`. `struct scom_debug_entry` records chip ID, device path blob, and debugfs name.

### Control Flow
Initialization checks for OPAL firmware, creates debugfs `scom`, scans nodes with `scom-controller`, derives chip IDs, and creates a per-chip directory containing `devspec` and `access`. Reads and writes require 8-byte-aligned offsets/counts, translate file offsets into SCOM register numbers, unmangle debugfs indirect-address bits, and call `opal_xscom_read()` or `opal_xscom_write()`.

### State, Persistence, And Dependencies
State consists of debugfs entries and per-chip metadata. Register effects persist in hardware/firmware. Dependencies include OF chip IDs, OPAL XSCOM calls, debugfs, user-copy helpers, and address bit conventions for indirect SCOM.

### Integration Points
The file is a device initcall and provides operator diagnostics rather than a normal driver API. `opal-prd.c` also exposes XSCOM through PRD ioctls for daemon use.

### Risks
Debugfs gives privileged raw register access and can destabilize hardware. `scom_debug_write()` increments `done` but does not advance `*ppos`, unlike reads. Address unmangling is specialized to debugfs offset limitations and can be misunderstood by users.

### Test Signals
Test aligned and unaligned reads/writes, indirect address bit mangling, missing OPAL feature, chip ID failures, user-copy errors, OPAL read/write failures, multiple chip directories, and write offset progression expectations.
