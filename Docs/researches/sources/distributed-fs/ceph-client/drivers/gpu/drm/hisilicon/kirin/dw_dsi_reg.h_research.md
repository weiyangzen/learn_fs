# sources/distributed-fs/ceph-client/drivers/gpu/drm/hisilicon/kirin/dw_dsi_reg.h

Purpose: defines DesignWare DSI host and D-PHY register offsets, bit values, mode enums, and a register update helper for Kirin DSI.

Important APIs/types: register macros include core power, clock manager, PHY reset/test/status, PHY timing test codes, DPI color/polarity, video horizontal/vertical timing, packet size, video mode, BTA/LP timers, LP clock control, and mode config. Enums define DPI color coding, video mode type, and command/video work mode. `dw_update_bits()` performs read-modify-write bitfield updates.

Control flow: no independent flow. `dw_drm_dsi.c` consumes these definitions while programming PHY, timing, video mode, and core power state.

State and persistence: DSI hardware state is the register values written via these offsets. The header carries no software storage.

Dependencies and integration points: includes Linux IO and assumes bit macros. It is specific to the DesignWare DSI version used by the Kirin driver.

Risks: `MASK(x)` uses `BIT(x) - 1`, so inputs must remain in valid bit-width ranges. Wrong register codes or offsets can break PHY bring-up. The helper shifts `mask` by `bit_start`, so callers must pass an unshifted mask.

Test signals: DSI controller register trace during panel enable, PHY lock/status, video timing output, and compile coverage of all macros used by `dw_drm_dsi.c`.
