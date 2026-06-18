# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd937x.h

## Purpose
`wcd937x.h` is the shared register and interface contract for the WCD937x codec driver pair. It defines the analog/digital register address map, bit masks, SoundWire port and channel enumerations, interrupt numbers, the `struct wcd937x_sdw_priv` bus-private state shared between the platform and SoundWire drivers, and conditional prototypes for SoundWire helper functions.

## Important APIs, Types, and Definitions
- Register constants span analog blocks at `0x3000` and digital blocks at `0x3400`, ending at `WCD937X_MAX_REGISTER`.
- Bit masks define MBHC detection, micbias modes and voltage fields, headphone PA ground overrides, PDM watchdog bits, interrupt status/mask/clear registers, and SoundWire channel mask helpers.
- `enum wcd937x_tx_sdw_ports` and `enum wcd937x_rx_sdw_ports` assign codec data-port numbers used by the SoundWire DPN property arrays.
- `struct wcd937x_sdw_priv` is the shared SoundWire state: slave device, stream config/runtime, port configs, channel info, enable flags, master channel map, TX/RX role, aggregate-codec backpointer, slave IRQ domain, and regmap.
- Conditional declarations for `wcd937x_sdw_free()`, `wcd937x_sdw_set_sdw_stream()`, and `wcd937x_sdw_hw_params()` return `-EOPNOTSUPP` when the SoundWire companion is not built.
- `enum` interrupt IDs must align with the `wcd937x_irqs` table in `wcd937x.c`.
- TX/RX channel enums are consumed by ALSA controls and `wcd937x_connect_port()` as indexes into `ch_info`.

## Control Flow and Integration
The header itself has no executable control flow, but it governs nearly all cross-file coupling. `wcd937x-sdw.c` uses the register constants for regmap defaults/access tables and uses the SoundWire port/channel enums for static channel metadata. `wcd937x.c` uses the same constants for DAPM event register programming, MBHC callbacks, IRQ setup, DAI stream operations, and control definitions. The Kconfig conditional around helper prototypes allows the platform driver to compile even when the SoundWire module is disabled, with calls failing explicitly.

## State and Persistence Behavior
`struct wcd937x_sdw_priv` captures the persistent bus-facing state that survives across ALSA callbacks while the device is bound. Hardware persistence is represented indirectly through register constants and the regmap cache configured in `wcd937x-sdw.c`. The `port_enable`, `port_config`, and `master_channel_map` members are the software record of user-selected SoundWire paths and are later translated into stream configuration.

## Dependencies and Integration Points
The header depends on SoundWire core types and `wcd-common.h` for shared channel-info helpers and micbias definitions. It is included by both the SoundWire slave driver and platform codec driver, so changes here can break register access policy, DAPM sequencing, MBHC fields, IRQ mapping, or channel-map interpretation.

## Risks and Edge Cases
- `WCD937X_MICB_DISABLE`, `WCD937X_MICB_ENABLE`, and `WCD937X_MICB_PULL_UP` are defined twice, once around MICB1/2 and again near MICB3. The duplicate values are identical, but it increases maintenance risk.
- `WCD937X_AUXPA_CLK_EN_MASK` is also defined twice.
- RX channel enum order lists `WCD937X_DSD_R` before `WCD937X_DSD_L`, while `wcd937x-sdw.c` initializes the channel-info array with DSD_L before DSD_R. Because the platform code indexes `ch_info[ch_id]`, this should be checked for channel inversion.
- Register address or interrupt enum changes must be synchronized with regmap defaults, readable/writeable/volatile policies, MBHC field maps, and regmap-irq tables.

## Test Signals
Header-level validation is mostly build and integration based: compile both enabled and disabled SoundWire configurations, confirm no duplicate macro warnings under stricter tooling, verify regmap accesses stay within `WCD937X_MAX_REGISTER`, check IRQ enum/table alignment, and run playback/capture channel-map tests that cover every TX/RX channel enum.
