# sources/distributed-fs/ceph-client/drivers/interconnect/qcom/osm-l3.c

## Purpose

`osm-l3.c` is a Qualcomm L3 interconnect provider for OSM and EPSS CPU/L3 clock-performance hardware. Unlike the NoC topology files in this group, it implements provider logic directly. It exposes a simple two-node interconnect path from an apps master to an L3 slave and translates requested peak bandwidth into a hardware performance-state index selected from a frequency LUT.

## Important APIs, Types, And Data

The file includes bitfield, clock, interconnect-provider, IO, OF, and platform headers plus `dt-bindings/interconnect/qcom,osm-l3.h`.

Important constants define LUT size and fields, OSM register offsets, EPSS register offsets, and a hardware clock divider. Important types are `qcom_osm_l3_icc_provider` for runtime state, `qcom_osm_l3_node` for node metadata, and `qcom_osm_l3_desc` for match-data variants. `DEFINE_QNODE` builds OSM nodes with bus width 16 and EPSS nodes with bus width 32. Descriptors are `osm_l3`, `epss_l3_perf_state`, and `epss_l3_l3_vote`.

## Control Flow

`qcom_osm_l3_probe()` reads `xo` and `alternate` clock rates, maps the MMIO resource, checks `REG_ENABLE`, reads match data, scans the hardware frequency LUT, creates onecell provider data, initializes an `icc_provider`, creates dynamic nodes, links master to slave, registers the provider, and stores driver data.

`qcom_osm_l3_set()` converts destination peak bandwidth to bytes per second, divides by source bus width, finds the first LUT entry at or above the requested rate, and writes that index to the configured performance-state register. `qcom_osm_l3_remove()` deregisters the provider and removes nodes.

## State And Persistence

Runtime state is per-platform-device and stored in `qcom_osm_l3_icc_provider`. The LUT is read from hardware at probe and retained in memory. The current hardware vote is not mirrored in a separate field; it is the last index written to the performance-state or L3-vote register. There is no persistence across reboot or driver unload.

## Dependencies And Integration Points

The driver integrates directly with the Linux interconnect framework, OF onecell translation, platform resources, MMIO, and named clocks `xo` and `alternate`. Supported compatibles include OSM and EPSS variants for multiple Qualcomm SoCs. Interconnect consumers request the L3 path using IDs from `qcom,osm-l3.h`.

## Risks And Edge Cases

The LUT scan assumes duplicate consecutive frequencies mean end-of-table; malformed hardware tables could stop early or expose no valid state. The source-node bus width is critical because requested bandwidth is divided by it before LUT comparison. The probe hard-fails if `REG_ENABLE` is not set. The link creation uses OSM binding indices even for EPSS arrays, so it depends on OSM and EPSS binding values being intentionally aligned.

## Test Signals

Runtime signals include successful probe with both clocks present, `REG_ENABLE` set, debug logs showing sensible LUT frequencies, and interconnect debugfs showing a two-node provider. Functional validation should request increasing peak bandwidths and confirm the written performance-state index increases and saturates at the last LUT entry. Remove/unbind should deregister the provider without leaked nodes.
