# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/analogix/analogix-anx78xx.c

Purpose: I2C DRM bridge driver for Analogix ANX7808/7812/7814/7816/7818 SlimPort transmitters. It turns an HDMI/TMDS input into DisplayPort output, exposes a DRM connector, registers a DP AUX channel, and manages the chip's five I2C register pages.

Important APIs/types/functions: `struct anx78xx` stores the bridge, connector, AUX adapter, cached EDID, GPIO/regulator platform data, regmaps, chip ID, DPCD cache, mutex, and power flag. Probe is `anx78xx_i2c_probe`; remove is `anx78xx_i2c_remove`; bridge ops are `anx78xx_bridge_attach`, `mode_valid`, `mode_set`, `enable`, and `disable`; interrupt paths are `anx78xx_hpd_threaded_handler` and `anx78xx_intp_threaded_handler`; AUX is delegated through `anx78xx_aux_transfer` to `anx_dp_aux_transfer`.

Control flow: probe obtains DVDD10, HPD/powerdown/reset GPIOs, maps five dummy I2C clients, powers the chip, validates device ID/version, installs HPD and INTP threaded IRQs, adds the bridge, and powers off if HPD is low. Attach registers AUX, connector, helper functions, encoder link, and connector. Enable calls `anx78xx_start`, which powers TX/RX blocks, enables interrupts, initializes HDMI RX and DP TX, then asserts downstream HPD. HDMI clock/sync interrupts trigger `anx78xx_dp_link_training`; the hardware training-finish interrupt enables video output.

State and persistence: Runtime state is in-memory only: `powered`, cached `drm_edid`, DPCD capabilities, regmaps, and GPIO/IRQ handles. The mutex serializes mode setting, HPD/INTP interrupt handling, and EDID reads. EDID is cached until HPD lost or remove. No disk persistence exists.

Dependencies and integration: Depends on Linux I2C, regmap, regulator, GPIO, threaded IRQs, DRM bridge/connector/EDID helpers, HDMI AVI infoframe helpers, and DP AUX/DPCD helpers. Device-tree compatibles select ANX7808 versus ANX781x I2C address maps. The file includes `analogix-anx78xx.h`, which pulls in the shared I2C DP TX register definitions.

Risks: Power sequencing ignores some regmap errors during `anx78xx_poweron`; a failed regulator disable leaves `powered` true. Bridge attach rejects `DRM_BRIDGE_ATTACH_NO_CONNECTOR`, so it is not compatible with connectorless bridge chains. Link training relies on chip hardware and minimal post-failure recovery. IRQ handlers access hardware only under the mutex, but HPD loss powers off while other code may have already observed `powered`.

Test signals: Useful checks are probe on supported/unsupported IDs, HPD plug/unplug, EDID cache invalidation, AUX DPCD reads, mode rejection above 154 MHz or interlace, HDMI clock/sync interrupt causing link training, training-finish enabling video, and regulator/GPIO error paths.
