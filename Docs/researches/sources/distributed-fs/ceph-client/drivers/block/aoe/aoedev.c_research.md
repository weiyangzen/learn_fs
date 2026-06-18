# sources/distributed-fs/ceph-client/drivers/block/aoe/aoedev.c

Purpose: manages the global AoE device list, minor allocation, device lookup/allocation, downing and flushing devices, target/frame cleanup, skb-pool cleanup, and module-exit teardown.

Important APIs and functions: `aoedev_by_aoeaddr()` finds or allocates an `aoedev` for an AoE major/minor address and increments its reference. `aoedev_put()` releases lookup references. `aoedev_downdev()` marks a device down, fails active/retransmit/in-progress/queued I/O, resets target windows, freezes/quiesces blk-mq queues, and zeroes disk capacity. `aoedev_flush()` parses user flush requests and delegates to `flush()`. `freedev()` deletes timers, gendisks, tag sets, mempools, targets, skb pools, and minor allocation. `minor_get_dyn/static()` and `minor_free()` manage block minors. `freetgt()` releases netdev refs and frames.

Control flow: discovery/config code calls `aoedev_by_aoeaddr(..., do_alloc=1)` to create devices with target array, work item, lock, request list, skb pool, dummy timer, active frame buckets, minor, RTT defaults, and list insertion. Flush/exit is multi-pass: first mark eligible devices `DEVFL_TKILL` after downing them, second call sleeping `freedev()`, third unlink and free devices whose resources are gone. Eligibility differs for exit, explicit specific/all flush, open devices, refs, and pending allocation/resize flags.

State and persistence: global `devlist` is protected by `devlist_lock`. Minor usage persists in `used_minors`. Per-device lifecycle flags include up/dead/tkill/freeing/freed and allocation/resize state. Device refs protect ktio-held frames. Timer state persists until device free.

Dependencies and integration points: called by `aoecmd.c`, `aoechr.c`, and `aoemain.c`; depends on blk-mq queue freeze/quiesce, gendisk teardown, mempool destroy, sk_buff lifetime checks, netdev references, and AoE shared structures.

Risks: manual reference counting is narrow and comments acknowledge limited confidence under async flushes. `skbfree()` can leak after waiting 30 seconds if another holder keeps a reference. Flush eligibility can leave devices alive when open or referenced. Test signals include dynamic/static minor collision tests, `echo all > /dev/etherd/flush`, explicit device flush, module unload with active I/O, down-device fast-fail behavior, and no leaked netdev/skb/disk resources.
