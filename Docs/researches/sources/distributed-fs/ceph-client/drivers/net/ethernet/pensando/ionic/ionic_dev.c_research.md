# sources/distributed-fs/ceph-client/drivers/net/ethernet/pensando/ionic/ionic_dev.c

Purpose: Implements low-level Ionic device operations: watchdog and firmware heartbeat checks, doorbell workaround scheduling, BAR0 register setup, CMB discovery/allocation, device command helpers, VF/port/LIF command builders, CQ servicing, and queue posting.

Important APIs and flow: `ionic_dev_setup()` validates BAR0 signature, maps device info/devcmd/interrupt registers, initializes dev info and watchdog workqueue, and records doorbell/CMB BARs. `ionic_map_cmb()` chooses discoverable or classic CMB mapping and initializes bitmap allocation state. `ionic_heartbeat_check()` samples firmware running/generation/heartbeat bits and enqueues LIF reset deferred work on up/down transitions. `ionic_dev_cmd_go()`, `ionic_dev_cmd_done/status/comp()`, and command-specific wrappers build firmware commands for device, port, VF, LIF, adminq, CMB discovery, and RDMA reset users. `ionic_get_cmb()` reserves bitmap regions, chooses regular or expanded-doorbell physical pages by stride, clears the memory with temporary WC mappings, and `ionic_put_cmb()` releases it. `ionic_cq_service()` advances completion color/tail and `ionic_q_post()` advances queue head and rings doorbells.

State and persistence: Owns firmware readiness state, watchdog timer/workqueue, BAR register pointers, doorbell page addresses, CMB bitmaps and physical regions, port info DMA pointers, queue/CQ indexes, and device info strings.

Dependencies and integration: Used by PCI probe/reset, LIF queue setup, adminq paths, ethtool settings, devlink firmware update, auxiliary RDMA reset, and TX/RX datapath doorbells.

Risks and test signals: Firmware reset transitions are asynchronous and depend on state bits in the LIF. CMB discovery has multiple firmware layout assumptions and bitmap allocation must be paired with release. Doorbell workaround work must stop before queue memory disappears. Test heartbeat stall/recovery, generation changes, devcmd timeout/null BAR handling, CMB classic/discovered/expanded regions, queue wraparound, completion color flips, and teardown while delayed work is queued.
