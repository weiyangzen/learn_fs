# sources/distributed-fs/ceph-client/drivers/regulator/qcom-labibb-regulator.c

Purpose: implements Qualcomm PMI8998 LAB/IBB display bias regulators. It controls positive LAB and negative IBB supplies, current limits, soft-start/discharge settings, pull-down/active discharge, and safety recovery for over-current and short-circuit interrupts.

Important APIs/types/functions: `struct labibb_regulator` holds the copied descriptor, regmap, base address, type, IRQs, recovery work, current-limit parameters, and fault counters. `qcom_labibb_set_current_limit()` uses secure access before programming current limits. `qcom_labibb_set_ocp()` configures VREG_OK OCP interrupts and installs `qcom_labibb_ocp_isr()`. `qcom_labibb_sc_isr()` and `qcom_labibb_sc_recovery_worker()` handle short-circuit conditions across both LAB and IBB.

Control flow: platform probe gets the parent regmap, iterates match data for `lab` and `ibb`, validates peripheral type registers, finds child DT nodes, requires `sc-err` IRQs and optionally records `ocp` IRQs, initializes delayed work, sets type-specific current-limit metadata, copies and names descriptors, registers regulators, and requests short-circuit IRQs. OCP setup is deferred until the regulator core calls the protection op.

State and persistence: fault counters and delayed work are in-memory runtime state. Current limit, voltage, pull-down, discharge, and enable settings live in PMIC registers. Recovery workers may disable or re-enable hardware after fault events.

Dependencies and integration: depends on parent Qualcomm regmap, OF child nodes and IRQ names, regulator core protection callbacks, delayed workqueues, and notifier chains. Compatible is `qcom,pmi8998-lab-ibb`.

Risks and test signals: OCP recovery can call `BUG_ON()` after repeated fatal disable failures, intentionally prioritizing hardware protection. Probe error path calls `dev_err_probe(vreg->dev, ...)` before `vreg` is allocated on missing short-circuit IRQ, which is a bug risk. Test peripheral type mismatch, IRQ handling, OCP polarity, SC/OCP recovery counters, secure writes, DT validation, and notifier events.
