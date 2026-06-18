<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,iproc-clocks.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,iproc-clocks.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,iproc-clocks.yaml` is a Devicetree binding schema for `Broadcom iProc Family Clocks`. It documents and validates clock-provider nodes for Broadcom clock infrastructure, with compatible contract `brcm,bcm63138-armpll`, `brcm,cygnus-armpll`, `brcm,cygnus-genpll`, `brcm,cygnus-lcpll0`, `brcm,cygnus-mipipll`, `brcm,cygnus-asiu-clk`, `brcm,cygnus-audiopll`, `brcm,hr2-armpll`, `brcm,nsp-armpll`, `brcm,nsp-genpll`, `brcm,nsp-lcpll0`, `brcm,ns2-genpll-scr`, and 13 more. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The iProc clock controller manages clocks that are common to the iProc family. An SoC from the iProc family may have several PLLs, e.g., ARMPLL, GENPLL, LCPLL0, MIPIPLL, and etc., all derived from an onboard crystal. Each PLL comprises of several leaf clocks ASIU clocks are a special case. These clocks are derived directly from the reference clock of the onboard crystal..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `reg`, `clocks`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
- `compatible`: enum `brcm,bcm63138-armpll`, `brcm,cygnus-armpll`, `brcm,cygnus-genpll`, `brcm,cygnus-lcpll0`, `brcm,cygnus-mipipll`, `brcm,cygnus-asiu-clk`, `brcm,cygnus-audiopll`, `brcm,hr2-armpll`, and 17 more.
- `reg`: minItems 1; 3 positional items.
- `clocks`: maxItems 1; The input parent clock phandle for the PLL / ASIU clock. For most iProc PLLs, this is an onboard crystal with a fixed rate..
- `#clock-cells` is allowed by the schema.
- `clock-output-names`: maxItems 45; minItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 3 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 417 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `brcm,bcm63138-armpll`, `brcm,cygnus-armpll`, `brcm,cygnus-genpll`, `brcm,cygnus-lcpll0`, `brcm,cygnus-mipipll`, `brcm,cygnus-asiu-clk`, `brcm,cygnus-audiopll`, `brcm,hr2-armpll`, `brcm,nsp-armpll`, `brcm,nsp-genpll`, `brcm,nsp-lcpll0`, `brcm,ns2-genpll-scr`, and 13 more, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,iproc-clocks.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,iproc-clocks.yaml -->
