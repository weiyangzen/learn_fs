# sources/distributed-fs/ceph-client/drivers/block/aoe/aoe.h

Purpose: central private header for the AoE driver. It defines protocol wire headers, driver constants, device/target/frame/request state structures, flags, and cross-file function prototypes.

Important APIs and types: protocol structs `aoe_hdr`, `aoe_atahdr`, and `aoe_cfghdr` model Ethernet AoE, ATA command, and config payloads. `struct aoedev` is the main device object, holding AoE address, flags, disk/queue/tag set, geometry, request list, timers, skb pool, target array, active-frame hash, retransmit queue, and in-progress request pointers. `struct aoetgt` tracks one remote MAC target, congestion window state, free frames, interfaces, taint, and packet counts. `struct frame` tracks one outstanding AoE command, skb, tag, sent time, target, bio iterator, and response skb. `struct buf` bridges blk-mq requests/bios to frames. `struct ktstate` abstracts driver kthreads.

Control flow role: no executable code, but it defines the contracts between `aoeblk.c` queueing, `aoecmd.c` frame construction/completion, `aoedev.c` lifecycle, `aoechr.c` control devices, `aoenet.c` packet I/O, and `aoemain.c` module init.

State and persistence: enumerated `DEVFL_*` flags encode device lifecycle, including up, timer kill, LBA48, gendisk allocation, size updates, freeing/freed, and dead timeout. AoE storage identity persists in `aoedev.ident`, geometry, size, target list, and firmware version until flush or module unload.

Dependencies and integration points: includes blk-mq and references Linux block, networking, mempool, timers, sk_buffs, workqueues, and debugfs through the implementation files. Public constants include `AOE_MAJOR`, `DEVICE_NAME`, `AOE_PARTITIONS`, and `VERSION`.

Risks: shared mutable structures are accessed under several locks and kthreads; flag semantics must remain consistent across files. Changing struct layout or flag meaning has driver-wide effects. Test signals include compile coverage for all AoE objects, lockdep/runtime tests for target/device transitions, and protocol interop with AoE shelves.
