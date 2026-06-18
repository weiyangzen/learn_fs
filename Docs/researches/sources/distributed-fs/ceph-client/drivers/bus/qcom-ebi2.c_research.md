# sources/distributed-fs/ceph-client/drivers/bus/qcom-ebi2.c

## Purpose
This driver configures Qualcomm EBI2/QPIC-era external memory bus chip-selects from device tree and then populates child devices attached to that parallel bus.

## Important APIs, Types, and Functions
`struct cs_data` maps chip-select indexes 0-5 to enable masks and slow/fast timing registers. `struct ebi2_xmem_prop` maps DT timing properties to register fields and maximum values. `qcom_ebi2_setup_chipselect()` enables a CS line, parses timing properties, caps out-of-range values, and writes slow/fast XMEMC registers. `qcom_ebi2_probe()` enables the `ebi2x` and `ebi2` clocks, maps the EBI2 and XMEM windows, disables all chip-selects, configures available children, and calls `of_platform_default_populate()`.

## Control Flow
Probe obtains and enables clocks before MMIO access. It writes `EBI2_XMEM_CFG` to disable power-save behavior, clears all CS enables, then walks each available child node. Each child must provide a `reg` chip-select index; invalid indexes are logged and skipped. If at least one child was configured, the driver populates child platform devices.

## State and Persistence
The driver keeps no private runtime state after probe. Persistent state is hardware register programming for enabled chip-selects and timing registers. Clocks are not explicitly disabled on successful remove because the driver has no remove callback in this source.

## Dependencies and Integration Points
It depends on CCF clocks, OF child nodes, platform resources, MMIO access, and DT bindings for `qcom,xmem-*` timing properties. It integrates with child memory/peripheral drivers by enabling their bus aperture before population.

## Risks and Test Signals
Risks include leaking enabled clocks for a module unload path, returning directly from missing child `reg` without disabling clocks, timing defaults of zero when properties are absent, and uncertain undocumented FAST register fields. Test signals are correct child probe, external memory read/write stability, clock enable errors on missing DT clocks, and register dumps matching expected timing values.
