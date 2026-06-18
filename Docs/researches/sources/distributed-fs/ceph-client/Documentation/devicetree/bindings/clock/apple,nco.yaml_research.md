<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apple,nco.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apple,nco.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apple,nco.yaml` is a Devicetree binding schema for `Apple SoCs' NCO block`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `apple,t6020-nco`, `apple,t8103-nco`, `apple,t6000-nco`, `apple,t8112-nco`, `apple,nco`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The NCO (Numerically Controlled Oscillator) block found on Apple SoCs such as the t8103 (M1) is a programmable clock generator performing fractional division of a high frequency input clock. It carries a number of independent channels and is typically used for generation of audio bitclocks..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `clocks`, `#clock-cells`, `reg`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 2 oneOf alternatives.
- `reg`: maxItems 1.
- `clocks`: maxItems 1; Specifies the reference clock from which the output clocks are derived through fractional division..
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 68 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `apple,t6020-nco`, `apple,t8103-nco`, `apple,t6000-nco`, `apple,t8112-nco`, `apple,nco`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apple,nco.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apple,nco.yaml -->
