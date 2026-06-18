# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pltfrm.c

## Purpose
`ufshcd-pltfrm.c` is the common platform-bus glue for UFS host drivers. It parses DT clocks, regulators, lane counts, OPP tables, and gear/rate limits; provides host/device power-mode negotiation defaults; maps platform MMIO/IRQ resources; allocates and initializes the generic UFS HBA; and handles platform remove.

## Important APIs, Types, And Functions
Exported APIs are `ufshcd_populate_vreg()`, `ufshcd_negotiate_pwr_params()`, `ufshcd_parse_gear_limits()`, `ufshcd_init_host_params()`, `ufshcd_pltfrm_init()`, and `ufshcd_pltfrm_remove()`. Private helpers parse clock info from `freq-table-hz`, regulator phandles/current limits for `vdd-hba`, `vcc`, `vccq`, and `vccq2`, `lanes-per-direction`, and `operating-points-v2`.

## Control Flow And State
Variant platform drivers call `ufshcd_pltfrm_init(pdev, vops)`. It maps resource 0, obtains IRQ 0, allocates an HBA, stores variant ops, parses clocks and regulators, initializes lanes per direction, parses OPP data if present, and calls `ufshcd_init()`. After successful core initialization it marks runtime PM active and enables runtime PM. Remove obtains the HBA from platform drvdata, resumes it synchronously, calls `ufshcd_remove()`, disables runtime PM, and drops the no-idle PM reference.

Clock parsing supports two mutually exclusive models. `freq-table-hz` provides per-clock min/max pairs matched to `clock-names`; `operating-points-v2` configures OPP with indexed clocks and backfills min/max frequencies from the OPP table. Host parameter initialization supplies two lanes, HS-G3, PWM-G4, FAST HS, SLOW PWM, Rate B, and HS desired mode. Negotiation chooses power mode, lanes, gear, and rate from the intersection of host policy and device maximums.

## Dependencies And Integration Points
The file depends on OF, Linux clocks, regulators through UFS core vreg structures, PM OPP, platform devices, runtime PM, UniPro constants, and the generic `ufshcd` core. It is used by Qualcomm, Renesas, Rockchip, Unisoc, and other platform UFS drivers.

## Risks And Edge Cases
`operating-points-v2` and `freq-table-hz` are explicitly incompatible. DT clock count and frequency-array length mismatches fail probe. Missing regulator phandles are treated as always-on, while present-but-invalid regulator properties fail. Negotiation returns `-ENOTSUPP` when host requires HS but the device does not support it. Optional `limit-hs-gear` and `limit-gear-rate` can silently constrain performance if DT is wrong.

## Test Signals
Test DT variants with no clocks, `freq-table-hz`, and OPP tables; malformed clock arrays; missing and present regulators; lane-count defaults; gear/rate limit properties; negotiation across HS/PWM device capabilities; runtime PM enablement after probe; and remove-time PM/HBA teardown ordering.
