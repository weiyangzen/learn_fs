# sources/distributed-fs/ceph/src/mds/ScrubHeader.h

Purpose: defines `ScrubHeader`, the shared parameter and accounting object carried by recursive MDS scrub operations.

Important APIs and types: constructor captures tag, internal-tag flag, force, recursive, repair, and scrub-mdsdir options. Accessors expose origin inode, options, tag, repaired bit, forwarding epoch, and pending count. It also records uninline failures by errno/inode/path and counters for uninline started/passed/failed/skipped. `ScrubHeaderRef` and `ScrubHeaderRefConst` are shared pointer aliases.

State and persistence: state is in-memory for the lifetime of one scrub tag. It tracks global completion through pending count and `epoch_last_forwarded`; final failure/counter data is later collected by `ScrubStack` into scrub stats and the damage table.

Dependencies and integration: depends on inode number types and Ceph assertions. `ScrubStack`, `CInode`, and `CDir` attach and read headers while queueing, forwarding, validating, and completing scrub work.

Risks and test signals: pending count asserts on underflow, so all forwarded or async work must balance increments/decrements in code outside this header. Tests should cover multi-MDS forwarding epochs, uninline failure aggregation, repair flag propagation, and status reporting for force/recursive/repair/scrub_mdsdir options.
