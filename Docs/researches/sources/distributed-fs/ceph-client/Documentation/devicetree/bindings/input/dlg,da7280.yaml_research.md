<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da7280.yaml -->
# Research: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da7280.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da7280.yaml` is a Linux devicetree YAML schema for a haptic/vibrator binding: **Dialog Semiconductor DA7280 Low Power High-Definition Haptic Driver**. The file describes the devicetree contract for the Dialog Semiconductor DA7280 Low Power High-Definition Haptic Driver. It is part of the kernel `Documentation/devicetree/bindings/input` ABI surface, so changes affect DTS validation and the contract consumed by input, touchscreen, keypad, haptics, GPIO, I2C, SPI, regulator, PWM, ADC, and PMIC drivers.

## Important APIs, Types, and Schema Surface
- Compatible contract: `dlg,da7280`.
- Required top-level fields: `compatible`, `reg`, `interrupts`, `dlg,actuator-type`, `dlg,const-op-mode`, `dlg,periodic-op-mode`, `dlg,nom-microvolt`, `dlg,abs-max-microvolt`, `dlg,imax-microamp`, `dlg,impd-micro-ohms`.
- Maintainers: Roy Im <roy.im.opensource@diasemi.com>.
- Top-level properties: `compatible`, `reg`, `interrupts`, `dlg,actuator-type`, `dlg,const-op-mode`, `dlg,periodic-op-mode`, `dlg,nom-microvolt`, `dlg,abs-max-microvolt`, `dlg,imax-microamp`, `dlg,impd-micro-ohms`, `pwms`, `dlg,ps-seq-id`, `dlg,ps-seq-loop`, `dlg,gpi0-seq-id`, `dlg,gpi1-seq-id`, `dlg,gpi2-seq-id`, `dlg,gpi0-mode`, `dlg,gpi1-mode`, `dlg,gpi2-mode`, `dlg,gpi0-polarity`, `dlg,gpi1-polarity`, `dlg,gpi2-polarity`, `dlg,resonant-freq-hz`, `dlg,bemf-sens-enable`, `dlg,freq-track-enable`, `dlg,acc-enable`, `dlg,rapid-stop-enable`, `dlg,amp-pid-enable`, and 1 more.
- `compatible`: const `dlg,da7280`.
- `reg`: maxItems 1; I2C address of the device..
- `interrupts`: maxItems 1.
- `pwms`: maxItems 1.
- `dlg,actuator-type`: enum `LRA`, `ERM-bar`, `ERM-coin`.
- `dlg,const-op-mode`: ref `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`; Haptic operation mode for FF_CONSTANT.
- `dlg,periodic-op-mode`: ref `/schemas/types.yaml#/definitions/uint32`; enum `1`, `2`; Haptic operation mode for FF_PERIODIC. The default value is 1 for both of the operation modes. For more details, please see the datasheet.
- `dlg,nom-microvolt`: Nominal actuator voltage rating.
- `dlg,abs-max-microvolt`: Absolute actuator maximum voltage rating.
- `dlg,imax-microamp`: Actuator max current rating.
- `dlg,impd-micro-ohms`: Impedance of the actuator.
- `dlg,ps-seq-id`: ref `/schemas/types.yaml#/definitions/uint32`; The PS_SEQ_ID(pattern ID in waveform memory inside chip) to play back when RTWM-MODE is enabled.
- `dlg,ps-seq-loop`: ref `/schemas/types.yaml#/definitions/uint32`; The PS_SEQ_LOOP, Number of times the pre-stored sequence pointed to by PS_SEQ_ID or GPI(N)_SEQUENCE_ID is repeated.
- `dlg,gpi0-seq-id`: ref `/schemas/types.yaml#/definitions/uint32`; the GPI0_SEQUENCE_ID, pattern to play when gpi0 is triggered.
- `dlg,gpi1-seq-id`: ref `/schemas/types.yaml#/definitions/uint32`; the GPI1_SEQUENCE_ID, pattern to play when gpi1 is triggered.
- `dlg,gpi2-seq-id`: ref `/schemas/types.yaml#/definitions/uint32`; the GPI2_SEQUENCE_ID, pattern to play when gpi2 is triggered.
- `dlg,gpi0-mode`: enum `Single-pattern`, `Multi-pattern`; Pattern mode for gpi0.
- `dlg,gpi1-mode`: enum `Single-pattern`, `Multi-pattern`; Pattern mode for gpi1.
- additional schema properties: `dlg,gpi2-mode`, `dlg,gpi0-polarity`, `dlg,gpi1-polarity`, `dlg,gpi2-polarity`, `dlg,resonant-freq-hz`, `dlg,bemf-sens-enable`, `dlg,freq-track-enable`, `dlg,acc-enable`, `dlg,rapid-stop-enable`, `dlg,amp-pid-enable`, `dlg,mem-array`.
- Shared-schema dependencies are pulled with `$ref`: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control Flow and Validation Behavior
- dt-schema starts at the compatible match, checks the required list, then validates each named property and any matching child-node regex. Child-node validation: no child-node pattern is declared; the node is validated directly.
- Conditional validation: there are no compatible-driven conditional branches; validation is mostly direct property checking.
- Unknown-property policy is `additionalProperties: False` and `unevaluatedProperties: not set`. This matters because many input bindings intentionally close the ABI after importing common schemas.
- The examples block is present and acts as the main executable test fixture for `dt_binding_check`.

## State, Persistence, Dependencies, and Integration Points
- There is no runtime state in this YAML file. Persistence is the devicetree ABI itself: once DTS files use these property names, compatible strings, child node names, or encoded key values, kernel drivers and schema validation must keep accepting them unless a migration is coordinated.
- Hardware and subsystem dependencies signaled by properties: `reg`, `interrupts`, `pwms`.
- The `reg` address and bus placement connect the binding to I2C/SPI/platform device instantiation and driver match tables.

## Risks and Test Signals
- Primary risks: removing or renaming required properties would break existing DTS validation and driver probe assumptions; compatible strings must stay aligned with driver `of_device_id` tables; updates to referenced common schemas can tighten this binding unexpectedly.
- Test signals: run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/input/dlg,da7280.yaml`; keep the embedded example compiling under dt-schema; validate representative DTS users with `make dtbs_check`; cross-check compatible strings against the matching Linux input/touchscreen/haptics driver.
- Research note: this report was generated after reading the full 248-line schema and extracting titles, compatible strings, required fields, properties, child patterns, `$ref`s, examples, and conditional branches.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/input/dlg,da7280.yaml -->
