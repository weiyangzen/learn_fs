# sources/distributed-fs/ceph-client/drivers/ufs/host/ufshcd-pltfrm.h

## Purpose
`ufshcd-pltfrm.h` declares the shared platform-bus UFS glue API and the `struct ufs_host_params` policy structure used by platform variants to negotiate link power mode, gear, lanes, and HS rate.

## Important APIs, Types, And Macros
The header defines `UFS_PWM_MODE`, `UFS_HS_MODE`, and `struct ufs_host_params`, which records preferred PWM/HS RX/TX gear, lane counts, PWM/HS power modes, HS rate, and desired working mode. It declares `ufshcd_negotiate_pwr_params()`, `ufshcd_init_host_params()`, `ufshcd_parse_gear_limits()`, `ufshcd_pltfrm_init()`, `ufshcd_pltfrm_remove()`, and `ufshcd_populate_vreg()`.

## Control Flow And State
The header contains no executable flow. Platform drivers allocate or embed `struct ufs_host_params`, initialize it through `ufshcd_init_host_params()`, optionally apply DT limits, and pass it into negotiation during power-mode changes. Probe/remove helpers are called directly by platform bus drivers.

## Dependencies And Integration Points
It includes `<ufs/ufshcd.h>` for HBA, variant ops, vreg, and power attribute types. It is the interface boundary between generic platform parsing in `ufshcd-pltfrm.c` and SoC-specific UFS drivers such as QCOM, Renesas, Rockchip, and Sprd.

## Risks And Edge Cases
The structure assumes symmetric policy is usually desired but exposes separate RX/TX fields; variant drivers must keep them coherent if hardware only supports symmetric operation. Wrong desired mode or gear limits can make negotiation fail or force a lower-performing link.

## Test Signals
Compile all platform variants against the declarations. Runtime tests should exercise default host-parameter initialization, DT gear/rate limit parsing, and power-mode negotiation callbacks in each platform driver.
