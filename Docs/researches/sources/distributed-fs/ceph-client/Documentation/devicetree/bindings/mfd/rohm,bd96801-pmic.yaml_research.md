# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd96801-pmic.yaml

Purpose: Schema for ROHM BD96801 and BD96805 scalable automotive PMICs, modeling regulators, safety interrupts, watchdog settings, and watchdog failure action.

Important schema surface and control flow: compatible is `rohm,bd96801` or `rohm,bd96805`; `reg`, `interrupts`, `interrupt-names`, and `regulators` are required. `interrupts` may describe `intb` and optional fatal `errb`; `interrupt-names` enforces the first name as `intb` or `errb` and the second as `errb`. Watchdog properties include `rohm,hw-timeout-ms`, `rohm,wdg-action` (`prstb` or `intb-only`), and generic `timeout-sec` through an `allOf` reference to `/schemas/watchdog/watchdog.yaml`. Regulators are delegated to the BD96801 regulator schema.

State, dependencies, and integration: the DT node defines safety IRQ topology, watchdog policy, and regulator limits including safety warning/error settings in child nodes. Dependencies include watchdog and ROHM regulator schemas plus interrupt and I2C bindings. Risks include omitting `errb` on systems that need fatal event handling, reversed interrupt names, and watchdog action that unexpectedly powers down rails. Test signals are `dt_binding_check`, watchdog schema validation, interrupt-name ordering checks, and runtime regulator/watchdog/IRQ registration.
