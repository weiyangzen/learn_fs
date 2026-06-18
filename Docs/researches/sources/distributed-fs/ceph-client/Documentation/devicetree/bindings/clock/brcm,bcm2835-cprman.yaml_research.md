<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2835-cprman.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2835-cprman.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2835-cprman.yaml` is a Devicetree binding schema for `Broadcom BCM2835 CPRMAN clocks`. It documents and validates clock-provider nodes for Broadcom clock infrastructure, with compatible contract `brcm,bcm2711-cprman`, `brcm,bcm2835-cprman`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The CPRMAN clock controller generates clocks in the audio power domain of the BCM2835. There is a level of PLLs deriving from an external oscillator, a level of PLL dividers that produce channels off of the few PLLs, and a level of mostly-generic clock generators sourcing from the PLL channels. Most other hardware components source from the clock generators, but a few (like the ARM or HDMI) will source from the PLL d.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `reg`, `clocks`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `brcm,bcm2711-cprman`, `brcm,bcm2835-cprman`.
- `reg`: maxItems 1.
- `clocks`: minItems 1; 7 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 59 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `brcm,bcm2711-cprman`, `brcm,bcm2835-cprman`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2835-cprman.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2835-cprman.yaml -->
