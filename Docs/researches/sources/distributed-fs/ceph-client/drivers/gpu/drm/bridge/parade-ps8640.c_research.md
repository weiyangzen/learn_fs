# sources/distributed-fs/ceph-client/drivers/gpu/drm/bridge/parade-ps8640.c

## Purpose

`parade-ps8640.c` drives the Parade PS8640 MIPI DSI-to-eDP bridge. It exposes a DRM bridge that accepts a fixed 4-lane RGB888 MIPI DSI input, links to a downstream eDP panel bridge, and provides a `drm_dp_aux` channel for EDID and panel AUX transactions. The chip is addressed as eight adjacent I2C pages, each wrapped in a no-cache 8-bit regmap.

## Important APIs, Types, And Functions

The main state is `struct ps8640`: DRM bridge, downstream panel bridge, DP AUX object, generated MIPI DSI device, page clients/regmaps, `vdd12`/`vdd33` regulators, reset/powerdown GPIOs, a stateless device link, `pre_enabled`, `need_post_hpd_delay`, and `aux_lock`.

Important callbacks are `ps8640_probe()`, `ps8640_bridge_get_dsi_resources()`, `ps8640_bridge_link_panel()`, `ps8640_bridge_attach()/detach()`, `ps8640_atomic_pre_enable()`, `ps8640_atomic_post_disable()`, runtime PM `ps8640_resume()/suspend()`, and AUX operations `ps8640_aux_transfer()` and `ps8640_wait_hpd_asserted()`. Register-level helpers include `_ps8640_wait_hpd_asserted()`, `ps8640_aux_transfer_msg()`, and `ps8640_bridge_vdo_control()`.

## Control Flow

Probe allocates the bridge, obtains regulators and GPIOs, records eDP connector type, discovers the upstream DSI host from port 0, creates a DSI device, builds dummy I2C clients/regmaps for pages 1-7, initializes DP AUX, enables runtime PM autosuspend, and links the downstream panel either through an AUX bus child or directly through port 1. Attach registers the AUX channel, creates a device link from DRM device to I2C device, and attaches the panel bridge after this bridge.

Runtime resume powers regulators, deasserts powerdown, performs a double reset, marks that a first-HPD delay is needed, and waits 200 ms for firmware. Pre-enable runtime-resumes the chip, waits for GPIO9-as-HPD, disables panel MCS, enables I2C bypass for EDID access, and enables DSI video. Post-disable disables video and synchronously suspends runtime PM under `aux_lock` so AUX transfers cannot keep the bridge powered during shutdown.

AUX transfers serialize with `aux_lock`, runtime-resume the chip, wait for HPD, program SWAUX address/length/request registers, optionally push write payload bytes, trigger `SWAUX_SEND`, poll completion, translate hardware ACK/NACK/DEFER/TIMEOUT into DP AUX replies, and pull read payload from the internal FIFO.

## State And Persistence Behavior

Driver state is volatile and device scoped. `need_post_hpd_delay` survives only across one resume-to-first-HPD sequence. `pre_enabled` tracks display pipeline state but is not otherwise used for persistence. Register caches are disabled, so every regmap operation reaches hardware. Power state is managed by runtime PM with a 2 second autosuspend delay to avoid repeated 300 ms power cycles during EDID/AUX activity.

## Dependencies And Integration Points

The driver integrates with DRM bridge, DRM DP AUX bus, MIPI DSI host registration, OF graph port 0/1 topology, regulator and GPIO frameworks, runtime PM, regmap, and device links. It depends on downstream panel bridge discovery and may defer probe until the upstream DSI host or downstream panel is available.

## Risks

Risks include the undocumented HPD-on-GPIO9 behavior, hard-coded reset delays, AUX transaction error handling, fixed four-lane RGB888 DSI assumptions, and the need to keep power sequencing synchronized with AUX operations. The code ignores the return from some regmap writes/polls in `ps8640_aux_transfer_msg()`, so failures can be reported later or as misleading status. Incorrect OF graph wiring prevents either DSI registration or panel linking.

## Test Signals

Useful signals are successful probe with eight I2C pages, runtime PM resume/suspend without regulator or GPIO errors, EDID reads through AUX, HPD wait behavior after reset, display enable/disable with video control toggling, no AUX timeout during connector probing, and suspend/resume cycles without stale power references.
