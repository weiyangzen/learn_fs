# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/rohm,bd9576-pmic.yaml

Purpose: Binding for ROHM BD9576MUF and BD9573MUF PMICs, focused on R-Car style regulator sequencing, watchdog GPIOs, DDR voltage selection, and VOUT1 external enable wiring.

Important schema surface and control flow: `compatible` is `rohm,bd9576` or `rohm,bd9573`; `reg` and `regulators` are required while `interrupts` is optional. Board-specific controls include `rohm,vout1-en-low`, `rohm,vout1-en-gpios`, `rohm,ddr-sel-low`, watchdog enable and ping GPIOs, and `rohm,hw-timeout-ms` with one or two values for normal or windowed watchdog mode. Regulators are delegated to `/schemas/regulator/rohm,bd9576-regulator.yaml`.

State, dependencies, and integration: DT configures watchdog control wiring, startup strap interpretation, DDR voltage selection, and regulator child setup used by MFD, regulator, and watchdog-related logic. Dependencies include GPIO and regulator schemas and ROHM PMIC drivers. Risks include describing a VOUT1 GPIO when the startup strap does not enable pin control, unsafe watchdog timeout windows, and incorrect DDR strap assumptions. Test signals are schema validation, referenced regulator schema validation, GPIO phandle resolution, and hardware watchdog/regulator behavior during boot and watchdog ping tests.
