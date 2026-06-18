# sources/distributed-fs/ceph-client/drivers/soc/mediatek/mtk-mutex.c

## Purpose
This driver provides MediaTek display and MDP hardware mutex support. It allocates mutex handles, maps display components to mutex module bits, configures SOF/EOF timing sources, enables/disables/acquires/releases hardware mutexes, and exposes command-queue enable support.

## Important APIs, Types, and Functions
Exported APIs include `mtk_mutex_get()`, `mtk_mutex_put()`, `mtk_mutex_prepare()`, `mtk_mutex_unprepare()`, `mtk_mutex_add_comp()`, `mtk_mutex_remove_comp()`, `mtk_mutex_enable()`, `mtk_mutex_enable_by_cmdq()`, `mtk_mutex_disable()`, `mtk_mutex_acquire()`, `mtk_mutex_release()`, `mtk_mutex_write_mod()`, and `mtk_mutex_write_sof()`. Key types are `struct mtk_mutex`, `struct mtk_mutex_data`, and `struct mtk_mutex_ctx`.

## Control Flow and State
Probe initializes ten mutex handles, obtains match data, optionally gets a clock, maps registers, stores the physical register base, reads optional CMDQ register metadata, and stores drvdata. `mtk_mutex_get()` marks an in-memory handle claimed; `put()` clears it. Component add/remove either sets module bits in one of two MOD registers or writes SOF selection for output components. Acquire writes enable and request bits, then polls `INT_MUTEX`; release clears the request bit.

## Dependencies and Integration Points
The driver integrates with DRM/DDP and MDP components through public MediaTek mutex APIs, with CMDQ through `cmdq_dev_get_client_reg()` and `cmdq_pkt_write()`, with clocks, and with OF compatibles for many SoCs and VPP/MDP variants.

## Risks and Test Signals
Risks include lack of locking around the `claimed` array, unchecked component IDs indexing SoC tables, SoC-specific module bit drift, and CMDQ address/subsys mismatch in `mtk_mutex_enable_by_cmdq()`. Test signals include concurrent display pipeline allocation, command queue enable, video mode EOF timing, MDP table-based module writes, clock enable/disable cycles, and acquisition timeout logs.
