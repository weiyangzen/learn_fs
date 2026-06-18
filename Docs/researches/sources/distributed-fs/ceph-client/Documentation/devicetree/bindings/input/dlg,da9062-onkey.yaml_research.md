<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da9062-onkey.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da9062-onkey.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da9062-onkey.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Dialog DA9061/62/63 OnKey Module**. This module is part of the DA9061/DA9062/DA9063. For more details about entire DA906{1,2,3} chips see Documentation/devicetree/bindings/mfd/dlg,da9063.yaml This module provides the KEY_POWER event. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `dlg,da9062-onkey`, `dlg,da9063-onkey`, `dlg,da9061-onkey`.
- Required top-level fields: `compatible`.
- Maintainers: Biju Das <biju.das.jz@bp.renesas.com>.
- Top-level properties: `compatible`, `dlg,disable-key-power`.
- `compatible`.
- `dlg,disable-key-power`: type `boolean`; Disable power-down using a long key-press. If this entry exists the OnKey driver will remove support for the KEY_POWER key press when triggered using a long press of the OnKey..
- The schema is self-contained and does not use `$ref` to import another binding schema.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/dlg,da9062-onkey.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 38-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da9062-onkey.yaml -->
