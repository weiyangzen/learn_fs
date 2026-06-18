# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/pinctrl/semtech,sx1501q.yaml

## Purpose
This schema describes the I2C-attached Semtech SX150x GPIO expander family. It combines GPIO provider, optional interrupt provider, and pin configuration child nodes with chip-specific GPIO and OSCIO pin limits. Source title: Semtech SX150x GPIO expander. Description signal from the file: No long-form description is present; the binding contract is carried by the schema properties and examples.

## Important APIs, Types, and Schema Surface
- Lines read: 251.
- Compatible contract: semtech,sx1501q, semtech,sx1502q, semtech,sx1503q, semtech,sx1504q, semtech,sx1505q, semtech,sx1506q, semtech,sx1507q, semtech,sx1508q, semtech,sx1509q. Top-level required properties: compatible, reg, #gpio-cells, gpio-controller. Important top-level properties found in the schema: reg, interrupts, gpio-controller, interrupt-controller, #gpio-cells, #interrupt-cells, gpio-line-names, semtech,probe-reset. Child-node patterns: -cfg$. Referenced schemas: pincfg-node.yaml#, pinmux-node.yaml#, pinctrl.yaml#.

## Control Flow
Validation first selects the SX150x compatible, then conditional `allOf` branches set `gpio-line-names` cardinality and allowed `pins` patterns for each chip width. `*-cfg` children combine pinconf and pinmux schema references; OSCIO pins deliberately reject bias and open-drain properties.

## State and Persistence Behavior
Persistent state is the I2C address, GPIO/interrupt provider cells, optional `semtech,probe-reset`, and named child configs. The schema encodes family capabilities so existing DTS files remain tied to the correct 4, 8, or 16 GPIO variants plus optional OSCIO.

## Dependencies and Integration Points
This schema is consumed by Linux devicetree validation tooling (`dt-schema`), board DTS files under architecture trees, and the matching kernel pinctrl/GPIO/interrupt driver. Integration points include `pinctrl.yaml`, generic `pinmux-node.yaml`/`pincfg-node.yaml`, vendor common schemas, dt-bindings headers, GPIO and interrupt-controller bindings, and SoC clock/reset/power-domain providers where referenced.

## Risks and Edge Cases
Main risks are permitting `semtech,probe-reset` on older devices, accepting the wrong GPIO count, or allowing OSCIO-only invalid electrical settings. Tests should cover each conditional compatible family.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/pinctrl/semtech,sx1501q.yaml` and at least one `make dtbs_check` target containing a DTS user of the compatible. For shared helper schemas, run the top-level importing bindings as well. Review the in-file example because it exercises required properties, child-node shape, and referenced dt-bindings constants.
