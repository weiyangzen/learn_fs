<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/azoteq,iqs7211.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/azoteq,iqs7211.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/azoteq,iqs7211.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Azoteq IQS7210A/7211A/E Trackpad/Touchscreen Controller**. The Azoteq IQS7210A, IQS7211A and IQS7211E trackpad and touchscreen control- lers employ projected-capacitance sensing and can track two contacts. Link to datasheets: https://www.azoteq.com/ It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `azoteq,iqs7210a`, `azoteq,iqs7211a`, `azoteq,iqs7211e`.
- Required top-level fields: `compatible`, `reg`, `irq-gpios`.
- Maintainers: Jeff LaBundy <jeff@labundy.com>.
- Top-level properties: `compatible`, `reg`, `irq-gpios`, `reset-gpios`, `azoteq,forced-comms`, `azoteq,forced-comms-default`, `azoteq,rate-active-ms`, `azoteq,rate-touch-ms`, `azoteq,rate-idle-ms`, `azoteq,rate-lp1-ms`, `azoteq,rate-lp2-ms`, `azoteq,timeout-active-ms`, `azoteq,timeout-touch-ms`, `azoteq,timeout-idle-ms`, `azoteq,timeout-lp1-ms`, `azoteq,timeout-lp2-ms`, `azoteq,timeout-ati-ms`, `azoteq,timeout-comms-ms`, `azoteq,timeout-press-ms`, `azoteq,fosc-freq`, `azoteq,fosc-trim`, `azoteq,num-contacts`, `azoteq,contact-split`, `azoteq,trim-x`, `azoteq,trim-y`, `trackpad`, `alp`, `button`, and 6 more.
- `compatible`: enum `azoteq,iqs7210a`, `azoteq,iqs7211a`, `azoteq,iqs7211e`.
- `reg`: maxItems 1.
- `irq-gpios`: maxItems 1; Specifies the GPIO connected to the device's active-low RDY output. The pin doubles as the IQS7211E's active-low MCLR input, in which case this GPIO must be configured as open-drain..
- `reset-gpios`: maxItems 1; Specifies the GPIO connected to the device's active-low MCLR input. The device is temporarily held in hardware reset prior to initialization if this property is present..
- `wakeup-source`.
- `touchscreen-size-x`.
- `touchscreen-size-y`.
- `azoteq,forced-comms`: type `boolean`; Enables forced communication; to be used with host adapters that cannot tolerate clock stretching..
- `azoteq,forced-comms-default`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`; Indicates if the device's OTP memory enables (1) or disables (0) forced communication by default. Specifying this property can expedite startup time if the default value is known. If this property is not specified, communication is not initiated until the....
- `azoteq,rate-active-ms`: Specifies the report rate (in ms) during active mode..
- `azoteq,rate-touch-ms`: Specifies the report rate (in ms) during idle-touch mode..
- `azoteq,rate-idle-ms`: Specifies the report rate (in ms) during idle mode..
- `azoteq,rate-lp1-ms`: Specifies the report rate (in ms) during low-power mode 1..
- `azoteq,rate-lp2-ms`: Specifies the report rate (in ms) during low-power mode 2..
- `azoteq,timeout-active-ms`: Specifies the length of time (in ms) to wait for an event before moving from active mode to idle or idle-touch modes..
- `azoteq,timeout-touch-ms`: Specifies the length of time (in ms) to wait for an event before moving from idle-touch mode to idle mode..
- `azoteq,timeout-idle-ms`: Specifies the length of time (in ms) to wait for an event before moving from idle mode to low-power mode 1..
- `azoteq,timeout-lp1-ms`: Specifies the length of time (in ms) to wait for an event before moving from low-power mode 1 to low-power mode 2..
- additional schema properties: `azoteq,timeout-lp2-ms`, `azoteq,timeout-ati-ms`, `azoteq,timeout-comms-ms`, `azoteq,timeout-press-ms`, `azoteq,fosc-freq`, `azoteq,fosc-trim`, `azoteq,num-contacts`, `azoteq,contact-split`, `azoteq,trim-x`, `azoteq,trim-y`, `trackpad`, `alp`, `button`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `../input.yaml#`, `touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `trackpad` object node with required none and properties `azoteq,rx-enable`, `azoteq,tx-enable`, `azoteq,channel-select`, `azoteq,ati-frac-div-fine`, `azoteq,ati-frac-mult-coarse`, `azoteq,ati-frac-div-coarse`, `azoteq,ati-comp-div`, `azoteq,ati-target`, `azoteq,touch-enter`, `azoteq,touch-exit`, `azoteq,thresh`, `azoteq,conv-period`, and 1 more; `alp` object node with required none and properties `azoteq,rx-enable`, `azoteq,tx-enable`, `azoteq,ati-frac-div-fine`, `azoteq,ati-frac-mult-coarse`, `azoteq,ati-frac-div-coarse`, `azoteq,ati-comp-div`, `azoteq,ati-target`, `azoteq,ati-base`, `azoteq,ati-mode`, `azoteq,sense-mode`, `azoteq,debounce-enter`, `azoteq,debounce-exit`, and 4 more; `button` object node with required none and properties `azoteq,ati-frac-div-fine`, `azoteq,ati-frac-mult-coarse`, `azoteq,ati-frac-div-coarse`, `azoteq,ati-comp-div`, `azoteq,ati-target`, `azoteq,ati-base`, `azoteq,ati-mode`, `azoteq,sense-mode`, `azoteq,touch-enter`, `azoteq,touch-exit`, `azoteq,debounce-enter`, `azoteq,debounce-exit`, and 3 more
- Conditional validation: if `azoteq,iqs7210a`: require none / constrain `alp`; if `azoteq,iqs7211e`: require none / constrain `reset-gpios`, `trackpad`, `alp`
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `irq-gpios`, `reset-gpios`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/touchscreen/azoteq,iqs7211.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 769-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/touchscreen/azoteq,iqs7211.yaml -->
