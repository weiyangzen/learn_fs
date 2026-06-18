<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37d.h

Purpose: `clc37d.h` defines the `NVC37D` display core class for newer display hardware. It describes notifier layout, core update/interlock methods, SOR control, window resource usage bounds, and head-level procamp, timing, cursor, LUT, and CRC methods.

Important APIs and types: `NV_DISP_NOTIFIER` describes present status, count, field, flip type, and timestamps. `NVC37D_UPDATE` includes special handling, reason, and interrupt inhibition. Notifier control sets DMA handle, offset, awaken/write mode, and notify enable. Interlock methods cover cursor, core, and up to 32 windows. SOR control supports owner masks for heads 0-7 and DSI in addition to LVDS/TMDS/DP. Window usage bounds define supported RGB/YUV format families, rotated format support, max pixels fetched per line, input LUT use, scaler taps, and upscaling. Head methods cover procamp with BT.2020 and black-level controls, output resource controls with color-space override, pixel clocks, dither up to 12 bits, head usage bounds, viewport/raster timing, cursor context/offset/control/composition, output LUT control/address/context, and CRC control.

Control flow: `corec37d.c` emits global core/window usage bounds and update/notifier/interlock methods. `headc37d.c` programs head timing, procamp, dither, cursor, viewport, and LUT state. `sorc37d.c` sets SOR routing. `crcc37d.c` programs CRC context/control using the compact primary/secondary CRC selector fields.

State and persistence: core/head/window bounds and routing persist in display hardware across atomic commits. Notifier memory persists present completion state and timestamps. Interlock flags control synchronization of updates across display channels.

Dependencies and integration: included by the Volta/Turing display implementation files under `dispnv50/`. It integrates with DRM atomic state, Nouveau's display channel abstractions, DMA notifier buffers, and `NVDEF`/`NVVAL` push helpers.

Risks: this class changes many field offsets from `NV907D`, especially head base offsets, cursor format encoding, CRC selectors, and dither bits. Incorrect interlock flags can cause partially applied multi-plane updates. Window format-usage bounds gate what later window channels are allowed to scan out; overly broad or narrow bounds can create validation/hardware mismatches.

Test signals: multi-head modesets, window/plane format validation including YUV families, cursor sizes and composition, LUT/color management, DP/DSI/TMDS routing, display CRC capture, and atomic commits involving several windows with interlocks. Failures appear as atomic check/commit mismatches, underflow, wrong color, failed CRC setup, or display channel errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37d.h -->
