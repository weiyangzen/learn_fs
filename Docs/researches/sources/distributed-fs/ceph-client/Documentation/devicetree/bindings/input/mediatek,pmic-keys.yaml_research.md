<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,pmic-keys.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,pmic-keys.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,pmic-keys.yaml` is a Linux devicetree YAML schema for a key/button input binding: **MediaTek PMIC Keys**. There are two key functions provided by MT6397, MT6323 and other MediaTek PMICs: pwrkey and homekey. The key functions are defined as the subnode of the function node provided by the PMIC that is defined as a Multi-Function Device (MFD). For MediaTek... It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `mediatek,mt6323-keys`, `mediatek,mt6328-keys`, `mediatek,mt6331-keys`, `mediatek,mt6357-keys`, `mediatek,mt6358-keys`, `mediatek,mt6359-keys`, `mediatek,mt6397-keys`.
- Required top-level fields: `compatible`.
- Maintainers: Chen Zhong <chen.zhong@mediatek.com>.
- Top-level properties: `compatible`, `power-off-time-sec`, `mediatek,long-press-mode`.
- `compatible`: enum `mediatek,mt6323-keys`, `mediatek,mt6328-keys`, `mediatek,mt6331-keys`, `mediatek,mt6357-keys`, `mediatek,mt6358-keys`, and 2 more.
- `power-off-time-sec`.
- `mediatek,long-press-mode`: ref `/schemas/types.yaml#/definitions/uint32`; Key long-press force shutdown setting 0 - disabled 1 - pwrkey 2 - pwrkey+homekey.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/uint32`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^((power|home)|(key-[a-z0-9-]+|[a-z0-9-]+-key))$` child nodes with required `linux,keycodes` and properties `interrupts`, `interrupt-names`, `linux,keycodes`, `wakeup-source`
- Conditional validation: if `powerkey`: require none / constrain `interrupt-names`
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: none.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/mediatek,pmic-keys.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 95-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/mediatek,pmic-keys.yaml -->
