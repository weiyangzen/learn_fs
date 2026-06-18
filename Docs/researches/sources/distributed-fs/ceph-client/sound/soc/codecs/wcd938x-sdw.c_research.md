# sources/distributed-fs/ceph-client/sound/soc/codecs/wcd938x-sdw.c

## Purpose
`wcd938x-sdw.c` is the SoundWire slave driver for WCD9380/WCD938x codecs. It performs the same bus-facing role as the WCD937x SoundWire file but for a wider codec: it defines TX/RX channel maps, port capabilities, stream setup/free/set-stream helpers exported to the platform codec, the large CSR regmap defaults/access policy, SoundWire interrupt forwarding, component registration, and runtime PM cache handling.

## Important APIs, Types, and Functions
- `wcd938x_sdw_rx_ch_info` covers HPH, CLSH, compander, line-out, and DSD playback channels.
- `wcd938x_sdw_tx_ch_info` covers four analog ADC channels, MBHC, and DMIC0-DMIC7 capture channels over the TX SoundWire ports.
- `wcd938x_sdw_hw_params()` compacts active port masks into `sdw_port_config` and calls `sdw_stream_add_slave()`.
- `wcd938x_sdw_free()` and `wcd938x_sdw_set_sdw_stream()` are exported helpers used by the matching platform codec driver.
- `wcd9380_interrupt_callback()` forwards SoundWire out-of-band interrupts to `wcd_interrupt_callback()` using the three WCD938x interrupt status registers.
- `wcd938x_defaults`, `wcd938x_rdwr_register()`, `wcd938x_readonly_register()`, `wcd938x_readable_register()`, `wcd938x_writeable_register()`, and `wcd938x_volatile_register()` define the CSR regmap cache model and hardware access rules.
- `wcd9380_probe()` initializes TX/RX SoundWire roles, reads static port mapping, creates the TX regmap, and registers the slave component.

## Control Flow
Probe allocates `struct wcd938x_sdw_priv`, checks for a TX port-mapping property, reads TX or RX static port mapping into the SoundWire master's port map, records `sdev`, sets bus properties such as SCP interrupt mask, lane control, and simple clock-stop support, then configures source or sink port capabilities. TX instances create the CSR regmap and start it in cache-only mode; RX instances only expose sink ports. Both register with the common WCD SoundWire component ops and are marked runtime-suspended until the aggregate codec binds them.

Stream control is exported: the platform DAI stores `sruntime`, calls `wcd938x_sdw_hw_params()` to add active ports to the stream, and calls `wcd938x_sdw_free()` to remove the slave. Interrupts are delivered through `sdw_slave_ops`, and the WCD938x driver also supplies `bus_config = wcd_bus_config`, unlike the WCD937x SoundWire driver.

## State and Persistence Behavior
State lives in the matching `wcd938x_sdw_priv` structure from `wcd938x.h`: role, stream runtime/configuration, selected port masks, channel maps, regmap, and IRQ domain pointer. Register state is cached with REGCACHE_MAPLE. Runtime suspend switches to cache-only and marks the cache dirty; runtime resume syncs cached writes and marks the device last busy.

## Dependencies and Integration Points
The driver depends on SoundWire core, regmap, runtime PM, component framework, ASoC, and shared Qualcomm helpers in `wcd-common.h` plus register/channel definitions from `wcd938x.h`. It integrates with the WCD938x platform codec driver through exported SoundWire helpers and `wcd_sdw_component_ops`. Device tree must provide appropriate static SoundWire port mappings for TX/RX board wiring.

## Risks and Edge Cases
- Like WCD937x, `sconfig.ch_count` starts at `1` before counting active channel bits, so stream setup should be validated against the SoundWire controller's expected channel count.
- Probe continues after missing static port mappings, which can defer board-data errors into stream startup or channel-map mismatches.
- Only TX owns the CSR regmap; aggregate binding must link and resume the TX device before any register access.
- `wcd938x_volatile_register()` treats all readonly registers as volatile, which is conservative but can reduce cache effectiveness for efuse/status reads.
- `wcd938x_sdw_free()` ignores the return value from `sdw_stream_remove_slave()`, so teardown errors are not surfaced to the DAI caller.

## Test Signals
Useful checks include TX/RX SoundWire enumeration, component binding with the platform codec, regmap cache sync after resume, DAI `set_stream`/`hw_params`/`hw_free` playback and capture cycles, all ADC/DMIC/HPH/DSD channel controls producing expected master channel maps, interrupt delivery through the shared IRQ domain, bus configuration callbacks on controller setup, and runtime PM autosuspend/resume while streams are closed and reopened.
