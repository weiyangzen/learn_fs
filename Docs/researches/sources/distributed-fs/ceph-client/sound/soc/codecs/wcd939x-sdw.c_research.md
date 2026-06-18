<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x-sdw.c -->
# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x-sdw.c

## Purpose

`wcd939x-sdw.c` is the SoundWire slave driver for Qualcomm WCD939x codec RX/TX child devices. It provides channel-to-port metadata, data-port properties, ALSA-to-SoundWire stream setup helpers exported to the main WCD939x codec driver, interrupt forwarding from SoundWire out-of-band events into the codec regmap IRQ domain, regmap defaults and access policy for the TX CSR interface, component-framework registration, and runtime PM cache handling.

This file is a transport and register-access layer rather than the full ASoC codec policy. The aggregate WCD939x codec driver owns the high-level controls and DAPM behavior; this SoundWire child driver gives that aggregate driver a regmap, SoundWire stream operations, and RX/TX child component instances.

## Important APIs, types, and functions

`wcd939x_sdw_rx_ch_info` and `wcd939x_sdw_tx_ch_info` define logical codec channels with `WCD_SDW_CH(channel_id, port_num, channel_mask)`. RX channels cover HPH L/R, class-H, compander L/R, line-out, DSD L/R, and HIFI PCM L/R. TX channels cover ADC1-4, DMIC0-7, and MBHC. The TX table maps both `WCD939X_MBHC` and `WCD939X_DMIC2` to `WCD939X_DMIC_0_3_MBHC_PORT` bit 2, which makes those logical functions mutually dependent on the same SoundWire channel bit.

`wcd939x_rx_dpn_prop` and `wcd939x_tx_dpn_prop` advertise SoundWire data-port capabilities to the SoundWire core. RX ports support simple data ports with 1-2 channels for HPH, compander, DSD, and HIFI PCM, and 1 channel for CLSH and LO. TX ports support simple 1-4 channel source ports for ADC, ADC/DMIC, DMIC/MBHC, and upper DMIC groups.

The exported stream helpers are `wcd939x_sdw_hw_params()`, `wcd939x_sdw_free()`, and `wcd939x_sdw_set_sdw_stream()`. The main codec DAI callbacks call these helpers with a `struct wcd939x_sdw_priv` child object. `hw_params()` builds an active `sdw_port_config` array from nonzero `wcd->port_config[i].ch_mask`, fills `sdw_stream_config` with frame rate, direction, and PCM type, and calls `sdw_stream_add_slave()`. `free()` removes the slave from the stream. `set_sdw_stream()` stores the `sdw_stream_runtime` pointer.

Interrupt handling is implemented by `wcd9390_interrupt_callback()`, which calls common `wcd_interrupt_callback()` with the child `slave_irq` domain and the three WCD939x digital interrupt status registers. This bridges SoundWire implementation-defined interrupts to the regmap IRQ machinery owned by the aggregate codec.

Regmap support is defined by `wcd939x_defaults`, `wcd939x_rdwr_register()`, `wcd939x_readable_register()`, `wcd939x_volatile_register()`, `wcd939x_writeable_register()`, and `wcd939x_regmap_config`. The defaults table covers analog, MBHC, TX, RX, class-H, flyback, digital CDC, interrupt, pad, dem, RX_TOP, compander, ear and DSD registers. The access callbacks split ordinary read/write registers from read-only status/efuse/result/debug registers and volatile status/result/interrupt/debug registers. The regmap uses 32-bit register addresses, 8-bit values, `REGCACHE_MAPLE`, and `WCD939X_MAX_REGISTER`.

Device lifecycle is handled by `wcd9390_probe()`, `wcd9390_remove()`, `wcd939x_sdw_runtime_suspend()`, and `wcd939x_sdw_runtime_resume()`. The SoundWire driver is registered by `module_sdw_driver(wcd9390_codec_driver)` with SoundWire device ID vendor `0x0217`, part `0x10e`.

## Control flow

At SoundWire probe, `wcd9390_probe()` allocates `struct wcd939x_sdw_priv`, detects whether this child is TX by checking for `qcom,tx-port-mapping`, and reads either TX or RX static port mapping into `pdev->m_port_map[1]` because WCD data ports start at index 1. Missing static mapping is informational rather than fatal. It then stores the SoundWire slave pointer, configures SCP interrupt masks, lane-control and simple clock-stop capability, assigns source or sink port bitmaps and DPN property arrays, and assigns the appropriate channel-info table.

Only TX children create a regmap with `devm_regmap_init_sdw()`, because the TX SoundWire device is the main CSR register interface. That regmap starts in cache-only mode until SoundWire enumeration and aggregate binding make hardware access safe. Both RX and TX children register with the component framework through `component_add(dev, &wcd_sdw_component_ops)`, allowing the aggregate codec platform driver to bind them.

