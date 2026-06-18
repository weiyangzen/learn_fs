# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd937x-sdw.c

## Purpose
`wcd937x-sdw.c` is the SoundWire slave-side companion for the WCD9370/WCD9375 codec platform driver. It describes RX/TX SoundWire data ports, channel-to-port mappings, the CSR regmap reachable through the TX SoundWire device, interrupt forwarding from SoundWire out-of-band events into a Linux IRQ domain, and runtime PM cache behavior. The platform codec driver in `wcd937x.c` binds this RX/TX pair through the component framework and uses the TX instance as the main register interface.

## Important APIs, Types, and Functions
- `wcd937x_sdw_rx_ch_info` and `wcd937x_sdw_tx_ch_info` map logical codec channels such as `WCD937X_HPH_L`, `WCD937X_ADC1`, `WCD937X_MBHC`, and DMIC channels to SoundWire port numbers and channel masks.
- `wcd937x_dpn_prop` declares five simple SoundWire data ports with one to four/eight channels and simple channel prepare state machines.
- `wcd937x_sdw_hw_params()` builds an `sdw_stream_config` and active `sdw_port_config` array from the per-port masks selected by mixer controls in `wcd937x.c`, then calls `sdw_stream_add_slave()`.
- `wcd9370_interrupt_callback()` delegates SoundWire interrupt handling to `wcd_interrupt_callback()` over the shared slave IRQ domain and the three digital interrupt status registers.
- `wcd937x_defaults`, `wcd937x_rdwr_register()`, `wcd937x_readable_register()`, and `wcd937x_volatile_register()` define the regmap cache defaults and register accessibility policy for the codec CSR space.
- `wcd9370_probe()` initializes the per-slave private state, reads static port/channel mappings from device tree, configures SoundWire properties, creates the TX regmap, and registers the slave as a component.
- Runtime PM callbacks switch the TX regmap into cache-only mode on suspend and resync it on resume.

## Control Flow
Probe allocates `struct wcd937x_sdw_priv`, decides whether the SoundWire slave is TX by checking `qcom,tx-port-mapping`, reads TX or RX port maps into `pdev->m_port_map[1...]`, and optionally reads channel mapping arrays. TX instances configure `source_ports`, `src_dpn_prop`, wake capability, and the SoundWire regmap; RX instances configure `sink_ports` and do not own a regmap. Both attach `wcd_sdw_component_ops` through `component_add()` so the platform device can later call `component_bind_all()`.

Audio stream setup is driven from `wcd937x_codec_hw_params()` in `wcd937x.c`: mixer controls update `wcd->port_config[*].ch_mask`, then `wcd937x_sdw_hw_params()` copies only active ports into a compact array and adds the slave to the existing SoundWire stream runtime. Direction is selected from `wcd->is_tx`. Interrupts arrive via `sdw_slave_ops.interrupt_callback`, which triggers the codec IRQ domain consumed by regmap-irq and MBHC/watchdog logic in the platform driver.

## State and Persistence Behavior
The persistent runtime state is in `struct wcd937x_sdw_priv`: `sdev`, `sconfig`, `sruntime`, selected `port_config`, channel metadata, `master_channel_map`, `active_ports`, `is_tx`, backpointer to the aggregate codec, `slave_irq`, and optional `regmap`. Hardware register state is cached by REGCACHE_MAPLE and seeded from the large `wcd937x_defaults` table. Suspend marks the regcache dirty and cache-only; resume disables cache-only and calls `regcache_sync()`, so late register writes during suspend are replayed.

## Dependencies and Integration Points
This file depends on Linux SoundWire core (`sdw_slave`, `sdw_stream_add_slave`, `sdw_dpn_prop`), regmap, runtime PM, component framework, ASoC headers, and shared Qualcomm helpers from `wcd-common.h`/`wcd937x.h`. The key integration is with `wcd937x.c`, which provides the aggregate component, consumes the TX regmap, manages SoundWire stream callbacks, and fills port masks through user controls and DAPM decisions. Device tree must provide `qcom,rx-port-mapping`/`qcom,tx-port-mapping`, and may provide channel mapping arrays.

## Risks and Edge Cases
- `wcd937x_sdw_hw_params()` initializes `sconfig.ch_count` to `1` before counting set channel bits. Tests should confirm this matches SoundWire expectations for all mono/stereo/multichannel port selections.
- TX channel entries for `ADC2` and `ADC3` both use `BIT(0)` on `WCD937X_ADC_2_3_PORT`; correctness depends on static channel mapping or codec-specific port semantics and deserves hardware validation.
- The DSD RX enum order in `wcd937x.h` puts `WCD937X_DSD_R` before `WCD937X_DSD_L`, while this file lists the channel info as L then R. Since `wcd937x_connect_port()` indexes `ch_info[ch_id]`, this can invert DSD channel masks if not intentional.
- Missing device-tree port/channel mappings are logged with `dev_info()` and the driver continues, so broken board data may fail later as silent channel-map issues.
- Only TX instances own a regmap; platform bind must always find and link the TX device before codec registration.

## Test Signals
Useful validation signals include successful SoundWire enumeration of both RX and TX slaves, `component_bind_all()` reaching the platform codec, `regcache_sync()` succeeding after runtime resume, ALSA playback/capture hw_params exercising enabled port masks, `get_channel_map()` returning expected master channel masks, interrupt delivery through MBHC and PDM watchdog lines, and suspend/resume audio smoke tests with cached register writes.
