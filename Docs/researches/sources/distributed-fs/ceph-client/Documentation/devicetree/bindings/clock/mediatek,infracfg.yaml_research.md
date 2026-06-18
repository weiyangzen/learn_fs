<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,infracfg.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,infracfg.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,infracfg.yaml` is a Devicetree binding schema for `MediaTek Infrastructure System Configuration Controller`. It documents and validates clock-provider nodes for MediaTek clock/reset infrastructure, with compatible contract `mediatek,mt2701-infracfg`, `mediatek,mt2712-infracfg`, `mediatek,mt6735-infracfg`, `mediatek,mt6765-infracfg`, `mediatek,mt6795-infracfg`, `mediatek,mt6779-infracfg_ao`, `mediatek,mt6797-infracfg`, `mediatek,mt7622-infracfg`, `mediatek,mt7629-infracfg`, `mediatek,mt7981-infracfg`, `mediatek,mt7986-infracfg`, `mediatek,mt7988-infracfg`, and 7 more. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The Mediatek infracfg controller provides various clocks and reset outputs to the system. The clock values can be found in <dt-bindings/clock/mt*-clk.h> and <dt-bindings/clock/mediatek,mt*-infracfg.h>, and reset values in <dt-bindings/reset/mt*-reset.h>, <dt-bindings/reset/mt*-resets.h> and <dt-bindings/reset/mediatek,mt*-infracfg.h>..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: 2 oneOf alternatives.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 87 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/mt*-clk.h`, `dt-bindings/clock/mediatek,mt*-infracfg.h`, `dt-bindings/reset/mt*-reset.h`, `dt-bindings/reset/mt*-resets.h`, `dt-bindings/reset/mediatek,mt*-infracfg.h`, MMIO resource description through `reg`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `mediatek,mt2701-infracfg`, `mediatek,mt2712-infracfg`, `mediatek,mt6735-infracfg`, `mediatek,mt6765-infracfg`, `mediatek,mt6795-infracfg`, `mediatek,mt6779-infracfg_ao`, `mediatek,mt6797-infracfg`, `mediatek,mt7622-infracfg`, `mediatek,mt7629-infracfg`, `mediatek,mt7981-infracfg`, `mediatek,mt7986-infracfg`, `mediatek,mt7988-infracfg`, and 7 more, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,infracfg.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,infracfg.yaml -->
