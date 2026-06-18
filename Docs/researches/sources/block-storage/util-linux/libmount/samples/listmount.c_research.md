# File Research: sources/block-storage/util-linux/libmount/samples/listmount.c

Sample comparing kernel `listmount()`/`statmount()` based mount table enumeration with `/proc/self/mountinfo`.

Key responsibilities:
- Builds a libmount table from `listmount()`.
- Optionally restricts listing to a mount ID or path-derived mount ID.
- Uses `libmnt_statmnt` to fetch mountpoint and filesystem type data.
- Prints listmount-based, procfs-based, and stepped reverse iteration outputs.
- Measures elapsed time for listmount-only, listmount+statmount, and mountinfo parsing.

Important behavior:
- Sets a statmount mask for mountpoint and filesystem type where kernel constants are available.
- Demonstrates on-demand statmount fetching by iterating the table.
- Demonstrates on-demand listmount in small steps by setting step size to 5 and enabling listmount backend.

Dependencies:
- Depends on libmount listmount/statmount support, `mountutils.h` fallbacks, `timeutils.h`, `strutils.h`, and `_PATH_PROC_MOUNTINFO`.

Notable risks:
- Designed for newer Linux kernels; failures are warned but the sample continues.
- Contains a typo in output text: `/proc/sef/mountinfo`.
