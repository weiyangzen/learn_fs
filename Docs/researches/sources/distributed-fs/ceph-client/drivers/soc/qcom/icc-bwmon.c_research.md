# sources/distributed-fs/ceph-client/drivers/soc/qcom/icc-bwmon.c

## Purpose
Qualcomm interconnect bandwidth monitor driver. It programs BWMON hardware thresholds, handles bandwidth zone interrupts, and adjusts PM OPP bandwidth votes to match measured interconnect demand.

## Important APIs, Types, And Functions
Private types are `struct icc_bwmon_data` and `struct icc_bwmon`. Register abstractions are `enum bwmon_fields`, SoC-specific `reg_field` arrays, and regmap configs for BWMON v4/v5/global register layouts. Runtime functions include `bwmon_clear_counters()`, `bwmon_clear_irq()`, `bwmon_disable()`, `bwmon_enable()`, `bwmon_set_threshold()`, `bwmon_start()`, `bwmon_intr()`, `bwmon_intr_thread()`, `bwmon_init_regmap()`, `bwmon_probe()`, and `bwmon_remove()`.

## Control Flow
Probe allocates state, maps monitor registers and optional global registers, bulk-allocates regmap fields, gets the IRQ, loads the OPP table, discovers min/max peak bandwidth OPPs, disables the monitor, requests a shared threaded IRQ, stores drvdata, and starts monitoring.

`bwmon_start()` clears counters, writes the sample window, initializes high/medium thresholds to the minimum bandwidth OPP, programs threshold counts and zone actions, clears interrupts, and enables zone 1 and zone 3 interrupts. The hard IRQ reads status, ignores unrelated interrupts, disables the monitor, reads the relevant zone max counter, converts it to `target_kbps`, and wakes the threaded handler. The thread finds the nearest OPP, computes up/down thresholds around it, clears counters/IRQs, reenables appropriate interrupts, traces the update, and calls `dev_pm_opp_set_opp()` when target bandwidth changes.

Remove disables the monitor and frees the IRQ.

## State And Persistence
Per-device state stores current/target/min/max bandwidth, IRQ, register fields, and SoC data. Hardware state consists of BWMON counters, thresholds, zone actions, IRQ masks, and enable state. No persistent storage.

## Dependencies And Integration Points
Depends on platform bus, MMIO regmap, regmap fields, PM OPP bandwidth APIs, IRQ threading, tracepoint `trace_icc-bwmon.h`, and device-tree compatibles such as `qcom,msm8998-bwmon`, `qcom,sdm845-bwmon`, `qcom,sdm845-llcc-bwmon`, and `qcom,sc7280-llcc-bwmon`.

## Risks
Register ordering is delicate; comments call out required clear ordering across regions. Some SoCs need force-clearing of clear registers. Spurious zone 2 interrupts are ignored, which can miss useful max values. Regmap locking is disabled because the driver expects no concurrent access beyond its IRQ flow. OPP tables must contain bandwidth entries; otherwise probe fails.

## Test Signals
Probe should find min/max bandwidth OPPs and request the IRQ. Trace events should show measured/up/down bandwidth transitions. OPP votes should change under memory traffic and settle to min/max bounds. Shared IRQ testing should verify unrelated status returns `IRQ_NONE`.
