<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs269a.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs269a.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs269a.yaml` is a Linux devicetree YAML schema for a key/button input binding: **Azoteq IQS269A Capacitive Touch Controller**. The Azoteq IQS269A is an 8-channel capacitive touch controller that features additional Hall-effect and inductive sensing capabilities. Link to datasheet: https://www.azoteq.com/ It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `azoteq,iqs269a`, `azoteq,iqs269a-00`, `azoteq,iqs269a-d0`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`.
- Maintainers: Jeff LaBundy <jeff@labundy.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `#address-cells`, `#size-cells`, `azoteq,hall-enable`, `azoteq,suspend-mode`, `azoteq,clk-div`, `azoteq,ulp-update`, `azoteq,reseed-offset`, `azoteq,filt-str-lp-lta`, `azoteq,filt-str-lp-cnt`, `azoteq,filt-str-np-lta`, `azoteq,filt-str-np-cnt`, `azoteq,rate-np-ms`, `azoteq,rate-lp-ms`, `azoteq,rate-ulp-ms`, `azoteq,timeout-pwr-ms`, `azoteq,timeout-lta-ms`, `azoteq,ati-band-disable`, `azoteq,ati-lp-only`, `azoteq,ati-band-tighten`, `azoteq,filt-disable`, `azoteq,gpio3-select`, `azoteq,dual-direction`, `azoteq,tx-freq`, `azoteq,global-cap-increase`, `azoteq,reseed-select`, and 8 more.
- `compatible`: enum `azoteq,iqs269a`, `azoteq,iqs269a-00`, `azoteq,iqs269a-d0`.
- `reg`: maxItems 1.
- `interrupts`: maxItems 1.
- `linux,keycodes`: maxItems 8; minItems 1; Specifies the numeric keycodes associated with each available gesture in the following order (enter 0 for unused gestures): 0: Slider 0 tap 1: Slider 0 hold 2: Slider 0 positive flick or swipe 3: Slider 0 negative flick or swipe 4: Slider 1 tap 5: Slider 1....
- `#address-cells`: const `1`.
- `#size-cells`: const `0`.
- `azoteq,hall-enable`: type `boolean`; Enables Hall-effect sensing on channels 6 and 7. In this case, keycodes assigned to channel 6 are ignored and keycodes assigned to channel 7 are interpreted as switch codes. Refer to the datasheet for requirements im- posed on channels 6 and 7 by....
- `azoteq,suspend-mode`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the power mode during suspend as follows: 0: Automatic (same as normal runtime, i.e. suspend/resume disabled) 1: Low power (all sensing at a reduced reporting rate) 2: Ultra-low power (channel 0 proximity sensing) 3: Halt (no sensing).
- `azoteq,clk-div`: type `boolean`; Divides the device's core clock by a factor of 4..
- `azoteq,ulp-update`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the ultra-low-power mode update rate..
- `azoteq,reseed-offset`: type `boolean`; Applies an 8-count offset to all long-term averages upon either ATI or reseed events..
- `azoteq,filt-str-lp-lta`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the long-term average filter strength during low-power mode..
- `azoteq,filt-str-lp-cnt`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the raw count filter strength during low-power mode..
- `azoteq,filt-str-np-lta`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the long-term average filter strength during normal-power mode..
- `azoteq,filt-str-np-cnt`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the raw count filter strength during normal-power mode..
- `azoteq,rate-np-ms`: Specifies the report rate (in ms) during normal-power mode..
- `azoteq,rate-lp-ms`: Specifies the report rate (in ms) during low-power mode..
- `azoteq,rate-ulp-ms`: Specifies the report rate (in ms) during ultra-low-power mode..
- additional schema properties: `azoteq,timeout-pwr-ms`, `azoteq,timeout-lta-ms`, `azoteq,ati-band-disable`, `azoteq,ati-lp-only`, `azoteq,ati-band-tighten`, `azoteq,filt-disable`, `azoteq,gpio3-select`, `azoteq,dual-direction`, `azoteq,tx-freq`, `azoteq,global-cap-increase`, `azoteq,reseed-select`, `azoteq,tracking-enable`, `azoteq,filt-str-slider`, `azoteq,touch-hold-ms`, `azoteq,gesture-swipe`, `azoteq,timeout-tap-ms`, `azoteq,timeout-swipe-ms`, `azoteq,thresh-swipe`.
- Shared-schema dependencies are pulled with `$ref`: `input.yaml#`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^channel@[0-7]$` child nodes with required `reg` and properties `reg`, `azoteq,reseed-disable`, `azoteq,blocking-enable`, `azoteq,slider0-select`, `azoteq,slider1-select`, `azoteq,rx-enable`, `azoteq,tx-enable`, `azoteq,meas-cap-decrease`, `azoteq,rx-float-inactive`, `azoteq,local-cap-size`, `azoteq,invert-enable`, `azoteq,proj-bias`, and 8 more
- Conditional validation: if `azoteq,iqs269a-d0`: require none / constrain none
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `azoteq,gpio3-select`.
- Integrates with the common input schema for Linux event codes, wakeup/autorepeat semantics, and input-device metadata.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; child-node regexes and required child fields are easy to regress because node names are part of the ABI; conditional branches can reject valid boards if compatible-specific requirements are too broad; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/iqs269a.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 648-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/iqs269a.yaml -->
