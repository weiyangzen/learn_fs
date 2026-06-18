<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,sai-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,sai-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,sai-clock.yaml` is a Devicetree binding schema for `Freescale SAI bitclock-as-a-clock`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx8mm-sai-clock`, `fsl,imx8mn-sai-clock`, `fsl,imx8mp-sai-clock`, `fsl,imx8mq-sai-clock`, `fsl,vf610-sai-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: It is possible to use the BCLK or MCLK pin of a SAI module as a generic clock output. Some SoC are very constrained in their pin multiplexer configuration. E.g. pins can only be changed in groups. For example, on the LS1028A SoC you can only enable SAIs in pairs. If you use only one SAI, the second pins are wasted. Using this binding it is possible to use the clock of the second SAI as a MCLK clock for an audio codec.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: present with inherited core-schema constraints; this defines how consumers encode clock phandle specifiers.
- `compatible`: 2 oneOf alternatives.
- `reg`: maxItems 1.
- `clocks`: maxItems 2; minItems 1.
- `clock-names`: minItems 1; 2 positional items.
- `#clock-cells`: present with inherited core-schema constraints.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 84 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx8mm-sai-clock`, `fsl,imx8mn-sai-clock`, `fsl,imx8mp-sai-clock`, `fsl,imx8mq-sai-clock`, `fsl,vf610-sai-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,sai-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,sai-clock.yaml -->
