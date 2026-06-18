<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.h

## Purpose
Declares the debugfs lifecycle hooks used by the `bng_re` driver.

## Important APIs, Types, And Functions
- `bng_re_debugfs_add_pdev(struct bng_re_dev *rdev)` and `bng_re_debugfs_rem_pdev(struct bng_re_dev *rdev)` manage per-device debugfs directories.
- `bng_re_register_debugfs()` and `bng_re_unregister_debugfs()` manage module-level debugfs root creation and removal.

## Control Flow
The header has no executable control flow. It allows `bng_dev.c` to call debugfs setup and teardown functions implemented in `bng_debugfs.c`.

## State And Persistence
The header stores no state. It exposes functions that mutate `bng_re_debugfs_root` and `rdev->dbg_root` in the implementation.

## Dependencies And Integration Points
The prototypes reference `struct bng_re_dev`, which is supplied by the driver's main header. It integrates the debugfs implementation with module and device lifecycle code.

## Risks And Edge Cases
There is no forward declaration for `struct bng_re_dev` in this header, so includers must include a header that defines or declares it before using these prototypes. Current source inclusion order in `bng_dev.c` and `bng_debugfs.c` satisfies this.

## Test Signals
Compilation of `bng_dev.c` and `bng_debugfs.c` confirms the prototypes match the implementation. Sparse or header self-containment checks may flag the missing forward declaration if the header is included standalone.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_debugfs.h -->
