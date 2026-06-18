## sources/distributed-fs/ceph-client/drivers/media/platform/mediatek/vcodec/encoder/mtk_vcodec_enc_pm.h

Purpose: declares encoder power-management helper functions.

Important APIs/types/functions: prototypes cover encoder clock initialization, runtime power on/off, and clock on/off. The header includes `mtk_vcodec_enc_drv.h` to access encoder device and common PM types.

Control flow: no implementation flow. The platform driver calls clock init during probe, and encode dispatch calls power/clock helpers around hardware encode operations.

State and persistence behavior: no state is owned by the header; functions operate on `struct mtk_vcodec_enc_dev` and `struct mtk_vcodec_pm` owned elsewhere.

Dependencies and integration points: shared between platform driver, encoder dispatch, and any future encoder code needing power control.

Risks: clock-on/off prototypes returning void make it impossible for callers to react to clock enable failures unless the API changes. Include dependency on the full driver header may increase recompilation/coupling.

Test signals: compile checks and runtime encode tests that verify the PM helpers are called in balanced pairs.
