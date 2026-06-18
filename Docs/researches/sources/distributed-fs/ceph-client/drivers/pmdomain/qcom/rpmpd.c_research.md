<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmpd.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmpd.c

## Purpose
Qualcomm legacy SMD RPM power-domain driver. It exposes RPM regulator/corner resources as generic PM domains, sends enable and corner/floor votes over SMD RPM, and supports many pre-RPMh Qualcomm SoCs.

## Important APIs, Types, And Functions
- `struct rpmpd` describes one SMD RPM-backed domain with genpd, parent, active-only peer, requested corner, enabled state, RPM resource type/id, maximum state, key (`KEY_CORNER`, `KEY_LEVEL`, `KEY_FLOOR_CORNER`, or `KEY_FLOOR_LEVEL`), and sync-state flag.
- `struct rpmpd_req` is the little-endian SMD RPM request payload.
- Core functions are `rpmpd_probe()`, `rpmpd_send_enable()`, `rpmpd_send_corner()`, `rpmpd_aggregate_corner()`, `rpmpd_power_on()`, `rpmpd_power_off()`, `rpmpd_set_performance()`, and `rpmpd_sync_state()`.
- Descriptor tables map compatible strings for MDM/MSM/SDM/QCS/QCM/SM parts to indexed domain arrays.

## Control Flow
`rpmpd_probe()` obtains the parent `qcom_smd_rpm` handle, selects the SoC descriptor, allocates onecell data, initializes each domain with genpd callbacks and `GENPD_FLAG_ACTIVE_WAKEUP`, assigns the descriptor max state, wires optional subdomains, and registers a onecell provider. Power-on sends an explicit `KEY_ENABLE` active-state request, marks the domain enabled, and sends the current corner if any. Power-off sends disable and clears `enabled`. Performance changes clamp the requested state to `max_state`, update `pd->corner`, and either defer aggregation for disabled normal domains or immediately send for enabled/floor-vote domains. Aggregation combines normal and AO peer active/sleep votes and sends active and sleep SMD RPM messages. Before genpd `sync_state`, unsynced domains vote their max state to avoid dropping boot constraints.

## State And Persistence Behavior
State is kept in static `rpmpd` descriptors: requested corner, enabled flag, max state, and sync-state flag. RPM maintains applied active/sleep votes outside the driver. Floor-corner/floor-level domains are special because performance updates are sent even while the genpd is not enabled.

## Dependencies And Integration Points
Depends on `linux/soc/qcom/smd-rpm.h`, a parent SMD RPM device, genpd onecell providers, and Qualcomm power dt-bindings. The compatible determines which resource type/id/key tuple is exposed to DT consumers.

## Risks
The comparison in `rpmpd_set_performance()` checks `pd->key` against `cpu_to_le32(KEY_FLOOR_*)` even though `pd->key` is assigned host-order constants; on little-endian this is harmless but it documents an endian-sensitive assumption. Peer aggregation and pre-sync max-state clamping must match legacy RPM firmware expectations. Missing array entries are warned but provider indices remain sparse, so DT bindings must align exactly.

## Test Signals
Probe should retrieve a valid parent RPM handle and register the onecell provider. Runtime tests should watch SMD RPM messages for `swen`, `corn`, `vfc`, `vfl`, or `vlvl` keys on power/performance changes. Suspend tests should verify sleep-state votes and `sync_state` de-clamping after all consumers bind.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmpd.c -->
