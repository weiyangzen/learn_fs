# sources/distributed-fs/ceph-client/drivers/spmi/spmi-pmic-arb.c

## Purpose
Qualcomm PMIC Arbiter platform driver implementing an SPMI controller plus a PMIC interrupt controller. It registers one or more `spmi_controller` instances, translates SPMI command APIs into PMIC Arbiter register transactions, maps PPID/APID ownership tables for arbiter hardware versions v1/v2/v3/v5/v7/v8, and exposes QPNP peripheral IRQs through an irqdomain.

## Important APIs, Types, and Functions
Key state is `struct spmi_pmic_arb` for shared hardware resources/version ops and `struct spmi_pmic_arb_bus` for each SPMI bus instance, including `spmic`, IRQ domain, `ppid_to_apid`, `apid_data`, APID bounds, and MMIO bases. `struct pmic_arb_ver_ops` abstracts version-specific resource mapping, APID init, PPID lookup, command formatting, offset calculation, and interrupt register addressing. SPMI entry points are `pmic_arb_cmd`, `pmic_arb_read_cmd`, `pmic_arb_write_cmd`; interrupt chip callbacks are `qpnpint_irq_ack`, mask/unmask/type/wake/get-state plus domain translate/alloc/activate. Probe/remove are `spmi_pmic_arb_probe` and `spmi_pmic_arb_remove`.

## Control Flow
Probe maps the `core` resource, reads `PMIC_ARB_VERSION`, selects a `pmic_arb_v*` ops table, maps observer/channel/core resources, reads DT `qcom,channel` and `qcom,ee`, then registers legacy or child `spmi` bus nodes. Bus init allocates a controller, maps `cnfg`/`intr` and optional v8 `chnl_owner`, builds APID state, creates an irqdomain, installs a chained IRQ handler, and adds the SPMI controller. Data transfers format opcode/address/count, compute version-specific channel offset from SID/address/APID, serialize with `raw_spin_lock_irqsave`, write/read data FIFOs, issue command, and poll `PMIC_ARB_STATUS_DONE`. IRQ flow enters `pmic_arb_chained_irq`, scans owner access status over APID ranges, dispatches each status bit to mapped virqs, and falls back to per-APID IRQ status if owner status was empty.

## State and Persistence
Runtime state is memory-resident and device-managed: APID/PPID caches, mapping validity bitmap, APID owner data, min/max APID bounds learned during IRQ translation, and bus count. Hardware state persists in PMIC Arbiter register windows and PMIC interrupt registers; the driver clears latched/enable registers during IRQ activation and ack. Remove unregisters chained handlers and irqdomains; devm resources handle mappings/allocations.

## Dependencies and Integration Points
Depends on Linux SPMI core, platform/OF resource parsing, irqdomain/chained IRQ framework, MMIO accessors, and DT bindings that provide `core`, `obsrvr`, `chnls`, `cnfg`, `intr`, optional `chnl_map`/`chnl_owner`, `periph_irq`, `qcom,channel`, and `qcom,ee`. It is consumed by SPMI client drivers through exported SPMI APIs and by OF interrupt consumers using four-cell PMIC IRQ specs.

## Risks
Version-specific offsets and APID ownership rules are the main risk; a wrong ops table, APID count, or v8 owner base can route writes/IRQs to the wrong EE. `spmi_pmic_arb_register_buses` returns `ret` after the child loop without initializing it if no child matches, so DT shape matters. IRQ min/max bounds are only tightened as interrupts are translated, so unmapped APID IRQs rely on fallback cleanup. Polling timeouts, permission failures, and duplicate PPID ownership can surface as `-ETIMEDOUT`, `-EPERM`, or missing interrupts.

## Test Signals
Useful signals are successful probe log with arbiter version, SPMI child device enumeration, working reads/writes up to 8 bytes, rejection of unsupported non-data commands on v2+, correct IRQ domain translation from DT, interrupt ack/mask/unmask behavior, suspend wake propagation to parent IRQ, and no timeout/denied/dropped messages under PMIC traffic.
