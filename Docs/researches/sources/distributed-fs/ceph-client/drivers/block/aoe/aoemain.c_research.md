# sources/distributed-fs/ceph-client/drivers/block/aoe/aoemain.c

Purpose: module initialization and teardown coordinator for the AoE driver. It creates the shared workqueue, initializes AoE subsystems in dependency order, registers the block major, and runs a periodic discovery timer.

Important APIs and functions: `aoe_init()` is the module entry point. `aoe_exit()` is the module exit point. `discover_timer()` reschedules itself every 60 seconds and sends a broadcast config query through `aoecmd_cfg(0xffff, 0xff)`. `aoe_wq` is the global workqueue used for sleeping device/disk work.

Control flow: init allocates `aoe_wq`, then initializes device, character, block, network, and command subsystems. Only after these are ready does it register block major 152 and start discovery. Error labels unwind previously initialized subsystems in reverse partial order. Exit deletes the timer, shuts down networking, unregisters the block major, stops command kthreads, removes char devices, flushes/frees devices, frees block caches, and destroys the workqueue.

State and persistence: module state includes `aoe_wq` and the discovery `timer_list`. Module metadata declares GPL license, author, description, and `VERSION`. Runtime device state is delegated to other files.

Dependencies and integration points: depends on all AoE subsystem init/exit functions and on shared constants from `aoe.h`. The order matters: block cache must outlive device buffer deallocation, and command/network subsystems must be available for discovery.

Risks: if init ordering changes, discovery or cleanup can run without required subsystems. The periodic discovery timer emits network traffic every minute while loaded. Test signals include successful module load/unload, init failure injection at each stage, discovery packet emission, no timer after unload, and correct cleanup ordering with discovered devices.