When the aggregate ASoC DAI configures a PCM stream, `wcd939x_sdw_set_sdw_stream()` first stores the SoundWire stream runtime. `wcd939x_sdw_hw_params()` scans `wcd->port_config` for enabled channel masks, copies active ports into a local array, computes a channel count from set bits, fills `sconfig`, selects TX or RX direction from `wcd->is_tx`, and calls `sdw_stream_add_slave()`. Stream shutdown calls `wcd939x_sdw_free()`, which removes the slave from the SoundWire stream.

During SoundWire interrupt delivery, the core calls `wcd9390_interrupt_callback()`. The callback does not decode codec interrupts itself; it delegates to the common WCD helper so the regmap IRQ chip in the aggregate driver can read status, acknowledge, and fan out nested IRQs.

Runtime suspend and resume only operate on the TX regmap when present. Suspend sets cache-only mode and marks the cache dirty. Resume clears cache-only mode and synchronizes cached writes to hardware. RX-only children have no regmap in this file and therefore do no cache work.

## State and persistence behavior

Persistent in-memory state lives in `struct wcd939x_sdw_priv`, which is allocated per SoundWire child. It stores the SoundWire slave, stream configuration, current stream runtime, per-port channel masks, active port count, TX/RX direction, parent aggregate pointer, slave IRQ domain, and TX regmap. The active port masks are expected to be mutated by the aggregate codec controls before `hw_params()` consumes them.

Hardware register state is represented by the TX child regmap. The defaults table seeds regcache, readable/writeable/volatile callbacks control cacheability and access validation, and runtime PM moves the regmap between cache-only and synchronized states. Since only TX owns the regmap, aggregate drivers must respect device links and PM ordering so register accesses do not occur while TX is suspended or not enumerated.

SoundWire stream state is not persistent across stream free. `sruntime` is a borrowed pointer set by the main DAI `.set_stream` path and used by `sdw_stream_add_slave()` and `sdw_stream_remove_slave()`. `active_ports` and `sconfig` are recomputed for each `hw_params()` call from current `port_config` masks.

## Dependencies and integration points

The driver depends on Linux SoundWire core APIs (`sdw_slave`, `sdw_stream_add_slave()`, `sdw_stream_remove_slave()`, `sdw_driver`, DPN properties, SCP interrupt masks), regmap over SoundWire, runtime PM, component framework, OF properties, and ALSA SoC DAI types used by exported helpers.

Local dependencies are `wcd939x.h` for WCD939x register, enum, and private-structure definitions, and `wcd-common.h` for `WCD_SDW_CH`, common SoundWire component ops, update-status and bus-config callbacks, and interrupt forwarding. The aggregate WCD939x codec driver is expected to bind the RX/TX SoundWire components, set `slave_irq`, set parent pointers, and call the exported stream helpers from its DAIs.

External integration points are SoundWire device ID `SDW_SLAVE_ENTRY(0x0217, 0x10e, 0)`, device-tree properties `qcom,tx-port-mapping` and `qcom,rx-port-mapping`, SoundWire implementation-defined interrupts, and runtime PM. TX children advertise wake capability, while RX children only advertise sink ports.

## Risks

`wcd939x_sdw_hw_params()` initializes `wcd->sconfig.ch_count` to `1` and then increments once for each set channel bit. If SoundWire expects an exact enabled-channel count, this appears to overcount by one for every stream. That behavior should be compared with hardware expectations and related WCD drivers before changing it, because a silent off-by-one in SoundWire stream config can break channel preparation.

The TX channel table maps `WCD939X_MBHC` and `WCD939X_DMIC2` to the same port and channel mask. That may be intentional because MBHC data shares a DMIC lane, but it is a risk for controls that allow both paths to be enabled independently. Static port mapping is optional; if firmware omits it, operation depends on default SoundWire port mapping being valid for the board.

Only TX creates the regmap. Any aggregate-driver path that tries to use RX child regmap state would fail, and any PM dependency bug that lets TX suspend before register access can produce stale cache writes or I/O failures. The register access policy is large and manual; missing a volatile status register or marking a write-only register readable can cause stale status, failed cache sync, or regmap warnings.

`wcd939x_sdw_free()` unconditionally calls `sdw_stream_remove_slave()` with the stored runtime. It assumes `.set_stream` was called and `sruntime` remains valid. Error paths around failed `sdw_stream_add_slave()` should ensure later free does not remove an unadded or NULL stream.

## Test signals

Probe tests should cover TX and RX child enumeration, optional static port mapping, component bind with the aggregate codec, TX regmap creation in cache-only mode, and correct source/sink port properties visible to the SoundWire core. Stream tests should verify enabled channel masks produce the expected SoundWire port configs, active port counts, TX/RX directions, frame rates, and channel counts for mono, stereo, and four-channel capture.

Power-management tests should suspend/resume the TX child and confirm regcache dirty/sync behavior, no register I/O while cache-only is active, and stable playback/capture across runtime PM cycles. Interrupt tests should inject or observe MBHC/button/OCP/status interrupts and confirm SoundWire callbacks trigger the aggregate regmap IRQ domain. Regmap tests should read volatile status registers without stale cache effects and verify cache sync does not attempt unsupported read-only writes.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/sound/soc/codecs/wcd939x-sdw.c -->
