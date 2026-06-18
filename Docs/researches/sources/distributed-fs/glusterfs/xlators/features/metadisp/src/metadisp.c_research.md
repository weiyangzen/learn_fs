# sources/distributed-fs/glusterfs/xlators/features/metadisp/src/metadisp.c

## Purpose

`metadisp.c` provides lifecycle hooks and xlator API registration for the metadisp translator.

## Important APIs, Types, and Functions

Functions are `init`, `fini`, and `reconfigure`. The exported `xlator_api` identifies the translator as `metadisp`, marks it tech preview, and points at externally defined `fops`, empty callback and dumpop structures, lifecycle hooks, and options.

## Control Flow

`init` validates that exactly two child translators are present, logs a dangling-volume warning when there are no parents, and returns success. `fini` and `reconfigure` are no-ops that return immediately.

## State and Persistence Behavior

No private runtime state is allocated by this file. Metadisp behavior is encoded in child topology and fop routing rather than `this->private`.

## Dependencies and Integration Points

It depends on generated or linked `struct xlator_fops fops`, Gluster xlator API registration, and the convention that `FIRST_CHILD` is metadata while `SECOND_CHILD` is data.

## Risks and Edge Cases

The translator has no private config validation beyond child count. Any child ordering mistake changes semantics drastically because metadata/data roles are positional. No reconfigure support exists for runtime behavior changes.

## Test Signals

Tests should load metadisp with zero, one, two, and three children; verify child order in a volfile; and confirm the generated fop table is linked into the API.
