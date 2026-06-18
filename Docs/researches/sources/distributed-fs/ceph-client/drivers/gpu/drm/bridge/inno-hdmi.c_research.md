# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/inno-hdmi.c

### Purpose
`inno-hdmi.c` is a reusable DRM bridge library for Innosilicon HDMI transmitters. It initializes the HDMI block, manages PHY power and platform-specific PHY tables, exposes HDMI bridge operations including HPD, EDID, infoframes, and mode validation, and implements a small DDC I2C adapter backed by the controller's EDID FIFO.

### Important APIs, Types, And Functions
`struct inno_hdmi` stores the bridge, pclk/refclk, MMIO registers, optional GRF regmap, DDC adapter, I2C state, and platform data. `struct inno_hdmi_i2c` tracks DDC offsets, segment pointer, mutex, and EDID completion. The exported entry point is `inno_hdmi_bind()`. Important helpers include `inno_hdmi_find_phy_config()`, `inno_hdmi_i2c_init()`, `inno_hdmi_init_hw()`, `inno_hdmi_standby()`, `inno_hdmi_power_up()`, `inno_hdmi_setup()`, `inno_hdmi_config_video_timing()`, `inno_hdmi_config_video_csc()`, bridge EDID/detect/infoframe callbacks, IRQ handlers, and the `inno_hdmi_i2c_xfer()` adapter implementation.

### Control Flow
`inno_hdmi_bind()` validates platform PHY data, allocates the bridge object, maps registers, enables `pclk` and optional `ref`, initializes hardware, requests a threaded IRQ, configures bridge identity and operations, creates the DDC adapter, registers the bridge, and attaches it to the encoder. Hardware init releases digital and analog resets, selects clock/power defaults, enters standby, configures DDC based on refclk or pclk, and unmasks HPD. Atomic enable calls `inno_hdmi_setup()`, which mutes audio/video, sets HDMI or DVI mode from sink display info, writes external timing registers, configures CSC/output range using connector HDMI state, updates infoframes through DRM helpers, recalculates DDC timing from the TMDS character rate, unmutes, and powers the PHY up. Atomic disable enters standby. Hard IRQ handles EDID-ready completion and HPD status; the threaded IRQ emits a DRM HPD event.

### State, Persistence, And Dependencies
Software state is the bridge object, DDC adapter state, clock handles, and platform PHY configuration. Hardware state persists in controller registers for resets, video timing, CSC coefficients, packet buffers, PHY driver/pre-emphasis/power, DDC timing, and interrupt masks. Dependencies include DRM HDMI state helpers, DRM bridge helpers, DRM EDID/DDC, platform-specific `inno_hdmi_plat_data`, MMIO register access, Linux I2C adapter APIs, IRQ handling, and clk APIs.

### Integration Points
This file is not a standalone platform driver; SoC-specific drivers bind it by calling `inno_hdmi_bind()` with an encoder and platform PHY configuration. It exposes a connector type of HDMI-A, bridge HDMI operations for AVI infoframes, HPD detect, EDID read through its DDC adapter, and mode validation based on minimum TMDS rate, PHY table maximum, and optional refclk rounding tolerance.

### Risks
The DDC engine only supports EDID-style reads; arbitrary I2C messages are rejected or interpreted as EDID offset/segment writes. HDMI Vendor Specific InfoFrame operations warn once but do not implement VSI transmission. CSC programming only handles selected RGB and YCbCr444 paths. Mode setup assumes connector and CRTC state are available from the atomic state. PHY fallback uses a default config when no table entry matches during power-up, while mode_valid would reject the same clock earlier. DDC read waits only `HZ / 10`, so slow EDID transactions can fail with `-EAGAIN`.

### Test Signals
Test bridge bind with missing PHY tables, pclk/refclk failures, HPD high/low IRQs, EDID reads across block 0 and extension segments, DDC timeout and invalid write messages, min/max TMDS mode validation, refclk tolerance rejection, RGB full/limited CSC paths, AVI infoframe writes, standby/power-up register sequencing, and SoC platform `enable()` callbacks during timing setup.
