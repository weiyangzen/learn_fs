# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/sprd,sc9860-pinctrl.yaml

## Purpose
This schema describes the Spreadtrum SC9860 pin controller, organized around typed register blocks and pin nodes with both standard and Spreadtrum-specific sleep/global-control fields. Source title: Spreadtrum SC9860 Pin Controller. Description signal from the file: The Spreadtrum pin controller are organized in 3 blocks (types). The first block comprises some global control registers, and each register contains several bit fields with one bit or several bits to configure for some global common configuration, such as domain pad driving level, system control select and so on ("domain pad driving level": One pin can output 3.0v or 1.8v, depending on the related domain pad driving selection, if the related doma

## Important APIs, Types, and Schema Surface
- Lines read: 199.
- Compatible contract: sprd,sc9860-pinctrl. Top-level required properties: compatible, reg. Important top-level properties found in the schema: reg. Child-node patterns: sleep$. Function enum sample: func1, func2, func3, func4. Referenced schemas: #/$defs/pin-node, /schemas/types.yaml#/definitions/uint32, /schemas/pinctrl/pincfg-node.yaml#, /schemas/pinctrl/pinmux-node.yaml#, /schemas/types.yaml#/definitions/string-array.

## Control Flow
Validation requires compatible and register resources, then dispatches child pin nodes through `$defs/pin-node`. The pin node composes standard pinconf/pinmux with Spreadtrum-specific sleep mode, global-control, and register block fields.

## State and Persistence Behavior
Persistent ABI is the register block layout and pin-node vocabulary used by SC9860 DTS files. Sleep-related properties describe static low-power state selection rather than mutable YAML persistence.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
The risky area is sleep/global control encoding. Values are tied to databook meanings, so schema broadening can validate DTS settings that produce incorrect low-power behavior.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/sprd,sc9860-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
