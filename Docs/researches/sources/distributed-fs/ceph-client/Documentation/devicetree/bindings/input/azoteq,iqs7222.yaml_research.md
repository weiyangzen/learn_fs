<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/azoteq,iqs7222.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/azoteq,iqs7222.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/azoteq,iqs7222.yaml` is a Linux devicetree YAML schema for a touchscreen/touchpad binding: **Azoteq IQS7222A/B/C/D Capacitive Touch Controller**. The Azoteq IQS7222A, IQS7222B, IQS7222C and IQS7222D are multichannel capacitive touch controllers that feature additional sensing capabilities. Link to datasheets: https://www.azoteq.com/ It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `azoteq,iqs7222a`, `azoteq,iqs7222b`, `azoteq,iqs7222c`, `azoteq,iqs7222d`.
- Required top-level fields: `compatible`, `reg`, `irq-gpios`.
- Maintainers: Jeff LaBundy <jeff@labundy.com>.
- Top-level properties: `compatible`, `reg`, `irq-gpios`, `reset-gpios`, `azoteq,max-counts`, `azoteq,auto-mode`, `azoteq,ati-frac-div-fine`, `azoteq,ati-frac-div-coarse`, `azoteq,ati-comp-select`, `azoteq,lta-beta-lp`, `azoteq,lta-beta-np`, `azoteq,counts-beta-lp`, `azoteq,counts-beta-np`, `azoteq,lta-fast-beta-lp`, `azoteq,lta-fast-beta-np`, `azoteq,timeout-ati-ms`, `azoteq,rate-ati-ms`, `azoteq,timeout-np-ms`, `azoteq,rate-np-ms`, `azoteq,timeout-lp-ms`, `azoteq,rate-lp-ms`, `azoteq,timeout-ulp-ms`, `azoteq,rate-ulp-ms`, `touchscreen-size-x`, `touchscreen-size-y`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`, and 1 more.
- `compatible`: enum `azoteq,iqs7222a`, `azoteq,iqs7222b`, `azoteq,iqs7222c`, `azoteq,iqs7222d`.
- `reg`: maxItems 1.
- `irq-gpios`: maxItems 1; Specifies the GPIO connected to the device's active-low RDY output..
- `reset-gpios`: maxItems 1; Specifies the GPIO connected to the device's active-low MCLR input. The device is temporarily held in hardware reset prior to initialization if this property is present..
- `touchscreen-size-x`.
- `touchscreen-size-y`.
- `azoteq,max-counts`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the maximum number of conversion periods (counts) that can be reported as follows: 0: 1023 1: 2047 2: 4095 3: 16384.
- `azoteq,auto-mode`: ref `/schemas/types.yaml#/definitions/uint32`; enum `0`, `1`, `2`, `3`; Specifies the number of conversions to occur before an interrupt is generated as follows: 0: 4 1: 8 2: 16 3: 32.
- `azoteq,ati-frac-div-fine`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the preloaded ATI fine fractional divider..
- `azoteq,ati-frac-div-coarse`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the preloaded ATI coarse fractional divider..
- `azoteq,ati-comp-select`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the preloaded ATI compensation selection..
- `azoteq,lta-beta-lp`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the long-term average filter damping factor to be applied during low-power mode..
- `azoteq,lta-beta-np`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the long-term average filter damping factor to be applied during normal-power mode..
- `azoteq,counts-beta-lp`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the counts filter damping factor to be applied during low-power mode..
- `azoteq,counts-beta-np`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the counts filter damping factor to be applied during normal- power mode..
- `azoteq,lta-fast-beta-lp`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the long-term average filter fast damping factor to be applied during low-power mode..
- `azoteq,lta-fast-beta-np`: ref `/schemas/types.yaml#/definitions/uint32`; Specifies the long-term average filter fast damping factor to be applied during normal-power mode..
- `azoteq,timeout-ati-ms`: Specifies the delay (in ms) before ATI is retried following an ATI error..
- additional schema properties: `azoteq,rate-ati-ms`, `azoteq,timeout-np-ms`, `azoteq,rate-np-ms`, `azoteq,timeout-lp-ms`, `azoteq,rate-lp-ms`, `azoteq,timeout-ulp-ms`, `azoteq,rate-ulp-ms`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`, `trackpad`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `input.yaml#`, `/schemas/pinctrl/pincfg-node.yaml#`, `touchscreen/touchscreen.yaml#`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: `^cycle-[0-9]$` child nodes with required none and properties `azoteq,conv-period`, `azoteq,conv-frac`, `azoteq,tx-enable`, `azoteq,rx-float-inactive`, `azoteq,dead-time-enable`, `azoteq,tx-freq-fosc`, `azoteq,vbias-enable`, `azoteq,sense-mode`, `azoteq,iref-enable`, `azoteq,iref-level`, `azoteq,iref-trim`; `^channel-([0-9]|1[0-9])$` child nodes with required none and properties `azoteq,ulp-allow`, `azoteq,ref-select`, `azoteq,ref-weight`, `azoteq,use-prox`, `azoteq,counts-filt-enable`, `azoteq,ati-band`, `azoteq,global-halt`, `azoteq,invert-enable`, `azoteq,dual-direction`, `azoteq,rx-enable`, `azoteq,samp-cap-double`, `azoteq,vref-half`, and 11 more; `^slider-[0-1]$` child nodes with required `azoteq,channel-select` and properties `azoteq,channel-select`, `azoteq,slider-size`, `azoteq,lower-cal`, `azoteq,upper-cal`, `azoteq,top-speed`, `azoteq,bottom-speed`, `azoteq,bottom-beta`, `azoteq,static-beta`, `azoteq,use-prox`, `linux,axis`; `^gpio-[0-2]$` child nodes with required none and properties `drive-open-drain`; `trackpad` object node with required `azoteq,channel-select` and properties `azoteq,channel-select`, `azoteq,num-rows`, `azoteq,num-cols`, `azoteq,top-speed`, `azoteq,bottom-speed`, `azoteq,use-prox`
- Conditional validation: if `azoteq,iqs7222a`, `azoteq,iqs7222b`, `azoteq,iqs7222c`: require none / constrain `touchscreen-size-x`, `touchscreen-size-y`, `touchscreen-inverted-x`, `touchscreen-inverted-y`, `touchscreen-swapped-x-y`, `trackpad`; if `azoteq,iqs7222b`, `azoteq,iqs7222c`: require none / constrain none; if `azoteq,iqs7222b`, `azoteq,iqs7222d`: require none / constrain none; if `azoteq,iqs7222b`: require none / constrain none; if `azoteq,iqs7222a`: require none / constrain none
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
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/azoteq,iqs7222.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 1148-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/azoteq,iqs7222.yaml -->
