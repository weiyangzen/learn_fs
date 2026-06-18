<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mvebu-core-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mvebu-core-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mvebu-core-clock.yaml` is a Devicetree binding schema for `Marvell MVEBU SoC core clock`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,armada-370-core-clock`, `marvell,armada-375-core-clock`, `marvell,armada-380-core-clock`, `marvell,armada-390-core-clock`, `marvell,armada-xp-core-clock`, `marvell,dove-core-clock`, `marvell,kirkwood-core-clock`, `marvell,mv88f5181-core-clock`, `marvell,mv88f5182-core-clock`, `marvell,mv88f5281-core-clock`, `marvell,mv88f6180-core-clock`, `marvell,mv88f6183-core-clock`, and 2 more. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Marvell MVEBU SoCs usually allow to determine core clock frequencies by reading the Sample-At-Reset (SAR) register. The core clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. The following is a list of provided IDs and clock names on Armada 370/XP: 0 = tclk (Internal Bus clock) 1 = cpuclk (CPU clock) 2 = nbclk (L2 Cache clock) 3 = hclk (DRAM control clock) 4 = dramcl.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `marvell,armada-370-core-clock`, `marvell,armada-375-core-clock`, `marvell,armada-380-core-clock`, `marvell,armada-390-core-clock`, `marvell,armada-xp-core-clock`, `marvell,dove-core-clock`, `marvell,kirkwood-core-clock`, `marvell,mv88f5181-core-clock`, and 6 more.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `clock-output-names`: Overwrite default clock output names..

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 94 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `marvell,armada-370-core-clock`, `marvell,armada-375-core-clock`, `marvell,armada-380-core-clock`, `marvell,armada-390-core-clock`, `marvell,armada-xp-core-clock`, `marvell,dove-core-clock`, `marvell,kirkwood-core-clock`, `marvell,mv88f5181-core-clock`, `marvell,mv88f5182-core-clock`, `marvell,mv88f5281-core-clock`, `marvell,mv88f6180-core-clock`, `marvell,mv88f6183-core-clock`, and 2 more, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mvebu-core-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mvebu-core-clock.yaml -->
