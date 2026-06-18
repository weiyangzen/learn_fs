# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/mfd/syscon-common.yaml

Purpose: Common schema fragment for system-controller register blocks that exposes reusable properties shared by syscon-style bindings.

Important schema surface and control flow: the schema requires `compatible` and includes common property definitions for syscon register regions, notably `reg-io-width` constrained to 1, 2, 4, or 8 bytes. Its `allOf` logic aligns the fragment with the core simple-bus/syscon-style contract and is intended for inclusion by concrete syscon bindings rather than direct board use alone.

State, dependencies, and integration: persistent DT state described through this fragment becomes regmap configuration and compatible matching for system controller drivers and consumers. Dependencies include the DT core schema and concrete bindings that include this common fragment, especially `syscon.yaml`. Risks include concrete bindings forgetting to include this common schema, invalid I/O width values that produce wrong regmap access size, and treating the common file as a complete device binding. Test signals are schema validation of including bindings and `dt_binding_check` failures for unsupported `reg-io-width`.
