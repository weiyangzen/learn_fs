# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/renesas,rzg2l-poeg.yaml

## Purpose
This schema is for Renesas RZ/G2L Port Output Enable for GPT rather than a general pinctrl provider. It validates the safety/control sideband that can disable timer output pins through POEG inputs and GPT linkage. Source title: Renesas RZ/G2L Port Output Enable for GPT (POEG). Description signal from the file: The output pins(GTIOCxA and GTIOCxB) of the general PWM timer (GPT) can be disabled by using the port output enabling function for the GPT (POEG). Specifically, either of the following ways can be used. * Input level detection of the GTETRGA to GTETRGD pins. * Output-disable request from the GPT. * SSF bit setting(ie, by setting POEGGn.SSF to 1) The state of the GTIOCxA and the GTIOCxB pins when the output is disabled, are controlled by the GPT m

## Important APIs, Types, and Schema Surface
- Lines read: 86.
- Compatible contract: renesas,r9a07g044-poeg, renesas,r9a07g054-poeg, renesas,rzg2l-poeg, renesas,poeg-id, renesas,gpt. Top-level required properties: compatible, reg, interrupts, clocks, power-domains, resets, renesas,poeg-id, renesas,gpt. Important top-level properties found in the schema: reg, interrupts, clocks, resets, power-domains, renesas,poeg-id, renesas,gpt. Child-node patterns: None declared in this schema. Referenced schemas: /schemas/types.yaml#/definitions/phandle, /schemas/types.yaml#/definitions/uint32.

## Control Flow
Validation requires POEG resources, interrupt, clock/reset/power-domain wiring, a `renesas,poeg-id`, and a `renesas,gpt` phandle. Unlike pinmux schemas, there are no arbitrary pin state children; the control flow models a fixed hardware sideband relation to GPT outputs.

## State and Persistence Behavior
Persistent ABI is the POEG node identity and linkage to the GPT provider. The runtime driver can use this relationship to disable timer outputs according to hardware input conditions, but the YAML only validates the static topology.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Wrong phandle typing or POEG ID constraints can misrepresent safety-related timer output disable wiring. Tests should include the documented compatible fallback and required resource set.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/renesas,rzg2l-poeg.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
