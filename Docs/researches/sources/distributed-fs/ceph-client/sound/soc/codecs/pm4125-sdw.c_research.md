# sources/distributed-fs/ceph-client/sound/soc/codecs/pm4125-sdw.c

## Purpose
This is the SoundWire slave-side driver for the Qualcomm PM4125 codec. It exposes RX and TX SoundWire endpoints to the common PM4125 platform codec driver, supplies the codec register map over the TX SoundWire device, and plugs the slave interrupt callback into the shared WCD interrupt path.

## Important APIs, types, and functions
The key exported API is `pm4125_sdw_hw_params()`, which turns the selected `struct pm4125_sdw_priv` port/channel state into `struct sdw_stream_config` plus `struct sdw_port_config` and calls `sdw_stream_add_slave()`. The file defines RX/TX `wcd_sdw_ch_info` maps, two `sdw_dpn_prop` entries, a large PM4125 regmap default table, readable/writeable/volatile register predicates, `pm4125_interrupt_callback()`, `pm4125_probe()`, runtime PM callbacks, and the `sdw_driver` named `pm4125-codec`.

## Control flow and integration
Probe decides whether this slave instance is TX or RX from `qcom,tx-port-mapping` versus `qcom,rx-port-mapping`, loads optional static channel maps, fills SoundWire properties, and registers itself as a component through `wcd_sdw_component_ops`. TX devices initialize `devm_regmap_init_sdw()` and start cache-only until enumeration/resume; RX devices only provide sink port data and channel mapping. Interrupt delivery enters from SoundWire OOB status, calls `wcd_interrupt_callback()`, and triggers the codec-level IRQ domain owned by `pm4125.c`.

## State and persistence
Persistent driver state is in `struct pm4125_sdw_priv`: stream runtime, port configs, channel map, port-enable flags, TX/RX role, back pointer to `pm4125_priv`, shared IRQ domain, and TX regmap. Runtime suspend marks the regmap cache-only and dirty; resume exits cache-only and syncs. Port and channel selections are in memory and are consumed during PCM hw_params.

## Dependencies
This file depends on Linux SoundWire core, regmap, runtime PM, component framework, `wcd-common.h` helpers through `pm4125.h`, and the PM4125 register definitions. Device-tree properties are central for SoundWire port and channel mapping.

## Risks and test signals
`pm4125_sdw_hw_params()` initializes `ch_count` to 1 before counting selected channels, so stream channel count behavior should be checked against hardware expectations. `for_each_set_bit(..., 4)` only counts four mask bits although constants allow more IDs. Probe logs but continues on missing mappings, so DT mistakes can become silent audio routing failures. Test signals include TX/RX SoundWire enumeration, regcache sync after runtime PM, PCM startup with selected switches/companders, and jack/MBHC interrupts reaching the PM4125 regmap IRQ chip.
