<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37a.h -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37a.h

Purpose: `clc37a.h` defines the `NVC37A` cursor immediate/display cursor channel methods. It is a very small ABI header for cursor update submission and output hotspot programming.

Important APIs and types: `NVC37A_UPDATE` triggers the cursor channel update. `NVC37A_SET_CURSOR_HOT_SPOT_POINT_OUT(b)` is an indexed method that packs X in bits 15:0 and Y in bits 31:16. The header contains no structs or functions.

Control flow: `dispnv50/cursc37a.c` includes this header and emits hotspot/update methods during cursor atomic updates. The expected sequence is to program one or more hotspot output points and then issue `UPDATE`, coordinated with the core/window display update path as needed.

State and persistence: hotspot coordinates persist in the cursor channel until changed. The cursor image memory and enable state are controlled by related core/head methods in `NVC37D`/`NVC57D`-style headers, while this file handles the immediate cursor-position-style update surface.

Dependencies and integration: direct dependencies are Nouveau display cursor code and pushbuffer helpers. It complements `NVC37D_HEAD_SET_CONTROL_CURSOR` and related cursor context/offset methods, rather than replacing them.

Risks: this class uses 16-bit X/Y packing, unlike older core cursor control fields that pack smaller hotspot values. Incorrect index `b` or missed `UPDATE` can leave stale cursor position/hotspot state. Because cursor moves are latency-sensitive, interlock mistakes can show up as cursor tearing or lag.

Test signals: hardware cursor movement, hotspot correctness at screen edges, multi-head cursor placement, and rapid cursor updates. A good runtime signal is cursor movement without full modeset and without visible flicker or coordinate truncation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/nouveau/include/nvhw/class/clc37a.h -->
