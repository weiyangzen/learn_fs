# sources/distributed-fs/ceph-client/drivers/media/i2c/vp27smpx.c

Purpose: legacy V4L2 I2C subdevice driver for the VP27SMPX audio processor/multiplexer. It tracks whether the parent is using radio or TV mode and programs audio mode bytes for mono, stereo, and bilingual modes.

Important APIs/types/functions: `struct vp27smpx_state` holds the subdev, `radio` flag, and cached `audmode`. `vp27smpx_set_audmode()` writes the three-byte mode command. Subdev ops are `vp27smpx_s_radio()`, `vp27smpx_s_std()`, `vp27smpx_s_tuner()`, `vp27smpx_g_tuner()`, and `vp27smpx_log_status()`. Probe checks `I2C_FUNC_SMBUS_BYTE_DATA`, allocates state, initializes the subdev, defaults to stereo, and writes the initial mode.

Control flow: setting radio marks the device as radio and suppresses TV tuner audio programming. Setting a video standard clears radio mode. `s_tuner` applies the requested audio mode only when not in radio mode. `g_tuner` returns stereo/LANG1/LANG2 capabilities and the cached mode for TV use.

State/persistence: only cached in-memory `radio` and `audmode` exist. The chip register state is volatile and initialized at probe.

Dependencies/integration: depends on Linux I2C, V4L2 subdev tuner/video/core ops, and a parent bridge that routes tuner calls to this subdevice.

Risks/test signals: `i2c_master_send()` errors are logged but not propagated from tuner operations. Radio mode hides state changes. Tests should cover mode byte mapping for all V4L2 tuner modes, radio vs TV transitions, initial stereo write, adapter functionality rejection, and remove-time subdev unregister.
