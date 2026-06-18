# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/ite-it6263.c

### Purpose
`ite-it6263.c` implements a DRM bridge for the ITE IT6263 LVDS-to-HDMI transmitter. It receives single- or dual-link LVDS input, configures LVDS input mapping and AFE settings, drives HDMI output, performs custom EDID reads over the chip DDC engine, and exposes HDMI bridge operations and infoframe programming.

### Important APIs, Types, And Functions
`struct it6263` stores HDMI and LVDS I2C clients/regmaps, the DRM bridge, downstream bridge, LVDS data mapping, dual-link state, and link swap state. Regmap callbacks define readable, writable, volatile, and banked HDMI register ranges plus a separate LVDS regmap. Important helpers are `it6263_parse_dt()`, `it6263_hw_reset()`, `it6263_lvds_set_i2c_addr()`, `it6263_lvds_config()`, `it6263_hdmi_config()`, `it6263_detect()`, `it6263_read_edid()`, bridge enable/disable, mode validation, input bus-format selection, TMDS validation, and HDMI infoframe callbacks.

### Control Flow
Probe allocates the bridge, creates the HDMI regmap on the primary I2C client, gets reset GPIO and required regulators, parses DT for LVDS data mapping, downstream bridge, and dual-link port order, performs hardware reset, programs the LVDS subaddress through HDMI registers, creates a dummy LVDS I2C client/regmap, initializes LVDS and HDMI blocks, and registers the bridge. Attach first attaches the downstream bridge with no connector; if the caller did not request no-connector, it creates a bridge connector and attaches it to the encoder. Atomic enable switches HDMI mode on, updates HDMI infoframes, configures HDMI AFE according to the adjusted pixel clock, pulses video reset, polls for stable input video with LVDS reconfiguration retries, releases AFE reset/power-down, clears AVMUTE, and enables repeated packets. Atomic disable mutes and powers down AFE.

### State, Persistence, And Dependencies
Software state is retained in the regmaps, bridge, downstream reference, LVDS mapping flags, and regulator/reset-managed resources. Hardware state persists in HDMI and LVDS register banks, including LVDS color depth/mapping/dual-link mode, HDMI reset, input RGB mode, GCP color depth, AFE controls, DDC state, and packet registers. Dependencies include DRM bridge connector helpers, DRM HDMI state helpers, DRM OF LVDS helpers, regmap bank selection, I2C dummy devices, GPIO reset, regulator bulk enable, and media-bus formats.

### Integration Points
The bridge consumes LVDS input formats `MEDIA_BUS_FMT_RGB888_1X7X4_JEIDA` or `MEDIA_BUS_FMT_RGB888_1X7X4_SPWG`, advertises HDMI-A output, supports HPD detect by polling `HPDETECT`, reads EDID with `drm_edid_read_custom()`, and forwards to a downstream bridge from DT port 2. It participates in HDMI atomic state through TMDS character-rate validation and AVI/HDMI infoframe callbacks.

### Risks
The chip lacks HPD interrupts, so detection is poll-driven. EDID reads depend on DDC polling and FIFO chunking; timeout or DDC error handling must be robust. `it6263_parse_dt()` rejects single-input port1 layouts and requires a valid `data-mapping`. Dual-link ordering affects `REG_LVDS_IN_SWAP`, so incorrect DT silently swaps pixels. Atomic enable tolerates unstable video after three retries with only a warning. Infoframe bulk writes assume the DRM helper-provided buffer is long enough for the chip register layout.

### Test Signals
Test single-link port0, dual-link odd/even and even/odd DTs, missing or invalid `data-mapping`, all required regulator failures, reset GPIO timing, LVDS dummy I2C creation, EDID reads including extension blocks and DDC error bits, TMDS rejection above 225 MHz and pixel clocks above 150 MHz, pclk-high AFE threshold at 80 MHz, bridge connector creation, and AVI/HDMI infoframe register writes.
