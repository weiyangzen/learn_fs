# sources/distributed-fs/ceph-client/drivers/gpu/drm/display/drm_scdc_helper.c

Purpose: implements HDMI 2.0 Status and Control Data Channel helpers over the DDC I2C adapter, covering raw SCDC read/write operations, scrambling status, scrambling enable, and high TMDS clock ratio control.

Important APIs/types/functions: exports `drm_scdc_read`, `drm_scdc_write`, `drm_scdc_get_scrambling_status`, `drm_scdc_set_scrambling`, and `drm_scdc_set_high_tmds_clock_ratio`. It uses SCDC register constants and bit definitions from `drm_scdc_helper.h` and connector DDC access through `connector->ddc`.

Control flow: `drm_scdc_read` performs a two-message I2C transaction to slave address `0x54`, first writing the offset and then reading the requested block, returning `-EPROTO` on short transfer. `drm_scdc_write` allocates a temporary buffer containing offset plus payload and sends one I2C write message. Scrambling and clock-ratio helpers read `SCDC_TMDS_CONFIG`, set or clear the relevant bit, write it back, and log connector-scoped debug errors on failure. Scrambling status reads `SCDC_SCRAMBLER_STATUS`. High TMDS ratio waits 1-2 ms after a successful write as required by the spec.

State and persistence: no kernel-side state is retained. Persistent state lives in the sink's SCDC registers and is lost on disconnect or some sink power transitions. The file documentation explicitly notes drivers may need detect/hotplug logic or empty modesets to restore SCDC state after reconnect.

Dependencies and integration: uses Linux I2C transfers, memory allocation, microsecond sleeps, DRM connector/device debug logging, and HDMI 2.0 link training paths in drivers such as VC4, i915, Tegra, Mediatek, and Synopsys DW-HDMI.

Risks: SCDC operations fail if the DDC adapter is absent, the sink is disconnected, or transfer counts are short. The read-modify-write sequence can race with external link management if drivers do not serialize HDMI enable/disable. Losing SCDC state on hotplug can leave high-rate HDMI links unsynchronized until the driver reprograms scrambling and clock ratio.

Test signals: hardware/integration tests should exercise >340 MHz HDMI 2.0 modes, scrambling enable/disable, reconnect restoration, DDC error handling, and clock-ratio timing. Unit-style tests can mock I2C transfer counts and verify `-EPROTO`/`-ENOMEM` behavior.
