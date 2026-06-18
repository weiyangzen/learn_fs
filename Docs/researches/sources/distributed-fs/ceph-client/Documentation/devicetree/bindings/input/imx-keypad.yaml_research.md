<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/imx-keypad.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/imx-keypad.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/imx-keypad.yaml` is a Linux devicetree YAML schema for a keypad binding: **Freescale i.MX Keypad Port(KPP)**. The KPP is designed to interface with a keypad matrix with 2-point contact or 3-point contact keys. The KPP is designed to simplify the software task of scanning a keypad matrix. The KPP is capable of detecting, debouncing, and decoding one or multiple... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `fsl,imx21-kpp`, `fsl,imx25-kpp`, `fsl,imx27-kpp`, `fsl,imx31-kpp`, `fsl,imx35-kpp`, `fsl,imx51-kpp`, `fsl,imx53-kpp`, `fsl,imx50-kpp`, `fsl,imx6q-kpp`, `fsl,imx6sx-kpp`, `fsl,imx6sl-kpp`, `fsl,imx6sll-kpp`, `fsl,imx6ul-kpp`, `fsl,imx7d-kpp`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `clocks`, `linux,keymap`.
- Maintainers: Liu Ying <gnuiyl@gmail.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `clocks`.
- `compatible`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `clocks`: maxItems 1.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/input/matrix-keymap.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `clocks`.
- Integrates with the matrix keymap schema, so `linux,keymap` values encode row, column, and key code information consumed by keypad drivers.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/imx-keypad.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 85-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/imx-keypad.yaml -->
