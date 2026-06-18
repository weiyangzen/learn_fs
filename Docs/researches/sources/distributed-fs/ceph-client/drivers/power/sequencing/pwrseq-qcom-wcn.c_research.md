# sources/distributed-fs/ceph-client/drivers/power/sequencing/pwrseq-qcom-wcn.c

## Purpose
`pwrseq-qcom-wcn.c` is a Qualcomm WCN Bluetooth/WLAN PMU power-sequencing provider. It models chip-specific regulator sets, optional VDDIO, reference clock, enable GPIOs, XO clock GPIO sequencing, inter-GPIO delays, and named `bluetooth` and `wlan` targets for consumers.

## Important APIs, Types, and Functions
Important data types are `struct pwrseq_qcom_wcn_pdata` for per-compatible regulator/delay/target/match data and `struct pwrseq_qcom_wcn_ctx` for runtime handles. Unit callbacks enable VDDIO, regulator bulks, clocks, BT/WLAN GPIOs, and WCN6855 XO assert/deassert sequencing. Match helpers associate consumers by regulator phandles such as `vddaon-supply`, `vddio-supply`, or `vdd-1.8-xo-supply`.

## Control Flow
Probe selects compatible data for WCN3950/3988/3990/3991/3998, QCA6390, WCN6750, WCN6855, or WCN7850; allocates regulator bulk data; gets regulators, optional VDDIO, BT/WLAN/XO GPIOs, and optional clock; preserves existing WLAN GPIO value while forcing output; then registers the pwrseq provider. Power-on follows dependency order: regulators and clock first, optional XO assertion, target GPIO enable with required spacing, then post-enable delay or XO deassert delay.

## State and Persistence Behavior
Persistent state includes regulator/clock/GPIO handles, `last_gpio_enable_jf` for spacing BT/WLAN enables, pwrseq core enable counts, and physical rail/GPIO/clock states while targets are on.

## Dependencies and Integration Points
It depends on OF platform matching, regulator bulk APIs, optional clocks, GPIO descriptors, jiffies/delay helpers, and the pwrseq provider framework. Consumer matching depends on DT supply phandles pointing back to this PMU node.

## Risks and Edge Cases
The WLAN GPIO uses `GPIOD_ASIS` to avoid dropping an already enumerated PCIe link, a deliberate workaround until controller link-down handling improves. Regulator phandle matching is topology-sensitive and can fail on unusual regulator node layouts. Delay values are chip data, so incorrect compatibles can violate hardware timing. Shared BT/WLAN targets require careful enable-count behavior in the core.

## Test Signals
Test every compatible's regulator names, optional VDDIO and clock handling, BT and WLAN target power-on/off independently and together, GPIO delay enforcement, WCN6855 XO timing, WLAN-as-is preservation, phandle matching failures, and provider removal while consumers defer or hold descriptors.
