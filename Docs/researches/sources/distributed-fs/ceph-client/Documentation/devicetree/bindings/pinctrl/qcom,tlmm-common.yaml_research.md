# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/qcom,tlmm-common.yaml

## Purpose
This shared schema supplies the common Qualcomm TLMM contract reused by SoC-specific Qualcomm bindings. It centralizes GPIO/interrupt controller requirements and the common pin configuration and pin mux node definition. Source title: Qualcomm Technologies, Inc. Top Level Mode Multiplexer (TLMM) definitions. Description signal from the file: This defines the common properties used to describe all Qualcomm Top Level Mode Multiplexer bindings and pinconf/pinmux states for these.

## Important APIs, Types, and Schema Surface
- Lines read: 101.
- Compatible contract: None declared in this schema. Top-level required properties: interrupts, interrupt-controller, #interrupt-cells, gpio-controller, #gpio-cells, gpio-ranges. Important top-level properties found in the schema: interrupts, gpio-controller, interrupt-controller, #gpio-cells, #interrupt-cells, gpio-ranges, gpio-reserved-ranges. Child-node patterns: None declared in this schema. Referenced schemas: pinctrl.yaml#, pincfg-node.yaml#, pinmux-node.yaml#.

## Control Flow
SoC-specific Qualcomm schemas include this file with `allOf`. The common schema validates controller capabilities and defines `$defs/qcom-tlmm-state`, which composes generic `pincfg-node.yaml` and `pinmux-node.yaml` with Qualcomm-specific state allowances.

## State and Persistence Behavior
The file is a shared ABI fragment. Its definitions persist expectations for every importing Qualcomm TLMM schema, including GPIO and interrupt-controller provider cells and permitted state-node properties.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Any change here fans out to many Qualcomm SoCs. Tightening or loosening common properties can create broad dtbs_check regressions, so edits need cross-SoC validation rather than testing one binding only.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/qcom,tlmm-common.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
