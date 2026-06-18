<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmhpd.c -->
# sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmhpd.c

## Purpose
Qualcomm RPMh power-domain driver. It maps DT power-domain specifier indices to RPMh ARC resources, exposes them as generic PM domains, aggregates normal and active-only peer votes, and sends active/wake/sleep corner votes through RPMh.

## Important APIs, Types, And Functions
- `struct rpmhpd` is one RPMh domain: genpd, optional parent, optional active-only peer, current requested corner, current active vote, enable corner, command DB level mapping, resource name/address, enable flag, sync-state flag, and retention-skip flag.
- `struct rpmhpd_desc` maps a compatible string to an indexed array of `struct rpmhpd *` domains.
- Core functions are `rpmhpd_probe()`, `rpmhpd_update_level_mapping()`, `rpmhpd_power_on()`, `rpmhpd_power_off()`, `rpmhpd_set_performance_state()`, `rpmhpd_aggregate_corner()`, and `rpmhpd_sync_state()`.
- Static descriptor arrays cover many Qualcomm SoCs such as SDM845, SC7180, SM8xxx, X1E80100, and related automotive/platform parts.

## Control Flow
At `core_initcall`, the platform driver binds to a compatible in `rpmhpd_match_table`. `rpmhpd_probe()` allocates onecell data, looks up each resource address with `cmd_db_read_addr()`, verifies `CMD_DB_HW_ARC`, reads the auxiliary level map from command DB, initializes each genpd with power and performance callbacks, and wires parent/child subdomains. `rpmhpd_set_performance_state()` maps the requested abstract level to the first command-DB level not less than the request, clamps over-max requests to the last supported corner, and if the domain is enabled aggregates and sends the new vote. `rpmhpd_power_on()` votes at least `enable_corner`; `rpmhpd_power_off()` votes zero. `rpmhpd_aggregate_corner()` combines this domain and an active-only peer, sending `RPMH_ACTIVE_ONLY_STATE`, `RPMH_WAKE_ONLY_STATE`, and `RPMH_SLEEP_STATE` as needed. Before `sync_state`, it clamps votes to the highest corner to avoid prematurely reducing bootloader-required resources; `rpmhpd_sync_state()` later marks resources synced and resends real enabled/disabled votes.

## State And Persistence Behavior
Runtime state is per static `rpmhpd` object: requested `corner`, active aggregate vote, `enabled`, `enable_corner`, `level[]`, `level_count`, and `state_synced`. The static domain objects are reused according to compatible descriptors, so this driver assumes one matching controller instance for these global descriptors. RPMh itself persists/applies votes across active, wake, and sleep states.

## Dependencies And Integration Points
Depends on `soc/qcom/cmd-db` for ARC address and level mapping, `soc/qcom/rpmh` for synchronous/asynchronous TCS writes, generic PM domains, OPP/genpd performance states, and dt-bindings indices from `qcom-rpmpd.h` and `qcom,rpmhpd.h`. Integration with consumers is through `of_genpd_add_provider_onecell()` and required-opps or power-domain references.

## Risks
Command DB data quality is critical: missing addresses, wrong slave IDs, zero-padded level arrays, or level counts over `RPMH_ARC_MAX_LEVELS` fail probe. Active-only peer aggregation is subtle: normal and AO peers share active votes but only non-AO domains contribute sleep votes. Pre-sync max-corner clamping trades power for safety; broken `sync_state` ordering can leave resources over-voted. Static global domain objects can be unsafe for multiple controller instances.

## Test Signals
Probe should show no missing RPMh resource errors, command DB level maps should be non-empty, and genpd consumers should observe performance-state votes reflected in RPMh traces. Suspend/resume tests should verify wake/sleep votes for AO peers, and `sync_state` should reduce boot-time max votes only after consumers are bound.

<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pmdomain/qcom/rpmhpd.c -->
