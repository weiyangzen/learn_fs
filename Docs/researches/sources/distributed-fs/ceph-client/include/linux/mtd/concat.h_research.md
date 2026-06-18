<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/concat.h -->
# sources/distributed-fs/ceph-client/include/linux/mtd/concat.h

## Purpose
`mtd/concat.h` declares the MTD concatenation layer, which presents multiple MTD devices as one larger virtual MTD device and supports device-tree driven virtual concatenation.

## Important APIs, Types, and Functions
It defines `struct mtd_concat`, `mtd_concat_create()`, `mtd_concat_destroy()`, `mtd_virt_concat_node_create()`, `mtd_virt_concat_add()`, `mtd_virt_concat_create_join()`, `mtd_virt_concat_destroy()`, `mtd_virt_concat_destroy_joins()`, and `mtd_virt_concat_destroy_items()`.

## Control Flow and State
Manual concatenation passes an array of subdevice pointers to `mtd_concat_create()` and later destroys the wrapper. Virtual concatenation discovers intended components, adds matching `mtd_info` objects as they appear, creates/registers the joined device once complete, and destroys joins/items during removal or cleanup.

## State and Persistence Behavior
`struct mtd_concat` owns runtime wrapper state and a flexible array of subdevice pointers. Underlying MTD contents persist independently; concatenation only changes the logical view.

## Dependencies and Integration Points
It integrates with MTD core, `struct mtd_info`, device-tree based MTD discovery, and MTD registration/removal paths.

## Risks
Subdevice ordering and size boundaries must be correct or offsets map to wrong chips. Removal of a subdevice must tear down the concat and re-register individual devices as documented. Lifetime of subdevice pointers is critical.

## Test Signals
Create/destroy concatenated MTDs, read/write across subdevice boundaries, device-tree virtual concat discovery, subdevice removal, partial component arrival, and cleanup of joins/items.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mtd/concat.h -->
