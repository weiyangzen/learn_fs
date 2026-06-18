# sources/distributed-fs/ceph-client/drivers/net/ethernet/amd/xgbe/xgbe-dcb.c

## Purpose

`xgbe-dcb.c` connects the AMD XGBE driver to Linux DCBNL for IEEE 802.1Qaz Enhanced Transmission Selection and Priority Flow Control. It validates user-provided ETS/PFC policy, stores accepted policy in `struct xgbe_prv_data`, and calls hardware-interface hooks implemented in `xgbe-dev.c` to reprogram traffic classes, queue mapping, FIFO allocation, and pause behavior.

The file is deliberately small and policy-oriented. It does not write registers directly; it translates DCBNL operations into driver state changes and delegates hardware programming to `pdata->hw_if`.

## Important APIs and Functions

- `xgbe_dcb_ieee_getets()` reports `ets_cap` from `pdata->hw_feat.tc_cnt` and returns the saved `struct ieee_ets` fields when configured.
- `xgbe_dcb_ieee_setets()` validates traffic class mappings and TSA algorithms, enforces ETS bandwidth totals, saves the requested ETS policy, updates `pdata->num_tcs`, and invokes `config_dcb_tc`.
- `xgbe_dcb_ieee_getpfc()` reports PFC class capability and returns saved PFC enable, MBC, and delay values.
- `xgbe_dcb_ieee_setpfc()` validates the PFC enable mask against supported traffic classes, saves the policy, and invokes `config_dcb_pfc`.
- `xgbe_dcb_getdcbx()` advertises host-managed IEEE DCBX.
- `xgbe_dcb_setdcbx()` rejects unsupported or incomplete DCBX modes; the driver only accepts `DCB_CAP_DCBX_HOST | DCB_CAP_DCBX_VER_IEEE`.
- `xgbe_dcbnl_ops` is the exported `struct dcbnl_rtnl_ops` table, returned by `xgbe_get_dcbnl_ops()`.

## Control Flow

ETS set begins by walking all eight IEEE priority/traffic-class slots. It logs TX/RX bandwidth and TSA values, computes the maximum requested traffic class from both priority mappings and explicit TC settings, and accepts only strict priority and ETS algorithms. If any TC uses ETS, all ETS `tc_tx_bw[]` values must sum to 100. The accepted config is copied into a devm-managed `pdata->ets` allocation, `pdata->num_tcs` is set to the highest used TC plus one, and the hardware is reconfigured.

PFC set logs the requested capability, enable mask, MBC, and delay; then it rejects bits outside the hardware TC count. Accepted data is copied into devm-managed `pdata->pfc`, after which `config_dcb_pfc` recomputes lossless FIFO thresholds and flow-control bits.

## State and Persistence Behavior

The file persists DCB policy in `pdata->ets`, `pdata->pfc`, and `pdata->num_tcs`. Allocations use `devm_kzalloc(pdata->dev, ...)`, so memory lifetime is tied to the device, not to each DCB operation. Hardware state is volatile and is re-applied through `xgbe-dev.c` paths during device initialization or when DCB setters run. No on-disk or firmware persistence is performed.

## Dependencies and Integration Points

The file depends on Linux `netdevice.h`, `net/dcbnl.h`, IEEE 802.1Qaz structures, and the xgbe private data and hardware-interface callbacks. It integrates with:

- DCBNL user interfaces such as `dcb`/`lldpad`.
- `xgbe-dev.c` functions `xgbe_config_dcb_tc()` and `xgbe_config_dcb_pfc()`.
- netdev traffic class APIs via the delegated `config_tc` path.
- PFC queue and FIFO threshold calculations used by the receive flow-control code.

## Risks and Failure Modes

- The file assumes `pdata->hw_feat.tc_cnt` is already populated correctly. Bad feature decoding can reject valid DCB policy or accept unsupported classes.
- ETS bandwidth validation sums all TC weights marked ETS; callers must set strict classes with zero or ignored bandwidth as appropriate.
- `pdata->num_tcs = max_tc + 1` means sparse TC selections still expose all classes up to the maximum.
- DCB updates can reconfigure live data-path behavior through callbacks. The delegated PFC path stops TX queues and suspends RX when needed, but race coverage depends on those lower-level paths.
- There is no semantic validation of PFC delay beyond storing the value; hardware feasibility is handled later by FIFO and threshold calculations.

## Test Signals

Test with `dcb` or equivalent DCBNL tooling: valid strict-only ETS, valid ETS weights summing to 100, invalid TSA values, over-capacity TC mappings, invalid PFC masks, and live PFC toggles under traffic. Inspect `tc -s qdisc`, netdev traffic class mappings, pause/PFC counters, and driver logs. Regression signals include failed `config_dcb_tc`, FIFO allocation warnings in `xgbe-dev.c`, dropped traffic during live PFC changes, or wrong queue selection for VLAN priorities.
