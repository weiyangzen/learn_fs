# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/spacemit,k1-pinctrl.yaml

## Purpose
This schema describes the SpacemiT K1/K3 pin controller, including protected register access through syscon-style integration and standard pinmux/pinconf child nodes. Source title: SpacemiT K1 SoC Pin Controller. Description signal from the file: No long-form description is present; the binding contract is carried by the schema properties and examples.

## Important APIs, Types, and Schema Surface
- Lines read: 159.
- Compatible contract: spacemit,k1-pinctrl, spacemit,k3-pinctrl. Top-level required properties: compatible, reg, clocks, clock-names. Important top-level properties found in the schema: reg, clocks, clock-names, resets, spacemit,apbc. Child-node patterns: -cfg$, -pins$. Referenced schemas: /schemas/types.yaml#/definitions/phandle, pincfg-node.yaml#, pinmux-node.yaml#, /schemas/types.yaml#/definitions/uint32.

## Control Flow
Validation selects K1/K3 compatibles, validates syscon/protected-register integration, and accepts child groups that combine standard pinmux/pinconf with SpacemiT-specific power, drive, and register access properties.

## State and Persistence Behavior
Persistent ABI includes syscon phandles and pin state values. The schema itself is stateless, but it guards access to protected register configuration expected by the driver.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Incorrect syscon references or electrical values can lead to invalid protected-register writes. Keep phandle typing and vendor property ranges aligned with the driver.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/spacemit,k1-pinctrl.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
