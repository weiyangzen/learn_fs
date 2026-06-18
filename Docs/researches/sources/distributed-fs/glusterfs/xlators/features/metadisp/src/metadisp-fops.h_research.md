# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp-fops.h

## Purpose

`metadisp-fops.h` declares the hand-written metadisp fops that are not generated into `fops.c`.

## Important APIs, Types, and Functions

Declared fops are `metadisp_readdir`, `metadisp_readdirp`, `metadisp_lookup`, `metadisp_create`, `metadisp_open`, `metadisp_stat`, `metadisp_inodelk`, `metadisp_fsync`, `metadisp_unlink`, and `metadisp_setattr`.

## Control Flow

The header has no control flow. It supplies prototypes used by `fops-tmpl.c` and generated `fops.c` so special-case implementations can be referenced in the final fop table.

## State and Persistence Behavior

No state is stored here.

## Dependencies and Integration Points

It includes Gluster dict and core headers plus `sys/types.h`. It is coupled to `gen-fops.py`'s skipped list: every skipped fop should have a matching declaration and implementation.

## Risks and Edge Cases

The header declares `metadisp_inodelk`, but the generator still has inodelk as a TODO and no corresponding implementation appears in this work item, which risks unresolved symbols if the fop table references it or incomplete lock routing if it does not.

## Test Signals

Compile the generated fop table against this header and verify every declared special fop is either linked or intentionally absent from the table. Lock-operation tests should confirm inodelk behavior before enabling that table entry.
