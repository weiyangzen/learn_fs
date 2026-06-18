<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc57d.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc57d.h

Purpose: `clc57d.h` defines the `NVC57D` display core class variant for a later generation than `NVC37D`. It preserves many core/window/head concepts while adding updated LUT capability fields, output resource extended-packet window selection, pixel-clock configuration, and OLUT programming.

Important APIs and types: the header defines notifier DMA context, window format and rotated-format usage bounds, window usage bounds with ILUT and TMO LUT allowance, scaler taps, and upscaling. Head methods cover procamp color space/range, output resource control including color-space override and `EXT_PACKET_WIN`, pixel clock frequency/configuration/max, head usage bounds with cursor, OLUT allowed, output scaler taps, and upscaling, raster timing, CRC context/control with explicit window/core controlling-channel values, and OLUT control/scale/context/offset.

Control flow: `corec57d.c` initializes context DMA notifier, window format usage bounds, and window usage bounds for each window using these macros. `headc57d.c` programs head timing, procamp, clocking, usage bounds, and OLUT state. `crcc57d.c` programs CRC control using the `NVC57D` selector fields.

State and persistence: programmed window/head/core bounds persist in display hardware. OLUT context/offset/control state persists per head. CRC context points at notifier memory, and output resource fields determine active head/output behavior.

Dependencies and integration: included by `corec57d.c`, `headc57d.c`, and `crcc57d.c`. It sits in the same Nouveau display stack as `NVC37D` but is not bit-compatible in all fields, so generation-specific files keep the use separated.

Risks: this class changes resource capability names and meanings: `ILUT_ALLOWED` replaces older input-LUT usage enum style, `TMO_LUT_ALLOWED` appears in window bounds, and `OLUT_ALLOWED`/OLUT control use a newer model. Output resource `EXT_PACKET_WIN` must match the window that supplies extension packets or be `NONE`. CRC controlling channel values include many window IDs plus core, so wrong values can capture the wrong stream.

Test signals: modesets on C57D-class hardware, window initialization for all windows, HDR/TMO or LUT-capability paths where supported, OLUT programming, pixel-clock hopping/configuration, and DRM CRC capture. Regressions show as unsupported-plane validation mismatch, absent LUT effects, wrong CRC source, bad output packets, or display underflow/blanking.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc57d.h -->
