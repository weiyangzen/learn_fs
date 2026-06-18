# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx78xx.h

Purpose: Register map header for the ANX78xx HDMI receiver and related TX page definitions used by `analogix-anx78xx.c`.

Important APIs/types/functions: It exports no functions or types. It includes `analogix-i2c-dptx.h` and `analogix-i2c-txcommon.h`, then defines RX_P0, RX_P1, and TX_P1 register addresses and bitfields for software reset, HDMI status, mute, power-down, audio/video auto control, interrupts, TMDS, video status, audio channel status, chip control, HDCP shadow/status, infoframes, control packets, DP TX link-training tuning, and firmware version.

Control flow: There is no executable control flow. The C driver uses these constants to reset HDMI RX blocks, mute/unmute audio/video, detect TMDS clock/data, configure TMDS PHY, send AVI infoframes, mask and clear HDMI interrupts, drive HPD output, and tune DP TX output emphasis.

State and persistence: The header names volatile hardware state only. Register bits reflect or control chip state across power transitions, but the header itself has no runtime memory. Cache and persistence decisions live in the C driver.

Dependencies and integration: Requires Linux `BIT()` definitions through including C files. It is part of the Analogix I2C bridge register namespace and deliberately composes with the DPTX and TX-common headers to cover the multiple I2C pages used by the chip.

Risks: Several definitions target undocumented or reserved hardware behavior, including an explicitly noted undocumented audio sample-change bit and register writes described in the C file as touching reserved bits. Wrong bit masks here can produce silent hardware bring-up failures, not compile-time failures.

Test signals: Compile coverage from `analogix-anx78xx.c`, register-trace comparison against datasheet sequences, interrupt mask/status behavior, AVI infoframe write locations, and TMDS clock/data detection are the practical validation points.
