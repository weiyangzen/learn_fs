# sources/distributed-fs/ceph-client/drivers/ssb/driver_chipcommon_pmu.c

## Purpose
Power Management Unit support for ChipCommon: programs PLLs, resource masks/dependencies, LDO voltages, PA reference LDO, ALP/CPU/control clocks, and spur-avoidance PLL updates for selected Broadcom chips.

## Important APIs, Types, and Functions
Core entry is `ssb_pmu_init`; exports `ssb_pmu_set_ldo_voltage`, `ssb_pmu_set_ldo_paref`, `ssb_pmu_get_alp_clock`, `ssb_pmu_get_cpu_clock`, `ssb_pmu_get_controlclock`, and `ssb_pmu_spuravoid_pllupdate`. Internal tables describe PMU0/PMU1 crystal PLL settings and per-chip resource up/down/dependency changes.

## Control Flow
`ssb_pmu_init` checks PMU capability, reads PMU revision, sets `NOILPONW` according to revision, then calls PLL and resource init. PLL init optionally reads `xtalfreq` from BCM47xx NVRAM for SoC buses, selects a per-chip PLL routine, powers PLL resources down, waits for HT to clear, writes PLL control registers, and writes crystal/divider fields. Resource init selects min/max masks and table updates by chip ID, writes resource rows, applies dependencies, and sets min/max masks. LDO and spur functions write register-control or PLL-control fields for supported chips.

## State and Persistence
Stores `cc->pmu.rev` and `cc->pmu.crystalfreq`; most effects persist in PMU PLL, resource, and regulator registers until reset or later reprogramming.

## Dependencies and Integration Points
Called by ChipCommon init and used by ChipCommon clock/watchdog logic. Depends on ChipCommon register accessors, delays, Broadcom NVRAM on BCM47xx, and chip ID/revision definitions.

## Risks
Unsupported chip IDs mostly log errors and keep defaults, which may be acceptable or may leave clocks/resources wrong. PLL programming has hardware sequencing delays and can fail if HT does not drop. `BUG_ON` in clock-table lookups assumes register values map to known tables. LDO/spur functions silently no-op for unsupported chips.

## Test Signals
On supported chips, logs should show PMU revision and PLL programming only when needed. Validate ALP/control/CPU clock values, resource masks, wireless stability after spur-avoidance changes, and no HT-off timeout emergency messages.
