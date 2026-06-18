# sources/distributed-fs/ceph-client/include/linux/soc/mediatek/mtk-mutex.h

Purpose: This header defines MediaTek display mutex APIs used to synchronize multimedia pipeline components and start-of-frame sources.

Important APIs/types/functions: It declares opaque `struct mtk_mutex`, enums for mutex module indices and SOF source indices, and functions to get/put a mutex, prepare/unprepare resources, add/remove components, enable/disable, enable via CMDQ, acquire/release, and write module/SOF registers.

Control flow: A display pipeline gets a mutex, prepares it, adds components in route order, selects SOF, enables it for frame synchronization, and disables/removes/unprepares on teardown. CMDQ-enabled paths program the enable operation through command packets.

State and persistence: Mutex hardware stores component masks, SOF source, enable/acquire state, and prepared clock/reset state. The handle tracks ownership.

Dependencies and integration: Integrates with MediaTek DRM, MMSYS, CMDQ, regmap, and componentized display drivers.

Risks and test signals: Component mask or SOF mismatches cause frame-start deadlocks or tearing. Test atomic modesets, CMDQ and non-CMDQ enable paths, acquire timeout behavior, suspend/resume, and component add/remove symmetry.
