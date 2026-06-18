<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8941-pwrkey.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8941-pwrkey.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8941-pwrkey.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Qualcomm PM8941 PMIC Power Key**. The file describes the devicetree contract for the Qualcomm PM8941 PMIC Power Key. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `qcom,pm8941-pwrkey`, `qcom,pm8941-resin`, `qcom,pmk8350-pwrkey`, `qcom,pmk8350-resin`, `qcom,pmm8654au-pwrkey`, `qcom,pmm8654au-resin`.
- Required top-level fields: `compatible`, `interrupts`.
- Maintainers: Courtney Cavin <courtney.cavin@sonymobile.com>, Vinod Koul <vkoul@kernel.org>.
- Top-level properties: `compatible`, `interrupts`, `debounce`, `bias-pull-up`, `wakeup-source`, `linux,code`.
- `compatible`.
- `interrupts`: maxItems 1.
- `linux,code`: The input key-code associated with the power key. Use the linux event codes defined in include/dt-bindings/input/linux-event-codes.h. When property is omitted KEY_POWER is assumed..
- `wakeup-source`: Button can wake-up the system. Only applicable for 'resin', 'pwrkey' always wakes the system by default..
- `debounce`: ref `/schemas/types.yaml#/definitions/uint32`; Time in microseconds that key must be pressed or released for state change interrupt to trigger..
- `bias-pull-up`: ref `/schemas/types.yaml#/definitions/flag`; Presence of this property indicates that the KPDPWR_N pin should be configured for pull up..
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: if `qcom,pm8941-pwrkey`, `qcom,pmk8350-pwrkey`: require none / constrain `wakeup-source`
- Unknown-property policy is `additionalProperties: not set` and `unevaluatedProperties: False`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- No examples block is present, so validation confidence depends on external DTS users and schema-only checks.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `interrupts`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/qcom,pm8941-pwrkey.yaml`; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 72-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/qcom,pm8941-pwrkey.yaml -->
