<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs626a.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs626a.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs626a.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Azoteq IQS626A Capacitive Touch Controller**. The Azoteq IQS626A is a 14-channel capacitive touch controller that features additional Hall-effect and inductive sensing capabilities. Link to datasheet: https://www.azoteq.com/ It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `azoteq,iqs626a`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`.
- Maintainers: Jeff LaBundy <jeff@labundy.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`, `azoteq,suspend-mode`, `azoteq,clk-div`, `azoteq,ulp-enable`, `azoteq,ulp-update`, `azoteq,ati-band-disable`, `azoteq,ati-lp-only`, `azoteq,gpio3-select`, `azoteq,reseed-select`, `azoteq,thresh-extend`, `azoteq,tracking-enable`, `azoteq,reseed-offset`, `azoteq,rate-np-ms`, `azoteq,rate-lp-ms`, `azoteq,rate-ulp-ms`, `azoteq,timeout-pwr-ms`, `azoteq,timeout-lta-ms`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`.
- `compatible`: const `azoteq,iqs626a`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `azoteq,suspend-mode`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the power mode during suspend as follows: 0: Automatic (same as normal runtime, i.e. suspend/resume disabled) 1: Low power (all sensing at a reduced reporting rate) 2: Ultra-low power (ULP channel proximity sensing) 3: Halt (no sensing).
- `azoteq,clk-div`: type `boolean`; Divides the device's core clock by a factor of 4..
- `azoteq,ulp-enable`: type `boolean`; Permits the device to automatically enter ultra-low-power mode from low- power mode..
- `azoteq,ulp-update`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`, `4`, and 3 more; Specifies the rate at which the trackpad, generic and Hall channels are updated during ultra-low-power mode as follows: 0: 8 1: 13 2: 28 3: 54 4: 89 5: 135 6: 190 7: 256.
- `azoteq,ati-band-disable`: type `boolean`; Disables the ATI band check..
- `azoteq,ati-lp-only`: type `boolean`; Limits automatic ATI to low-power mode..
- `azoteq,gpio3-select`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`, `4`, and 3 more; Selects the channel or group of channels for which the GPIO3 pin represents touch state as follows: 0: None 1: ULP channel 2: Trackpad 3: Trackpad 4: Generic channel 0 5: Generic channel 1 6: Generic channel 2 7: Hall channel.
- `azoteq,reseed-select`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the event(s) that prompt the device to reseed (i.e. reset the long-term average) of an associated channel as follows: 0: None 1: Proximity 2: Proximity or touch 3: Proximity, touch or deep touch.
- `azoteq,thresh-extend`: type `boolean`; Multiplies all touch and deep-touch thresholds by 4..
- `azoteq,tracking-enable`: type `boolean`; Enables all associated channels to track their respective reference channels..
- `azoteq,reseed-offset`: type `boolean`; Applies an 8-count offset to all long-term averages upon either ATI or reseed events..
- `azoteq,rate-np-ms`: Specifies the report rate (in ms) during normal-power mode..
- `azoteq,rate-lp-ms`: Specifies the report rate (in ms) during low-power mode..
- additional schema properties: `azoteq,rate-ulp-ms`, `azoteq,timeout-pwr-ms`, `azoteq,timeout-lta-ms`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`.
- Shared-schema dependencies are pulled with `$ref`: `touchscreen/touchscreen.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/string-array`, `input.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^ulp-0|generic-[0-2]|hall$` child nodes with required none and properties `azoteq,ati-exclude`, `azoteq,reseed-disable`, `azoteq,meas-cap-decrease`, `azoteq,rx-inactive`, `azoteq,linearize`, `azoteq,dual-direction`, `azoteq,filt-disable`, `azoteq,ati-mode`, `azoteq,ati-base`, `azoteq,ati-target`, `azoteq,cct-increase`, `azoteq,proj-bias`, and 17 more; `^trackpad-3x[2-3]$` child nodes with required none and properties `azoteq,ati-exclude`, `azoteq,reseed-disable`, `azoteq,meas-cap-decrease`, `azoteq,rx-inactive`, `azoteq,linearize`, `azoteq,dual-direction`, `azoteq,filt-disable`, `azoteq,ati-mode`, `azoteq,ati-target`, `azoteq,cct-increase`, `azoteq,proj-bias`, `azoteq,sense-freq`, and 11 more
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `azoteq,gpio3-select`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- Integrates with common touchscreen properties for axes, inversion, swapping, fuzz, pressure, and panel linkage where applicable.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/iqs626a.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 878-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs626a.yaml -->
