<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_drv.c -->
# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_drv.c

## Purpose

`adv7511_drv.c` is the main DRM bridge and I2C driver for Analog Devices ADV7511/ADV7513/ADV7533/ADV7535 HDMI transmitters. It handles register-map setup, hardware patches, power/HPD/EDID, video mode programming, HDMI infoframes, optional bridge connector creation, CEC regmap setup, regulator/GPIO setup, DSI companion attachment, and module registration.

## Important APIs, Types, And Functions

- Register data: `adv7511_fixed_registers`, `adv7511_register_defaults`, volatile-register predicate, and regmap configs for main, packet, and CEC maps.
- Video helpers: `adv7511_set_colormap()`, packet enable/disable, `adv7511_set_config_csc()`, `adv7511_set_link_config()`, and `adv7511_mode_set()`.
- Power/HPD/EDID helpers: `__adv7511_power_on/off()`, `adv7511_power_on/off()`, `adv7511_hpd_work()`, `adv7511_irq_process()`, `adv7511_wait_for_edid()`, `adv7511_get_edid_block()`, `adv7511_edid_read()`, and `adv7511_detect()`.
- DRM bridge funcs: atomic enable/disable, mode/TMDS validation, attach, detect, EDID read, HDMI infoframe clear/write hooks, optional audio hooks, and optional CEC hooks.
- Probe/remove: regulator init, ancillary EDID/packet/CEC I2C devices, chip-specific register patching, DT parsing, bridge registration, IRQ request, and ADV7533 DSI attach.
- Chip metadata for ADV7511, ADV7533, and ADV7535 plus I2C/OF IDs and module init/exit that registers both MIPI DSI and I2C drivers when configured.

## Control Flow

Probe validates OF data, allocates the bridge object, finds downstream bridge, parses either parallel RGB link config or ADV7533 DSI DT, enables supplies and optional powerdown GPIO, creates regmaps and ancillary I2C clients, applies chip patches, initializes CEC regmap, powers the chip off into a clean cached state, configures bridge ops and optional audio/CEC metadata, registers the bridge, requests IRQ, and attaches DSI for ADV7533/7535. Atomic enable powers on, retrieves connector and CRTC state, configures CSC/output mode, programs timing, and updates HDMI infoframes. Atomic disable powers off. EDID reads temporarily power the chip if needed and fetch 256-byte EDID segments via four 64-byte I2C reads. IRQ handling acknowledges INT0/INT1, schedules HPD work, wakes EDID waits, and dispatches CEC.

## State And Persistence Behavior

Persistent software state is the `struct adv7511` allocated with the bridge: power flag, connector status, current mode, TMDS clock, EDID cache/segment, waitqueue/work item, input color/sync flags, ancillary I2C clients/regmaps, regulator array, DSI state, and CEC state. Hardware state persists in ADV7511 registers but many registers reset on powerdown or HPD low; the driver uses regcache dirty/sync to restore cached state.

## Dependencies And Integration Points

The driver depends on I2C, regmap cache, regulators, optional GPIO, OF graph, DRM bridge/bridge-connector/HDMI state helpers, EDID helpers, optional ASoC audio, optional CEC, and MIPI DSI for ADV7533/7535. It integrates with downstream bridges through `drm_of_find_panel_or_bridge()` and `drm_bridge_attach()`.

## Risks And Edge Cases

The chip can reset registers on unplug, so HPD handling must mark regcache dirty and repower to restore state. EDID retrieval supports IRQ and polling paths; missed interrupts or DDC errors surface as `-EIO`. Link-config DT parsing is strict about depth, colorspace, clock style, input style, justification, and clock delay. Error paths must unregister ancillary I2C clients and disable CEC clocks/regulators in the right order. ADV7535 HPD override behavior differs from other variants. Infoframe writes assume buffers include the HDMI packet type byte and bulk-write `buffer + 1`.

## Test Signals

Probe/remove error-path tests, EDID read with IRQ and polling, HPD plug/unplug while powered, DVI vs HDMI sink mode, YCbCr-to-RGB CSC and YCbCr422 output, low-refresh modes, infoframe contents, TMDS clock limits, ADV7533/7535 DSI mode validation/attach, suspend-like power cycles, audio/CEC Kconfig combinations, and regcache restoration after HPD reset are key signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/adv7511/adv7511_drv.c -->
