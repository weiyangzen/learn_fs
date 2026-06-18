# sources/distributed-fs/ceph-client/drivers/gpu/drm/vc4/vc4_hdmi.h

## Purpose

`vc4_hdmi.h` defines the shared HDMI driver interface and state containers used by `vc4_hdmi.c` and `vc4_hdmi_phy.c`. It describes variant-specific behavior, live HDMI device state, audio substate, lane identifiers, container conversion helpers, and PHY function prototypes for VC4, VC5, and VC6 HDMI blocks.

## Important APIs, Types, and Functions

- `enum vc4_hdmi_phy_channel` names the three data lanes and clock lane used by lane-mapping tables.
- `struct vc4_hdmi_variant` is the key abstraction for hardware generations. It contains encoder identity, ALSA/debugfs names, max pixel clock, variant register table, lane mapping, hardware quirks, resource/reset/CSC/timing/PHY callbacks, channel-map callback, HDR flag, and HPD callback.
- `struct vc4_hdmi_audio` stores the ASoC card/link/component fields, DMA data, and streaming flag.
- `struct vc4_hdmi` stores the entire controller instance: audio must be first, followed by platform and variant references, VC4 encoder, DRM connector, delayed SCDC work, DDC, MMIO bases, GPIO HPD, coexistence flag, CEC state, clocks, reset, debugfs regsets, hardware lock, cross-framework mutex, saved mode/output state, packet RAM/SCDC flags, and HDMI jack.
- `connector_to_vc4_hdmi()` and `encoder_to_vc4_hdmi()` provide safe container conversions.
- Prototypes expose `vc4_hdmi_phy_*`, `vc5_hdmi_phy_*`, and `vc6_hdmi_phy_*` implementation functions.

## Control Flow

The header itself has no executable control flow beyond `encoder_to_vc4_hdmi()`. Its structure drives runtime control in the C files: bind selects a `vc4_hdmi_variant`, stores it in `struct vc4_hdmi`, then all major operations dispatch through variant callbacks for resource acquisition, reset, CSC, timings, PHY, RNG, channel map, and HPD.

## State and Persistence

All fields are volatile kernel state. The header documents the intended locking model: `hw_lock` protects register access, `mutex` protects state shared by KMS/ALSA/CEC, `saved_adjusted_mode`, `packet_ram_enabled`, `scdc_enabled`, `output_bpc`, and `output_format` are mutex-protected copies used outside immediate atomic commit context. No fields are persistent across driver unbind; device tree and platform match data reconstruct variant state.

## Dependencies and Integration Points

The header depends on DRM connector types, CEC messages, ASoC and DMAEngine audio types, and local `vc4_drv.h`. It is consumed by the HDMI core, PHY implementation, register accessors, and other VC4 files that need encoder/container conversion or PHY prototypes.

## Risks and Edge Cases

- `BUILD_BUG_ON()` assumptions in the audio init path require `struct vc4_hdmi_audio` and `struct vc4_hdmi` layout to keep audio/card at offset zero; moving fields would break the driver.
- Variant callbacks are mandatory for many paths but may be NULL for unsupported generation features, so new variants must fill fields carefully.
- Locking comments in this header are part of the contract; adding new users of saved mode, packet RAM, SCDC, or audio state without respecting `mutex` can create KMS/ALSA/CEC races.
- The VC5-only MMIO and debugfs fields are used by VC6 too through the same register-base enum names, so comments are historical rather than strict type separation.

## Test Signals

Compile-time layout checks, allmodconfig/build coverage, KUnit mock construction of VC4 devices, and variant probing on BCM2835/BCM2711/BCM2712 are the key signals. Any new field that changes layout or callback requirements should be validated by HDMI bind, audio registration, and PHY init paths.
