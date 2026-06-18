# subset-b-000563 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll5-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll5-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll5-clk.yaml` is a Devicetree binding schema for `Allwinner A10 DRAM PLL`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun4i-a10-pll5-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The first output is the DRAM clock output, the second is meant for peripherals on the SoC.; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `allwinner,sun4i-a10-pll5-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`; The first output is the DRAM clock output, the second is meant for peripherals on the SoC..
- `clock-output-names`: maxItems 2.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 53 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun4i-a10-pll5-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll5-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll5-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll6-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll6-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll6-clk.yaml` is a Devicetree binding schema for `Allwinner A10 Peripheral PLL`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun4i-a10-pll6-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The first output is the SATA clock output, the second is the regular PLL output, the third is a PLL output at twice the rate.; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `allwinner,sun4i-a10-pll6-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`; The first output is the SATA clock output, the second is the regular PLL output, the third is a PLL output at twice the rate..
- `clock-output-names`: maxItems 3.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 53 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun4i-a10-pll6-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll6-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-pll6-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-tcon-ch0-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-tcon-ch0-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-tcon-ch0-clk.yaml` is a Devicetree binding schema for `Allwinner A10 TCON Channel 0 Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun4i-a10-tcon-ch0-clk`, `allwinner,sun4i-a10-tcon-ch1-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: enum `allwinner,sun4i-a10-tcon-ch0-clk`, `allwinner,sun4i-a10-tcon-ch1-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 4; The parent order must match the hardware programming order..
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 2 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 77 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `allwinner,sun4i-a10-tcon-ch0-clk`, `allwinner,sun4i-a10-tcon-ch1-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-tcon-ch0-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-tcon-ch0-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-usb-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-usb-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-usb-clk.yaml` is a Devicetree binding schema for `Allwinner A10 USB Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun4i-a10-usb-clk`, `allwinner,sun5i-a13-usb-clk`, `allwinner,sun6i-a31-usb-clk`, `allwinner,sun8i-a23-usb-clk`, `allwinner,sun8i-h3-usb-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The additional ID argument passed to the clock shall refer to the index of the output.; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: enum `allwinner,sun4i-a10-usb-clk`, `allwinner,sun5i-a13-usb-clk`, `allwinner,sun6i-a31-usb-clk`, `allwinner,sun8i-a23-usb-clk`, `allwinner,sun8i-h3-usb-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`; The additional ID argument passed to the clock shall refer to the index of the output..
- `clock-output-names`: maxItems 8; minItems 2.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 5 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 166 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `allwinner,sun4i-a10-usb-clk`, `allwinner,sun5i-a13-usb-clk`, `allwinner,sun6i-a31-usb-clk`, `allwinner,sun8i-a23-usb-clk`, `allwinner,sun8i-h3-usb-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-usb-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-usb-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-ve-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-ve-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-ve-clk.yaml` is a Devicetree binding schema for `Allwinner A10 Video Engine Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun4i-a10-ve-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `0`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: const `allwinner,sun4i-a10-ve-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.
- `#reset-cells`: const `0`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 55 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `allwinner,sun4i-a10-ve-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-ve-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun4i-a10-ve-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun55i-a523-ccu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun55i-a523-ccu.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun55i-a523-ccu.yaml` is a Devicetree binding schema for `Allwinner A523 Clock Control Unit`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun55i-a523-ccu`, `allwinner,sun55i-a523-mcu-ccu`, `allwinner,sun55i-a523-r-ccu`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: enum `allwinner,sun55i-a523-ccu`, `allwinner,sun55i-a523-mcu-ccu`, `allwinner,sun55i-a523-r-ccu`.
- `reg`: maxItems 1.
- `clocks`: maxItems 9; minItems 4.
- `clock-names`: maxItems 9; minItems 4.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 136 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `allwinner,sun55i-a523-ccu`, `allwinner,sun55i-a523-mcu-ccu`, `allwinner,sun55i-a523-r-ccu`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun55i-a523-ccu.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun55i-a523-ccu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun5i-a13-ahb-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun5i-a13-ahb-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun5i-a13-ahb-clk.yaml` is a Devicetree binding schema for `Allwinner A13 AHB Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun5i-a13-ahb-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `allwinner,sun5i-a13-ahb-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 3; The parent order must match the hardware programming order..
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 52 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun5i-a13-ahb-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun5i-a13-ahb-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun5i-a13-ahb-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun6i-a31-pll6-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun6i-a31-pll6-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun6i-a31-pll6-clk.yaml` is a Devicetree binding schema for `Allwinner A31 Peripheral PLL`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun6i-a31-pll6-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The first output is the regular PLL output, the second is a PLL output at twice the rate.; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `allwinner,sun6i-a31-pll6-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`; The first output is the regular PLL output, the second is a PLL output at twice the rate..
- `clock-output-names`: maxItems 2.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 53 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun6i-a31-pll6-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun6i-a31-pll6-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun6i-a31-pll6-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun7i-a20-gmac-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun7i-a20-gmac-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun7i-a20-gmac-clk.yaml` is a Devicetree binding schema for `Allwinner A20 GMAC TX Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun7i-a20-gmac-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `allwinner,sun7i-a20-gmac-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 2; The parent clocks shall be fixed rate dummy clocks at 25 MHz and 125 MHz, respectively..
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 51 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun7i-a20-gmac-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun7i-a20-gmac-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun7i-a20-gmac-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun7i-a20-out-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun7i-a20-out-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun7i-a20-out-clk.yaml` is a Devicetree binding schema for `Allwinner A20 Output Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun7i-a20-out-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `allwinner,sun7i-a20-out-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 3; The parent order must match the hardware programming order..
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 52 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun7i-a20-out-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun7i-a20-out-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun7i-a20-out-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun8i-a83t-de2-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun8i-a83t-de2-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun8i-a83t-de2-clk.yaml` is a Devicetree binding schema for `Allwinner A83t Display Engine 2/3 Clock Controller`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun8i-a83t-de2-clk`, `allwinner,sun8i-h3-de2-clk`, `allwinner,sun8i-v3s-de2-clk`, `allwinner,sun50i-a64-de2-clk`, `allwinner,sun50i-h5-de2-clk`, `allwinner,sun50i-h6-de3-clk`, `allwinner,sun50i-h616-de33-clk`, `allwinner,sun8i-r40-de2-clk`, `allwinner,sun20i-d1-de2-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `resets`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`, `resets`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: 9 oneOf alternatives.
- `reg`: maxItems 1.
- `clocks`: 2 positional items.
- `clock-names`: 2 positional items.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.
- `resets`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 80 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/sun8i-h3-ccu.h`, `dt-bindings/reset/sun8i-h3-ccu.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `allwinner,sun8i-a83t-de2-clk`, `allwinner,sun8i-h3-de2-clk`, `allwinner,sun8i-v3s-de2-clk`, `allwinner,sun50i-a64-de2-clk`, `allwinner,sun50i-h5-de2-clk`, `allwinner,sun50i-h6-de3-clk`, `allwinner,sun50i-h616-de33-clk`, `allwinner,sun8i-r40-de2-clk`, `allwinner,sun20i-d1-de2-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun8i-a83t-de2-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun8i-a83t-de2-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun8i-h3-bus-gates-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun8i-h3-bus-gates-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun8i-h3-bus-gates-clk.yaml` is a Devicetree binding schema for `Allwinner A10 Bus Gates Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun8i-h3-bus-gates-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-indices`, `clock-names`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `clock-output-names`, `clock-indices`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; This additional argument passed to that clock is the offset of the bit controlling this particular gate in the register.; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `allwinner,sun8i-h3-bus-gates-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 4.
- `clock-names`: maxItems 4; The parent order must match the hardware programming order..
- `#clock-cells`: const `1`; This additional argument passed to that clock is the offset of the bit controlling this particular gate in the register..
- `clock-output-names`: maxItems 64; minItems 1.
- `clock-indices`: maxItems 64; minItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 103 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun8i-h3-bus-gates-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun8i-h3-bus-gates-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun8i-h3-bus-gates-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-ahb-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-ahb-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-ahb-clk.yaml` is a Devicetree binding schema for `Allwinner A80 AHB Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun9i-a80-ahb-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `allwinner,sun9i-a80-ahb-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 4; The parent order must match the hardware programming order..
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 52 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun9i-a80-ahb-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-ahb-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-ahb-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-apb0-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-apb0-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-apb0-clk.yaml` is a Devicetree binding schema for `Allwinner A80 APB0 Bus Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun9i-a80-apb0-clk`, `allwinner,sun9i-a80-apb1-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `allwinner,sun9i-a80-apb0-clk`, `allwinner,sun9i-a80-apb1-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 2; The parent order must match the hardware programming order..
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 2 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 63 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun9i-a80-apb0-clk`, `allwinner,sun9i-a80-apb1-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-apb0-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-apb0-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-cpus-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-cpus-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-cpus-clk.yaml` is a Devicetree binding schema for `Allwinner A80 CPUS Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun9i-a80-cpus-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `allwinner,sun9i-a80-cpus-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 4; The parent order must match the hardware programming order..
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 52 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun9i-a80-cpus-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-cpus-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-cpus-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-de-clks.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-de-clks.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-de-clks.yaml` is a Devicetree binding schema for `Allwinner A80 Display Engine Clock Controller`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun9i-a80-de-clks`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`, `clock-names`, `resets`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`, `resets`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: const `allwinner,sun9i-a80-de-clks`.
- `reg`: maxItems 1.
- `clocks`: 3 positional items.
- `clock-names`: 3 positional items.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.
- `resets`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 67 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/sun9i-a80-ccu.h`, `dt-bindings/reset/sun9i-a80-ccu.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `allwinner,sun9i-a80-de-clks`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-de-clks.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-de-clks.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-gt-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-gt-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-gt-clk.yaml` is a Devicetree binding schema for `Allwinner A80 GT Bus Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun9i-a80-gt-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `allwinner,sun9i-a80-gt-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 4; The parent order must match the hardware programming order..
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 52 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun9i-a80-gt-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-gt-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-gt-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-mmc-config-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-mmc-config-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-mmc-config-clk.yaml` is a Devicetree binding schema for `Allwinner A80 MMC Configuration Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun9i-a80-mmc-config-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: There is one clock/reset output per mmc controller. The number of outputs is determined by the size of the address block, which is related to the overall mmc block.. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`, `#reset-cells`, `resets`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The additional ID argument passed to the clock shall refer to the index of the output.; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: const `allwinner,sun9i-a80-mmc-config-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`; The additional ID argument passed to the clock shall refer to the index of the output..
- `clock-output-names`: maxItems 4.
- `#reset-cells`: const `1`.
- `resets`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 68 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `allwinner,sun9i-a80-mmc-config-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-mmc-config-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-mmc-config-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-pll4-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-pll4-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-pll4-clk.yaml` is a Devicetree binding schema for `Allwinner A80 Peripheral PLL`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun9i-a80-pll4-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `allwinner,sun9i-a80-pll4-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 50 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `allwinner,sun9i-a80-pll4-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-pll4-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-pll4-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-clks.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-clks.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-clks.yaml` is a Devicetree binding schema for `Allwinner A80 USB Clock Controller`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun9i-a80-usb-clks`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: const `allwinner,sun9i-a80-usb-clks`.
- `reg`: maxItems 1.
- `clocks`: 2 positional items.
- `clock-names`: 2 positional items.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 59 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/sun9i-a80-ccu.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `allwinner,sun9i-a80-usb-clks`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-clks.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-clks.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-mod-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-mod-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-mod-clk.yaml` is a Devicetree binding schema for `Allwinner A80 USB Module Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun9i-a80-usb-mod-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The additional ID argument passed to the clock shall refer to the index of the output.; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: const `allwinner,sun9i-a80-usb-mod-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`; The additional ID argument passed to the clock shall refer to the index of the output..
- `clock-output-names`: maxItems 6.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 60 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `allwinner,sun9i-a80-usb-mod-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-mod-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-mod-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-phy-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-phy-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-phy-clk.yaml` is a Devicetree binding schema for `Allwinner A80 USB PHY Clock`. It documents and validates clock-provider nodes for Allwinner sunxi clock infrastructure, with compatible contract `allwinner,sun9i-a80-usb-phy-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The binding is marked deprecated, so new DTS files should prefer the replacement CCU or consolidated binding expected by the platform.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The additional ID argument passed to the clock shall refer to the index of the output.; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: const `allwinner,sun9i-a80-usb-phy-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`; The additional ID argument passed to the clock shall refer to the index of the output..
- `clock-output-names`: maxItems 6.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 60 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `allwinner,sun9i-a80-usb-phy-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- Deprecated bindings can remain necessary for legacy DTS compatibility, but new nodes risk review rejection or driver drift if they continue using the old compatible.
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-phy-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Legacy DTS users should remain covered so deprecation does not break old DTB compatibility.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/allwinner,sun9i-a80-usb-phy-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/alphascale,asm9260-clock-controller.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/alphascale,asm9260-clock-controller.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/alphascale,asm9260-clock-controller.yaml` is a Devicetree binding schema for `Alphascale Clock Controller`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `alphascale,asm9260-clock-controller`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The ACC (Alphascale Clock Controller) is responsible for choosing proper clock source, setting dividers and clock gates. Simple one-cell clock specifier format is used, where the only cell is used as an index of the clock inside the provider. It is encouraged to use dt-binding for clock index definitions. SoC specific dt-binding should be included to the device tree descriptor. For example Alphascale ASM9260: #includ.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `alphascale,asm9260-clock-controller`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 49 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/alphascale,asm9260.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `alphascale,asm9260-clock-controller`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/alphascale,asm9260-clock-controller.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/alphascale,asm9260-clock-controller.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,a1-peripherals-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,a1-peripherals-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,a1-peripherals-clkc.yaml` is a Devicetree binding schema for `Amlogic A1 Peripherals Clock Control Unit`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,a1-peripherals-clkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `reg`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `amlogic,a1-peripherals-clkc`.
- `reg`: maxItems 1.
- `clocks`: minItems 6; 7 positional items.
- `clock-names`: minItems 6; 7 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 78 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/amlogic,a1-pll-clkc.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `amlogic,a1-peripherals-clkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,a1-peripherals-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,a1-peripherals-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,a1-pll-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,a1-pll-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,a1-pll-clkc.yaml` is a Devicetree binding schema for `Amlogic A1 PLL Clock Control Unit`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,a1-pll-clkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `reg`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `amlogic,a1-pll-clkc`.
- `reg`: maxItems 1.
- `clocks`: minItems 2; 3 positional items.
- `clock-names`: minItems 2; 3 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 64 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/amlogic,a1-peripherals-clkc.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `amlogic,a1-pll-clkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,a1-pll-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,a1-pll-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,axg-audio-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,axg-audio-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,axg-audio-clkc.yaml` is a Devicetree binding schema for `Amlogic AXG Audio Clock Controller`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,axg-audio-clkc`, `amlogic,g12a-audio-clkc`, `amlogic,sm1-audio-clkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The Amlogic AXG audio clock controller generates and supplies clock to the other elements of the audio subsystem, such as fifos, i2s, spdif and pdm devices..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `reg`, `clocks`, `clock-names`, `resets`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`, `resets`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: enum `amlogic,axg-audio-clkc`, `amlogic,g12a-audio-clkc`, `amlogic,sm1-audio-clkc`.
- `reg`: maxItems 1.
- `clocks`: minItems 1; 29 positional items.
- `clock-names`: minItems 1; 29 positional items.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.
- `resets`: internal reset line.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 201 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/axg-clkc.h`, `dt-bindings/reset/amlogic,meson-axg-reset.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `amlogic,axg-audio-clkc`, `amlogic,g12a-audio-clkc`, `amlogic,sm1-audio-clkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,axg-audio-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,axg-audio-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,c3-peripherals-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,c3-peripherals-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,c3-peripherals-clkc.yaml` is a Devicetree binding schema for `Amlogic C3 series Peripheral Clock Controller`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,c3-peripherals-clkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `amlogic,c3-peripherals-clkc`.
- `reg`: maxItems 1.
- `clocks`: minItems 16; 17 positional items.
- `clock-names`: minItems 16; 17 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 120 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `amlogic,c3-peripherals-clkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,c3-peripherals-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,c3-peripherals-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,c3-pll-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,c3-pll-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,c3-pll-clkc.yaml` is a Devicetree binding schema for `Amlogic C3 series PLL Clock Controller`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,c3-pll-clkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `amlogic,c3-pll-clkc`.
- `reg`: maxItems 1.
- `clocks`: 3 positional items.
- `clock-names`: 3 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 62 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `amlogic,c3-pll-clkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,c3-pll-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,c3-pll-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,gxbb-aoclkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,gxbb-aoclkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,gxbb-aoclkc.yaml` is a Devicetree binding schema for `Amlogic Always-On Clock Controller`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,meson-gxbb-aoclkc`, `amlogic,meson-gxl-aoclkc`, `amlogic,meson-gxm-aoclkc`, `amlogic,meson-axg-aoclkc`, `amlogic,meson-gx-aoclkc`, `amlogic,meson-g12a-aoclkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`. Important properties include `compatible`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: 2 oneOf alternatives.
- `clocks`: maxItems 5; minItems 2.
- `clock-names`: minItems 2; 5 positional items.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 85 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `amlogic,meson-gxbb-aoclkc`, `amlogic,meson-gxl-aoclkc`, `amlogic,meson-gxm-aoclkc`, `amlogic,meson-axg-aoclkc`, `amlogic,meson-gx-aoclkc`, `amlogic,meson-g12a-aoclkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,gxbb-aoclkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,gxbb-aoclkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,gxbb-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,gxbb-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,gxbb-clkc.yaml` is a Devicetree binding schema for `Amlogic Clock Controller`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,gxbb-clkc`, `amlogic,gxl-clkc`, `amlogic,axg-clkc`, `amlogic,g12a-clkc`, `amlogic,g12b-clkc`, `amlogic,sm1-clkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `amlogic,gxbb-clkc`, `amlogic,gxl-clkc`, `amlogic,axg-clkc`, `amlogic,g12a-clkc`, `amlogic,g12b-clkc`, `amlogic,sm1-clkc`.
- `clocks`: maxItems 1.
- `clock-names`: const `xtal`.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 37 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `amlogic,gxbb-clkc`, `amlogic,gxl-clkc`, `amlogic,axg-clkc`, `amlogic,g12a-clkc`, `amlogic,g12b-clkc`, `amlogic,sm1-clkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,gxbb-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,gxbb-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,meson8-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,meson8-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,meson8-clkc.yaml` is a Devicetree binding schema for `Amlogic Meson8, Meson8b and Meson8m2 Clock and Reset Controller`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,meson8-clkc`, `amlogic,meson8b-clkc`, `amlogic,meson8m2-clkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `clocks`, `clock-names`, `#reset-cells`. Important properties include `compatible`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: 2 oneOf alternatives.
- `clocks`: maxItems 3; minItems 2.
- `clock-names`: minItems 2; 3 positional items.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 45 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `amlogic,meson8-clkc`, `amlogic,meson8b-clkc`, `amlogic,meson8m2-clkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,meson8-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,meson8-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,meson8-ddr-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,meson8-ddr-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,meson8-ddr-clkc.yaml` is a Devicetree binding schema for `Amlogic DDR Clock Controller`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,meson8-ddr-clkc`, `amlogic,meson8b-ddr-clkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `amlogic,meson8-ddr-clkc`, `amlogic,meson8b-ddr-clkc`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `clock-names`: 1 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 50 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `amlogic,meson8-ddr-clkc`, `amlogic,meson8b-ddr-clkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,meson8-ddr-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,meson8-ddr-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,s4-peripherals-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,s4-peripherals-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,s4-peripherals-clkc.yaml` is a Devicetree binding schema for `Amlogic S4 Peripherals Clock Controller`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,s4-peripherals-clkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `amlogic,s4-peripherals-clkc`.
- `reg`: maxItems 1.
- `clocks`: minItems 14; 15 positional items.
- `clock-names`: minItems 14; 15 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 96 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/amlogic,s4-peripherals-clkc.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `amlogic,s4-peripherals-clkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,s4-peripherals-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,s4-peripherals-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,s4-pll-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,s4-pll-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,s4-pll-clkc.yaml` is a Devicetree binding schema for `Amlogic S4 PLL Clock Controller`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,s4-pll-clkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `amlogic,s4-pll-clkc`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `clock-names`: 1 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 49 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `amlogic,s4-pll-clkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,s4-pll-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,s4-pll-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,t7-peripherals-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,t7-peripherals-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,t7-peripherals-clkc.yaml` is a Devicetree binding schema for `Amlogic T7 Peripherals Clock Controller`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,t7-peripherals-clkc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `reg`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `amlogic,t7-peripherals-clkc`.
- `reg`: maxItems 1.
- `clocks`: minItems 14; 17 positional items.
- `clock-names`: minItems 14; 17 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 116 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `amlogic,t7-peripherals-clkc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,t7-peripherals-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,t7-peripherals-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,t7-pll-clkc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,t7-pll-clkc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,t7-pll-clkc.yaml` is a Devicetree binding schema for `Amlogic T7 PLL Clock Control Controller`. It documents and validates clock-provider nodes for Amlogic Meson clock infrastructure, with compatible contract `amlogic,t7-gp0-pll`, `amlogic,t7-gp1-pll`, `amlogic,t7-hifi-pll`, `amlogic,t7-pcie-pll`, `amlogic,t7-mpll`, `amlogic,t7-hdmi-pll`, `amlogic,t7-mclk-pll`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `reg`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `amlogic,t7-gp0-pll`, `amlogic,t7-gp1-pll`, `amlogic,t7-hifi-pll`, `amlogic,t7-pcie-pll`, `amlogic,t7-mpll`, `amlogic,t7-hdmi-pll`, `amlogic,t7-mclk-pll`.
- `reg`: maxItems 1.
- `clocks`: minItems 1; 3 positional items.
- `clock-names`: minItems 1; 3 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 114 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `amlogic,t7-gp0-pll`, `amlogic,t7-gp1-pll`, `amlogic,t7-hifi-pll`, `amlogic,t7-pcie-pll`, `amlogic,t7-mpll`, `amlogic,t7-hdmi-pll`, `amlogic,t7-mclk-pll`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,t7-pll-clkc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/amlogic,t7-pll-clkc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apm,xgene-device-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apm,xgene-device-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apm,xgene-device-clock.yaml` is a Devicetree binding schema for `APM X-Gene SoC device clocks`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `apm,xgene-device-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `clock-output-names`, `reg-names`, `csr-offset`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `apm,xgene-device-clock`.
- `reg`: maxItems 2; minItems 1.
- `clocks`: maxItems 1.
- `clock-names`: maxItems 1.
- `#clock-cells`: const `1`.
- `clock-output-names`: maxItems 1.
- `reg-names`: minItems 1; 2 positional items.
- `csr-offset`: Offset to the CSR reset register; ref `/schemas/types.yaml#/definitions/uint32`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 80 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/types.yaml#/definitions/uint32`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `apm,xgene-device-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apm,xgene-device-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apm,xgene-device-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apm,xgene-socpll-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apm,xgene-socpll-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apm,xgene-socpll-clock.yaml` is a Devicetree binding schema for `APM X-Gene SoC PLL, PCPPLL, and PMD clocks`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `apm,xgene-pcppll-clock`, `apm,xgene-pcppll-v2-clock`, `apm,xgene-pmd-clock`, `apm,xgene-socpll-clock`, `apm,xgene-socpll-v2-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `clock-output-names`, `reg-names`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 1 positional items.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `clock-names`: enum `pcppll`, `socpll`.
- `#clock-cells`: const `1`.
- `clock-output-names`: maxItems 1.
- `reg-names`: minItems 1; 2 positional items.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 50 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `apm,xgene-pcppll-clock`, `apm,xgene-pcppll-v2-clock`, `apm,xgene-pmd-clock`, `apm,xgene-socpll-clock`, `apm,xgene-socpll-v2-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apm,xgene-socpll-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/apm,xgene-socpll-clock.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/arm,syscon-icst.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/arm,syscon-icst.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/arm,syscon-icst.yaml` is a Devicetree binding schema for `ARM System Controller ICST Clocks`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `arm,syscon-icst525`, `arm,syscon-icst307`, `arm,syscon-icst525-integratorap-cm`, `arm,syscon-icst525-integratorap-sys`, `arm,syscon-icst525-integratorap-pci`, `arm,syscon-icst525-integratorcp-cm-core`, `arm,syscon-icst525-integratorcp-cm-mem`, `arm,integrator-cm-auxosc`, `arm,versatile-cm-auxosc`, `arm,impd1-vco1`, `arm,impd1-vco2`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The ICS525 and ICS307 oscillators are produced by Integrated Devices Technology (IDT). ARM integrated these oscillators deeply into their reference designs by adding special control registers that manage such oscillators to their system controllers. The various ARM system controllers contain logic to serialize and initialize an ICST clock request after a write to the 32 bit register at an offset into the system contr.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `clocks`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`, `lock-offset`, `vco-offset`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `arm,syscon-icst525`, `arm,syscon-icst307`, `arm,syscon-icst525-integratorap-cm`, `arm,syscon-icst525-integratorap-sys`, `arm,syscon-icst525-integratorap-pci`, `arm,syscon-icst525-integratorcp-cm-core`, `arm,syscon-icst525-integratorcp-cm-mem`, `arm,integrator-cm-auxosc`, and 3 more.
- `reg`: maxItems 1; The VCO register.
- `clocks`: maxItems 1; Parent clock for the ICST VCO.
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.
- `lock-offset`: Offset to the unlocking register for the oscillator; ref `/schemas/types.yaml#/definitions/uint32`.
- `vco-offset`: Offset to the VCO register for the oscillator; ref `/schemas/types.yaml#/definitions/uint32`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 110 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/types.yaml#/definitions/uint32`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `arm,syscon-icst525`, `arm,syscon-icst307`, `arm,syscon-icst525-integratorap-cm`, `arm,syscon-icst525-integratorap-sys`, `arm,syscon-icst525-integratorap-pci`, `arm,syscon-icst525-integratorcp-cm-core`, `arm,syscon-icst525-integratorcp-cm-mem`, `arm,integrator-cm-auxosc`, `arm,versatile-cm-auxosc`, `arm,impd1-vco1`, `arm,impd1-vco2`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/arm,syscon-icst.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/arm,syscon-icst.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/atmel,at91rm9200-pmc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/atmel,at91rm9200-pmc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/atmel,at91rm9200-pmc.yaml` is a Devicetree binding schema for `Atmel Power Management Controller (PMC)`. It documents and validates clock-provider nodes for Atmel/Microchip clock infrastructure, with compatible contract `atmel,at91sam9g20-pmc`, `atmel,at91sam9260-pmc`, `syscon`, `atmel,at91sam9g15-pmc`, `atmel,at91sam9g25-pmc`, `atmel,at91sam9g35-pmc`, `atmel,at91sam9x25-pmc`, `atmel,at91sam9x35-pmc`, `atmel,at91sam9x5-pmc`, `atmel,at91rm9200-pmc`, `atmel,at91sam9261-pmc`, `atmel,at91sam9263-pmc`, and 10 more. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The power management controller optimizes power consumption by controlling all system and user peripheral clocks. The PMC enables/disables the clock inputs to many of the peripherals and to the processor..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `#clock-cells`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `interrupts`, `atmel,osc-bypass`.
`#clock-cells` is constrained as `#clock-cells`: const `2`; - 1st cell is the clock type, one of PMC_TYPE_CORE, PMC_TYPE_SYSTEM, PMC_TYPE_PERIPHERAL, PMC_TYPE_GCK, PMC_TYPE_PROGRAMMABLE (as defined in <dt-bindings/clock/at91.h>) - 2nd cell is the clock identifier as defined in <d; this defines how consumers encode clock phandle specifiers.
- `compatible`: 3 oneOf alternatives.
- `reg`: maxItems 1.
- `clocks`: maxItems 3; minItems 2.
- `clock-names`: maxItems 3; minItems 2.
- `#clock-cells`: const `2`; - 1st cell is the clock type, one of PMC_TYPE_CORE, PMC_TYPE_SYSTEM, PMC_TYPE_PERIPHERAL, PMC_TYPE_GCK, PMC_TYPE_PROGRAMMABLE (as defined in <dt-bindings/clock/at91.h>) - 2nd cell is the clock identifier as defined in <d.
- `interrupts`: maxItems 1.
- `atmel,osc-bypass`: set when a clock signal is directly provided on XIN.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 162 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/at91.h`, `dt-bindings/clock/at91.h
        (for core clocks) or as defined in datasheet (for system, peripheral,
        gck and programmable clocks).
    const: 2

  clocks:
    minItems: 2
    maxItems: 3

  clock-names:
    minItems: 2
    maxItems: 3

  atmel,osc-bypass:
    description: set when a clock signal is directly provided on XIN
    type: boolean

required:
  - compatible
  - reg
  - interrupts
  - "#clock-cells"
  - clocks
  - clock-names

allOf:
  - if:
      properties:
        compatible:
          contains:
            enum:
              - microchip,sam9x60-pmc
              - microchip,sam9x7-pmc
              - microchip,sama7d65-pmc
              - microchip,sama7g5-pmc
    then:
      properties:
        clocks:
          minItems: 3
          maxItems: 3
        clock-names:
          items:
            - const: td_slck
            - const: md_slck
            - const: main_xtal

  - if:
      properties:
        compatible:
          contains:
            enum:
              - atmel,at91rm9200-pmc
              - atmel,at91sam9260-pmc
              - atmel,at91sam9261-pmc
              - atmel,at91sam9263-pmc
              - atmel,at91sam9g20-pmc
    then:
      properties:
        clocks:
          minItems: 2
          maxItems: 2
        clock-names:
          items:
            - const: slow_xtal
            - const: main_xtal

  - if:
      properties:
        compatible:
          contains:
            enum:
              - atmel,sama5d2-pmc
              - atmel,sama5d3-pmc
              - atmel,sama5d4-pmc
    then:
      properties:
        clocks:
          minItems: 2
          maxItems: 2
        clock-names:
          items:
            - const: slow_clk
            - const: main_xtal

additionalProperties: false

examples:
  - |
    #include <dt-bindings/interrupt-controller/irq.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `atmel,at91sam9g20-pmc`, `atmel,at91sam9260-pmc`, `syscon`, `atmel,at91sam9g15-pmc`, `atmel,at91sam9g25-pmc`, `atmel,at91sam9g35-pmc`, `atmel,at91sam9x25-pmc`, `atmel,at91sam9x35-pmc`, `atmel,at91sam9x5-pmc`, `atmel,at91rm9200-pmc`, `atmel,at91sam9261-pmc`, `atmel,at91sam9263-pmc`, and 10 more, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/atmel,at91rm9200-pmc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/atmel,at91rm9200-pmc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/atmel,at91sam9x5-sckc.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/atmel,at91sam9x5-sckc.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/atmel,at91sam9x5-sckc.yaml` is a Devicetree binding schema for `Atmel Slow Clock Controller (SCKC)`. It documents and validates clock-provider nodes for Atmel/Microchip clock infrastructure, with compatible contract `atmel,at91sam9x5-sckc`, `atmel,sama5d3-sckc`, `atmel,sama5d4-sckc`, `microchip,sam9x60-sckc`, `microchip,sam9x7-sckc`, `microchip,sama7d65-sckc`, `microchip,sama7g5-sckc`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `atmel,osc-bypass`.
`#clock-cells` is constrained as `#clock-cells`: enum `0`, `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 2 oneOf alternatives.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: enum `0`, `1`.
- `atmel,osc-bypass`: set when a clock signal is directly provided on XIN.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 73 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `atmel,at91sam9x5-sckc`, `atmel,sama5d3-sckc`, `atmel,sama5d4-sckc`, `microchip,sam9x60-sckc`, `microchip,sam9x7-sckc`, `microchip,sama7d65-sckc`, `microchip,sama7g5-sckc`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/atmel,at91sam9x5-sckc.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/atmel,at91sam9x5-sckc.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec6-clkctrl.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec6-clkctrl.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec6-clkctrl.yaml` is a Devicetree binding schema for `Axis ARTPEC-6 clock controller`. It documents and validates clock-provider nodes for Axis ARTPEC clock infrastructure, with compatible contract `axis,artpec6-clkctrl`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `axis,artpec6-clkctrl`.
- `reg`: maxItems 1.
- `clocks`: minItems 1; 4 positional items.
- `clock-names`: minItems 1; 4 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 55 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `axis,artpec6-clkctrl`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec6-clkctrl.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec6-clkctrl.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec8-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec8-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec8-clock.yaml` is a Devicetree binding schema for `Axis ARTPEC-8 SoC clock controller`. It documents and validates clock-provider nodes for Axis ARTPEC clock infrastructure, with compatible contract `axis,artpec8-cmu-cmu`, `axis,artpec8-cmu-bus`, `axis,artpec8-cmu-core`, `axis,artpec8-cmu-cpucl`, `axis,artpec8-cmu-fsys`, `axis,artpec8-cmu-imem`, `axis,artpec8-cmu-peri`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: ARTPEC-8 clock controller is comprised of several CMU (Clock Management Unit) units, generating clocks for different domains. Those CMU units are modeled as separate device tree nodes, and might depend on each other. The root clock in that root tree is an external clock: OSCCLK (25 MHz). This external clock must be defined as a fixed-rate clock in dts. CMU_CMU is a top-level CMU, where all base clocks are prepared us.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `axis,artpec8-cmu-cmu`, `axis,artpec8-cmu-bus`, `axis,artpec8-cmu-core`, `axis,artpec8-cmu-cpucl`, `axis,artpec8-cmu-fsys`, `axis,artpec8-cmu-imem`, `axis,artpec8-cmu-peri`.
- `reg`: maxItems 1.
- `clocks`: maxItems 5; minItems 1.
- `clock-names`: maxItems 5; minItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 213 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/axis,artpec8-clk.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `axis,artpec8-cmu-cmu`, `axis,artpec8-cmu-bus`, `axis,artpec8-cmu-core`, `axis,artpec8-cmu-cpucl`, `axis,artpec8-cmu-fsys`, `axis,artpec8-cmu-imem`, `axis,artpec8-cmu-peri`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec8-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec8-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec9-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec9-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec9-clock.yaml` is a Devicetree binding schema for `Axis ARTPEC-9 SoC clock controller`. It documents and validates clock-provider nodes for Axis ARTPEC clock infrastructure, with compatible contract `axis,artpec9-cmu-cmu`, `axis,artpec9-cmu-bus`, `axis,artpec9-cmu-core`, `axis,artpec9-cmu-cpucl`, `axis,artpec9-cmu-fsys0`, `axis,artpec9-cmu-fsys1`, `axis,artpec9-cmu-imem`, `axis,artpec9-cmu-peri`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: ARTPEC-9 clock controller is comprised of several CMU (Clock Management Unit) units, generating clocks for different domains. Those CMU units are modeled as separate device tree nodes, and might depend on each other. The root clock in that root tree is an external clock: OSCCLK (25 MHz). This external clock must be defined as a fixed-rate clock in dts. CMU_CMU is a top-level CMU, where all base clocks are prepared us.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `axis,artpec9-cmu-cmu`, `axis,artpec9-cmu-bus`, `axis,artpec9-cmu-core`, `axis,artpec9-cmu-cpucl`, `axis,artpec9-cmu-fsys0`, `axis,artpec9-cmu-fsys1`, `axis,artpec9-cmu-imem`, `axis,artpec9-cmu-peri`.
- `reg`: maxItems 1.
- `clocks`: maxItems 5; minItems 1.
- `clock-names`: maxItems 5; minItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 232 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/axis,artpec9-clk.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `axis,artpec9-cmu-cmu`, `axis,artpec9-cmu-bus`, `axis,artpec9-cmu-core`, `axis,artpec9-cmu-cpucl`, `axis,artpec9-cmu-fsys0`, `axis,artpec9-cmu-fsys1`, `axis,artpec9-cmu-imem`, `axis,artpec9-cmu-peri`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec9-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/axis,artpec9-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/bitmain,bm1880-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/bitmain,bm1880-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/bitmain,bm1880-clk.yaml` is a Devicetree binding schema for `Bitmain BM1880 Clock Controller`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `bitmain,bm1880-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The Bitmain BM1880 clock controller generates and supplies clock to various peripherals within the SoC. This binding uses common clock bindings [1] Documentation/devicetree/bindings/clock/clock-bindings.txt.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `reg-names`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `reg-names`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `bitmain,bm1880-clk`.
- `reg`: 2 positional items.
- `clocks`: maxItems 1.
- `clock-names`: const `osc`.
- `#clock-cells`: const `1`.
- `reg-names`: 2 positional items.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 64 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `bitmain,bm1880-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/bitmain,bm1880-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/bitmain,bm1880-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2711-dvp.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2711-dvp.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2711-dvp.yaml` is a Devicetree binding schema for `Broadcom BCM2711 HDMI DVP`. It documents and validates clock-provider nodes for Broadcom clock infrastructure, with compatible contract `brcm,brcm2711-dvp`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `#reset-cells`, `compatible`, `reg`, `clocks`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: const `brcm,brcm2711-dvp`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 47 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `brcm,brcm2711-dvp`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2711-dvp.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2711-dvp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2835-aux-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2835-aux-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2835-aux-clock.yaml` is a Devicetree binding schema for `Broadcom BCM2835 auxiliary peripheral clock`. It documents and validates clock-provider nodes for Broadcom clock infrastructure, with compatible contract `brcm,bcm2835-aux`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The auxiliary peripherals (UART, SPI1, and SPI2) have a small register area controlling clock gating to the peripherals, and providing an IRQ status register..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`, `clocks`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `brcm,bcm2835-aux`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 47 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/bcm2835.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `brcm,bcm2835-aux`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2835-aux-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm2835-aux-clock.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm53573-ilp.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm53573-ilp.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm53573-ilp.yaml` is a Devicetree binding schema for `Broadcom BCM53573 ILP clock`. It documents and validates clock-provider nodes for Broadcom clock infrastructure, with compatible contract `brcm,bcm53573-ilp`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: ILP clock (sometimes referred as "slow clock") on Broadcom BCM53573 devices using Cortex-A7 CPU. ILP's rate has to be calculated on runtime and it depends on ALP clock which has to be referenced. This clock is part of PMU (Power Management Unit), a Broadcom device handling power-related aspects. Its node must be sub-node of the PMU device..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are no explicit required-property list. Important properties include `compatible`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 1 positional items.
- `clocks`: maxItems 1.
- `#clock-cells`: const `0`.
- `clock-output-names`: 1 positional items.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 46 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `brcm,bcm53573-ilp`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm53573-ilp.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm53573-ilp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm63268-timer-clocks.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm63268-timer-clocks.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm63268-timer-clocks.yaml` is a Devicetree binding schema for `Broadcom BCM63268 Timer Clock and Reset`. It documents and validates clock-provider nodes for Broadcom clock infrastructure, with compatible contract `brcm,bcm63268-timer-clocks`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`, `#reset-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: const `brcm,bcm63268-timer-clocks`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 40 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `brcm,bcm63268-timer-clocks`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm63268-timer-clocks.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm63268-timer-clocks.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm63xx-clocks.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm63xx-clocks.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm63xx-clocks.yaml` is a Devicetree binding schema for `MIPS based BCM63XX SoCs Gated Clock Controller`. It documents and validates clock-provider nodes for Broadcom clock infrastructure, with compatible contract `brcm,bcm3368-clocks`, `brcm,bcm6318-clocks`, `brcm,bcm6318-ubus-clocks`, `brcm,bcm6328-clocks`, `brcm,bcm6358-clocks`, `brcm,bcm6362-clocks`, `brcm,bcm6368-clocks`, `brcm,bcm63268-clocks`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `brcm,bcm3368-clocks`, `brcm,bcm6318-clocks`, `brcm,bcm6318-ubus-clocks`, `brcm,bcm6328-clocks`, `brcm,bcm6358-clocks`, `brcm,bcm6362-clocks`, `brcm,bcm6368-clocks`, `brcm,bcm63268-clocks`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 44 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `brcm,bcm3368-clocks`, `brcm,bcm6318-clocks`, `brcm,bcm6318-ubus-clocks`, `brcm,bcm6328-clocks`, `brcm,bcm6358-clocks`, `brcm,bcm6362-clocks`, `brcm,bcm6368-clocks`, `brcm,bcm63268-clocks`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm63xx-clocks.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,bcm63xx-clocks.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,kona-ccu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,kona-ccu.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,kona-ccu.yaml` is a Devicetree binding schema for `Broadcom Kona family clock control units (CCU)`. It documents and validates clock-provider nodes for Broadcom clock infrastructure, with compatible contract `brcm,bcm11351-aon-ccu`, `brcm,bcm11351-hub-ccu`, `brcm,bcm11351-master-ccu`, `brcm,bcm11351-root-ccu`, `brcm,bcm11351-slave-ccu`, `brcm,bcm21664-aon-ccu`, `brcm,bcm21664-master-ccu`, `brcm,bcm21664-root-ccu`, `brcm,bcm21664-slave-ccu`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Broadcom "Kona" style clock control unit (CCU) is a clock provider that manages a set of clock signals. All available clock IDs are defined in - include/dt-bindings/clock/bcm281xx.h for BCM281XX family - include/dt-bindings/clock/bcm21664.h for BCM21664 family.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`, `clock-output-names`. Important properties include `compatible`, `reg`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `brcm,bcm11351-aon-ccu`, `brcm,bcm11351-hub-ccu`, `brcm,bcm11351-master-ccu`, `brcm,bcm11351-root-ccu`, `brcm,bcm11351-slave-ccu`, `brcm,bcm21664-aon-ccu`, `brcm,bcm21664-master-ccu`, `brcm,bcm21664-root-ccu`, and 1 more.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `clock-output-names`: maxItems 10; minItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 181 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `brcm,bcm11351-aon-ccu`, `brcm,bcm11351-hub-ccu`, `brcm,bcm11351-master-ccu`, `brcm,bcm11351-root-ccu`, `brcm,bcm11351-slave-ccu`, `brcm,bcm21664-aon-ccu`, `brcm,bcm21664-master-ccu`, `brcm,bcm21664-root-ccu`, `brcm,bcm21664-slave-ccu`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,kona-ccu.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/brcm,kona-ccu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/calxeda.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/calxeda.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/calxeda.yaml` is a Devicetree binding schema for `Calxeda highbank platform Clock Controller`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `calxeda,hb-pll-clock`, `calxeda,hb-a9periph-clock`, `calxeda,hb-a9bus-clock`, `calxeda,hb-emmc-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: This binding covers the Calxeda SoC internal peripheral and bus clocks as used by peripherals. The clocks live inside the "system register" region of the SoC, so are typically presented as children of an "hb-sregs" node..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `clocks`, `reg`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `calxeda,hb-pll-clock`, `calxeda,hb-a9periph-clock`, `calxeda,hb-a9bus-clock`, `calxeda,hb-emmc-clock`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `0`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 82 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `calxeda,hb-pll-clock`, `calxeda,hb-a9periph-clock`, `calxeda,hb-a9bus-clock`, `calxeda,hb-emmc-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/calxeda.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/calxeda.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/canaan,k210-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/canaan,k210-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/canaan,k210-clk.yaml` is a Devicetree binding schema for `Canaan Kendryte K210 Clock`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `canaan,k210-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Canaan Kendryte K210 SoC clocks driver bindings. The clock controller node must be defined as a child node of the K210 system controller node. See also: - dt-bindings/clock/k210-clk.h.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `clocks`. Important properties include `compatible`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `canaan,k210-clk`.
- `clocks`: maxItems 1; Phandle of the SoC 26MHz fixed-rate oscillator clock..
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 55 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/k210-clk.h`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `canaan,k210-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/canaan,k210-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/canaan,k210-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,cs2000-cp.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,cs2000-cp.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,cs2000-cp.yaml` is a Devicetree binding schema for `CIRRUS LOGIC Fractional-N Clock Synthesizer & Clock Multiplier`. It documents and validates clock-provider nodes for Cirrus clock infrastructure, with compatible contract `cirrus,cs2000-cp`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The CS2000-CP is an extremely versatile system clocking device that utilizes a programmable phase lock loop. Link: https://www.cirrus.com/products/cs2000/.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `cirrus,aux-output-source`, `cirrus,clock-skip`, `cirrus,dynamic-mode`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `cirrus,cs2000-cp`.
- `reg`: maxItems 1.
- `clocks`: maxItems 2; Common clock binding for CLK_IN, XTI/REF_CLK.
- `clock-names`: 2 positional items.
- `#clock-cells`: const `0`.
- `cirrus,aux-output-source`: enum `0`, `1`, `2`, `3`; Specifies the function of the auxiliary clock output pin; ref `/schemas/types.yaml#/definitions/uint32`.
- `cirrus,clock-skip`: This mode allows the PLL to maintain lock even when CLK_IN has missing pulses for up to 20 ms.; ref `/schemas/types.yaml#/definitions/flag`.
- `cirrus,dynamic-mode`: In dynamic mode, the CLK_IN input is used to drive the digital PLL of the silicon. If not given, the static mode shall be used to derive the output signal directly from the REF_CLK input.; ref `/schemas/types.yaml#/definitions/flag`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 90 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/flag`, DTS examples or descriptions reference `dt-bindings/clock/cirrus,cs2000-cp.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `cirrus,cs2000-cp`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,cs2000-cp.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,cs2000-cp.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,ep7209-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,ep7209-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,ep7209-clk.yaml` is a Devicetree binding schema for `Cirrus Logic CLPS711X Clock Controller`. It documents and validates clock-provider nodes for Cirrus clock infrastructure, with compatible contract `cirrus,ep7312-clk`, `cirrus,ep7209-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: See include/dt-bindings/clock/clps711x-clock.h for the full list of CLPS711X clock IDs..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `startup-frequency`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `startup-frequency`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 2 positional items.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `startup-frequency`: Factory set CPU startup frequency in HZ.; ref `/schemas/types.yaml#/definitions/uint32`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 47 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/types.yaml#/definitions/uint32`, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `cirrus,ep7312-clk`, `cirrus,ep7209-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,ep7209-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,ep7209-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,lochnagar.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,lochnagar.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,lochnagar.yaml` is a Devicetree binding schema for `Cirrus Logic Lochnagar Audio Development Board`. It documents and validates clock-provider nodes for Cirrus clock infrastructure, with compatible contract `cirrus,lochnagar1-clk`, `cirrus,lochnagar2-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Lochnagar is an evaluation and development board for Cirrus Logic Smart CODEC and Amp devices. It allows the connection of most Cirrus Logic devices on mini-cards, as well as allowing connection of various application processor systems to provide a full evaluation platform. Audio system topology, clocking and power can all be controlled through the Lochnagar, allowing the device under test to be used in a variety of .

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`. Important properties include `compatible`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The first cell indicates the clock number, see [2] for available clocks and [1].; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `cirrus,lochnagar1-clk`, `cirrus,lochnagar2-clk`.
- `clocks`: maxItems 19; minItems 1.
- `clock-names`: maxItems 19; minItems 1.
- `#clock-cells`: const `1`; The first cell indicates the clock number, see [2] for available clocks and [1]..

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 78 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `cirrus,lochnagar1-clk`, `cirrus,lochnagar2-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,lochnagar.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/cirrus,lochnagar.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/eswin,eic7700-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/eswin,eic7700-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/eswin,eic7700-clock.yaml` is a Devicetree binding schema for `Eswin EIC7700 SoC clock controller`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `eswin,eic7700-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock controller generates and supplies clock to all the modules for eic7700 SoC..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `eswin,eic7700-clock`.
- `reg`: maxItems 1.
- `clocks`: 1 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 46 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `eswin,eic7700-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/eswin,eic7700-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/eswin,eic7700-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-clock.yaml` is a Devicetree binding schema for `Simple fixed-rate clock sources`. It documents and validates clock-provider nodes for generic fixed clock provider infrastructure, with compatible contract `fixed-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `clock-frequency`. Important properties include `compatible`, `#clock-cells`, `clock-output-names`, `clock-frequency`, `$nodename`, `clock-accuracy`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fixed-clock`.
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.
- `clock-frequency` is allowed by the schema.
- `$nodename`: 2 anyOf alternatives.
- `clock-accuracy`: accuracy of clock in ppb (parts per billion).; ref `/schemas/types.yaml#/definitions/uint32`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 53 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
For fixed-rate style nodes, `clock-frequency` becomes persistent board data that the fixed-clock provider uses directly instead of deriving a rate from hardware registers.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/types.yaml#/definitions/uint32`.

### Integration Points
Integration is through compatible matching for `fixed-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-factor-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-factor-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-factor-clock.yaml` is a Devicetree binding schema for `Simple fixed factor rate clock sources`. It documents and validates clock-provider nodes for generic fixed clock provider infrastructure, with compatible contract `fixed-factor-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `clocks`, `#clock-cells`, `clock-div`, `clock-mult`. Important properties include `compatible`, `clocks`, `#clock-cells`, `clock-output-names`, `clock-mult`, `clock-div`, `$nodename`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `fixed-factor-clock`.
- `clocks`: maxItems 1.
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.
- `clock-mult`: Fixed multiplier; ref `/schemas/types.yaml#/definitions/uint32`.
- `clock-div`: Fixed divider; ref `/schemas/types.yaml#/definitions/uint32`.
- `$nodename`: 2 anyOf alternatives.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 63 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/types.yaml#/definitions/uint32`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fixed-factor-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-factor-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-factor-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-mmio-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-mmio-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-mmio-clock.yaml` is a Devicetree binding schema for `Simple memory mapped IO fixed-rate clock sources`. It documents and validates clock-provider nodes for generic fixed clock provider infrastructure, with compatible contract `fixed-mmio-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: This binding describes a fixed-rate clock for which the frequency can be read from a single 32-bit memory mapped I/O register. It was designed for test systems, like FPGA, not for complete, finished SoCs..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fixed-mmio-clock`.
- `reg`: maxItems 1.
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 47 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fixed-mmio-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-mmio-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fixed-mmio-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,flexspi-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,flexspi-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,flexspi-clock.yaml` is a Devicetree binding schema for `Freescale FlexSPI clock driver for Layerscape SoCs`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,ls1028a-flexspi-clk`, `fsl,lx2160a-flexspi-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The Freescale Layerscape SoCs have a special FlexSPI clock which is derived from the platform PLL..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `fsl,ls1028a-flexspi-clk`, `fsl,lx2160a-flexspi-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 55 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,ls1028a-flexspi-clk`, `fsl,lx2160a-flexspi-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,flexspi-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,flexspi-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8-acm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8-acm.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8-acm.yaml` is a Devicetree binding schema for `NXP i.MX8 Audio Clock Mux`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx8dxl-acm`, `fsl,imx8qm-acm`, `fsl,imx8qxp-acm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: NXP i.MX8 Audio Clock Mux is dedicated clock muxing IP used to control Audio related clock on the SoC..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `power-domains`, `#clock-cells`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `power-domains`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imx8-clock.h for the full list of i.MX8 ACM clock IDs.; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `fsl,imx8dxl-acm`, `fsl,imx8qm-acm`, `fsl,imx8qxp-acm`.
- `reg`: maxItems 1.
- `clocks`: maxItems 27; minItems 13.
- `clock-names`: maxItems 27; minItems 13.
- `#clock-cells`: const `1`; The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imx8-clock.h for the full list of i.MX8 ACM clock IDs..
- `power-domains`: maxItems 21; minItems 13.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 282 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/imx8-lpcg.h`, `dt-bindings/firmware/imx/rsrc.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx8dxl-acm`, `fsl,imx8qm-acm`, `fsl,imx8qxp-acm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8-acm.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8-acm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8m-anatop.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8m-anatop.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8m-anatop.yaml` is a Devicetree binding schema for `NXP i.MX8M Family Anatop Module`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx8mm-anatop`, `fsl,imx8mq-anatop`, `fsl,imx8mn-anatop`, `fsl,imx8mp-anatop`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: NXP i.MX8M Family anatop PLL module which generates PLL to CCM root..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 2 oneOf alternatives.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `interrupts`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 51 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx8mm-anatop`, `fsl,imx8mq-anatop`, `fsl,imx8mn-anatop`, `fsl,imx8mp-anatop`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8m-anatop.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8m-anatop.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8ulp-sim-lpav.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8ulp-sim-lpav.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8ulp-sim-lpav.yaml` is a Devicetree binding schema for `NXP i.MX8ULP LPAV System Integration Module (SIM)`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx8ulp-sim-lpav`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The i.MX8ULP LPAV subsystem contains a block control module known as SIM LPAV, which offers functionalities such as clock gating or reset line assertion/de-assertion..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`, `mux-controller`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`, `mux-controller`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: const `fsl,imx8ulp-sim-lpav`.
- `reg`: maxItems 1.
- `clocks`: maxItems 3.
- `clock-names`: 3 positional items.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.
- `mux-controller`: ref `/schemas/mux/reg-mux.yaml#`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 72 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/mux/reg-mux.yaml#`, DTS examples or descriptions reference `dt-bindings/clock/imx8ulp-clock.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `fsl,imx8ulp-sim-lpav`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8ulp-sim-lpav.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx8ulp-sim-lpav.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx93-anatop.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx93-anatop.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx93-anatop.yaml` is a Devicetree binding schema for `NXP i.MX93 ANATOP Clock Module`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx93-anatop`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: NXP i.MX93 ANATOP module which contains PLL and OSC to Clock Controller Module..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 1 positional items.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 42 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx93-anatop`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx93-anatop.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,imx93-anatop.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,plldig.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,plldig.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,plldig.yaml` is a Devicetree binding schema for `NXP QorIQ Layerscape LS1028A Display PIXEL Clock`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,ls1028a-plldig`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: NXP LS1028A has a clock domain PXLCLK0 used for the Display output interface in the display core, as implemented in TSMC CLN28HPM PLL. which generate and offers pixel clocks to Display..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `fsl,vco-hz`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,ls1028a-plldig`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `0`.
- `fsl,vco-hz`: Optional for VCO frequency of the PLL in Hertz. The VCO frequency of this PLL cannot be changed during runtime only at startup. Therefore, the output frequencies are very limited and might not even closely match the requ.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 58 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,ls1028a-plldig`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,plldig.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,plldig.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,qoriq-clock-legacy.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,qoriq-clock-legacy.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,qoriq-clock-legacy.yaml` is a Devicetree binding schema for `Legacy Clock Block on Freescale QorIQ Platforms`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,qoriq-core-pll-1.0`, `fsl,qoriq-core-pll-2.0`, `fsl,qoriq-core-mux-1.0`, `fsl,qoriq-core-mux-2.0`, `fsl,qoriq-sysclk-1.0`, `fsl,qoriq-sysclk-2.0`, `fsl,qoriq-platform-pll-1.0`, `fsl,qoriq-platform-pll-2.0`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: These nodes are deprecated. Kernels should continue to support device trees with these nodes, but new device trees should not use them. Most of the bindings are from the common clock binding[1]. [1] Documentation/devicetree/bindings/clock/clock-bindings.txt.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: present with inherited core-schema constraints; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `fsl,qoriq-core-pll-1.0`, `fsl,qoriq-core-pll-2.0`, `fsl,qoriq-core-mux-1.0`, `fsl,qoriq-core-mux-2.0`, `fsl,qoriq-sysclk-1.0`, `fsl,qoriq-sysclk-2.0`, `fsl,qoriq-platform-pll-1.0`, `fsl,qoriq-platform-pll-2.0`.
- `reg`: maxItems 1.
- `clocks`: maxItems 4; minItems 1.
- `clock-names`: maxItems 4; minItems 1.
- `#clock-cells`: present with inherited core-schema constraints.
- `clock-output-names`: maxItems 8; minItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 84 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,qoriq-core-pll-1.0`, `fsl,qoriq-core-pll-2.0`, `fsl,qoriq-core-mux-1.0`, `fsl,qoriq-core-mux-2.0`, `fsl,qoriq-sysclk-1.0`, `fsl,qoriq-sysclk-2.0`, `fsl,qoriq-platform-pll-1.0`, `fsl,qoriq-platform-pll-2.0`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,qoriq-clock-legacy.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,qoriq-clock-legacy.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,qoriq-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,qoriq-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,qoriq-clock.yaml` is a Devicetree binding schema for `Clock Block on Freescale QorIQ Platforms`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,p2041-clockgen`, `fsl,p3041-clockgen`, `fsl,p4080-clockgen`, `fsl,p5020-clockgen`, `fsl,p5040-clockgen`, `fsl,qoriq-clockgen-1.0`, `fsl,t1023-clockgen`, `fsl,t1024-clockgen`, `fsl,t1040-clockgen`, `fsl,t1042-clockgen`, `fsl,t2080-clockgen`, `fsl,t2081-clockgen`, and 13 more. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Freescale QorIQ chips take primary clocking input from the external SYSCLK signal. The SYSCLK input (frequency) is multiplied using multiple phase locked loops (PLL) to create a variety of frequencies which can then be passed to a variety of internal logic, including cores and peripheral IP blocks. Please refer to the Reference Manual for details. All references to "1.0" and "2.0" refer to the QorIQ chassis version t.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `clock-frequency`, `ranges`, `#address-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `2`; The first cell of the clock specifier is the clock type, and the second cell is the clock index for the specified type. Type# Name Index Cell 0 sysclk must be 0 1 cmux index (n in CLKCnCSR) 2 hwaccel index (n in CLKCGnHW; this defines how consumers encode clock phandle specifiers.
- `compatible`: 4 oneOf alternatives.
- `reg`: maxItems 1.
- `clocks`: minItems 1; 2 positional items.
- `clock-names`: 2 positional items.
- `#clock-cells`: const `2`; The first cell of the clock specifier is the clock type, and the second cell is the clock index for the specified type. Type# Name Index Cell 0 sysclk must be 0 1 cmux index (n in CLKCnCSR) 2 hwaccel index (n in CLKCGnHW.
- `clock-frequency`: Input system clock frequency (SYSCLK).
- `ranges` is allowed by the schema.
- `#address-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 2 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 207 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
For fixed-rate style nodes, `clock-frequency` becomes persistent board data that the fixed-clock provider uses directly instead of deriving a rate from hardware registers.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `fsl,qoriq-clock-legacy.yaml`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,p2041-clockgen`, `fsl,p3041-clockgen`, `fsl,p4080-clockgen`, `fsl,p5020-clockgen`, `fsl,p5040-clockgen`, `fsl,qoriq-clockgen-1.0`, `fsl,t1023-clockgen`, `fsl,t1024-clockgen`, `fsl,t1040-clockgen`, `fsl,t1042-clockgen`, `fsl,t2080-clockgen`, `fsl,t2081-clockgen`, and 13 more, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,qoriq-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,qoriq-clock.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,scu-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,scu-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,scu-clk.yaml` is a Devicetree binding schema for `i.MX SCU Client Device Node - Clock Controller Based on SCU Message Protocol`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx8dxl-clk`, `fsl,imx8qm-clk`, `fsl,imx8qxp-clk`, `fsl,scu-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: i.MX SCU Client Device Node Client nodes are maintained as children of the relevant IMX-SCU device node. This binding uses the common clock binding. (Documentation/devicetree/bindings/clock/clock-bindings.txt) The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See the full list of clock IDs from include/dt-bindings/clock/imx8qxp-clock.h.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`. Important properties include `compatible`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `2`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 2 positional items.
- `#clock-cells`: const `2`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 43 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling.

### Integration Points
Integration is through compatible matching for `fsl,imx8dxl-clk`, `fsl,imx8qm-clk`, `fsl,imx8qxp-clk`, `fsl,scu-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,scu-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,scu-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,vf610-ccm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,vf610-ccm.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,vf610-ccm.yaml` is a Devicetree binding schema for `Clock for Freescale Vybrid VF610 SOC`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,vf610-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/vf610-clock.h for the full list of VF610 clock IDs.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,vf610-ccm`.
- `reg`: maxItems 1.
- `clocks`: minItems 2; 4 positional items.
- `clock-names`: minItems 2; 4 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 58 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,vf610-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,vf610-ccm.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/fsl,vf610-ccm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gated-fixed-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gated-fixed-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gated-fixed-clock.yaml` is a Devicetree binding schema for `Gated Fixed clock`. It documents and validates clock-provider nodes for generic fixed clock provider infrastructure, with compatible contract `gated-fixed-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `clock-frequency`, `vdd-supply`. Important properties include `compatible`, `#clock-cells`, `clock-output-names`, `enable-gpios`, `clock-frequency`, `vdd-supply`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `gated-fixed-clock`.
- `#clock-cells`: const `0`.
- `clock-output-names`: maxItems 1.
- `enable-gpios`: maxItems 1; Contains a single GPIO specifier for the GPIO that enables and disables the oscillator..
- `clock-frequency` is allowed by the schema.
- `vdd-supply`: handle of the regulator that provides the supply voltage.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 49 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
For fixed-rate style nodes, `clock-frequency` becomes persistent board data that the fixed-clock provider uses directly instead of deriving a rate from hardware registers.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling.

### Integration Points
Integration is through compatible matching for `gated-fixed-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gated-fixed-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gated-fixed-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/google,gs101-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/google,gs101-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/google,gs101-clock.yaml` is a Devicetree binding schema for `Google GS101 SoC clock controller`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `google,gs101-cmu-top`, `google,gs101-cmu-apm`, `google,gs101-cmu-dpu`, `google,gs101-cmu-hsi0`, `google,gs101-cmu-hsi2`, `google,gs101-cmu-misc`, `google,gs101-cmu-peric0`, `google,gs101-cmu-peric1`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Google GS101 clock controller is comprised of several CMU units, generating clocks for different domains. Those CMU units are modeled as separate device tree nodes, and might depend on each other. The root clock in that clock tree is OSCCLK (24.576 MHz). That external clock must be defined as a fixed-rate clock in dts. CMU_TOP is a top-level CMU, where all base clocks are prepared using PLLs and dividers; all other l.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `clocks`, `clock-names`, `reg`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `power-domains`, `samsung,sysreg`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `google,gs101-cmu-top`, `google,gs101-cmu-apm`, `google,gs101-cmu-dpu`, `google,gs101-cmu-hsi0`, `google,gs101-cmu-hsi2`, `google,gs101-cmu-misc`, `google,gs101-cmu-peric0`, `google,gs101-cmu-peric1`.
- `reg`: maxItems 1.
- `clocks`: maxItems 5; minItems 1.
- `clock-names`: maxItems 5; minItems 1.
- `#clock-cells`: const `1`.
- `power-domains`: maxItems 1.
- `samsung,sysreg`: Phandle to system registers interface.; ref `/schemas/types.yaml#/definitions/phandle`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 220 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/types.yaml#/definitions/phandle`, DTS examples or descriptions reference `dt-bindings/clock/google,gs101.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `google,gs101-cmu-top`, `google,gs101-cmu-apm`, `google,gs101-cmu-dpu`, `google,gs101-cmu-hsi0`, `google,gs101-cmu-hsi2`, `google,gs101-cmu-misc`, `google,gs101-cmu-peric0`, `google,gs101-cmu-peric1`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/google,gs101-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/google,gs101-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gpio-gate-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gpio-gate-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gpio-gate-clock.yaml` is a Devicetree binding schema for `Simple GPIO clock gate`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `gpio-gate-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `enable-gpios`. Important properties include `compatible`, `clocks`, `#clock-cells`, `enable-gpios`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `gpio-gate-clock`.
- `clocks`: maxItems 1.
- `#clock-cells`: const `0`.
- `enable-gpios`: maxItems 1; GPIO reference for enabling and disabling the clock..

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 42 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/gpio/gpio.h`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `gpio-gate-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gpio-gate-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gpio-gate-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gpio-mux-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gpio-mux-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gpio-mux-clock.yaml` is a Devicetree binding schema for `Simple GPIO clock multiplexer`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `gpio-mux-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `clocks`, `#clock-cells`, `select-gpios`. Important properties include `compatible`, `clocks`, `#clock-cells`, `select-gpios`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `gpio-mux-clock`.
- `clocks`: 2 positional items.
- `#clock-cells`: const `0`.
- `select-gpios`: maxItems 1; GPIO reference for selecting the parent clock..

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 45 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/gpio/gpio.h`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `gpio-mux-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gpio-mux-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/gpio-mux-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/hisilicon,hi3559av100-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/hisilicon,hi3559av100-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/hisilicon,hi3559av100-clock.yaml` is a Devicetree binding schema for `Hisilicon SOC Clock for HI3559AV100`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `hisilicon,hi3559av100-clock`, `hisilicon,hi3559av100-shub-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Hisilicon SOC clock control module which supports the clocks, resets and power domains on HI3559AV100. See also: dt-bindings/clock/hi3559av100-clock.h.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`, `#reset-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `2`; First cell is reset request register offset. Second cell is bit offset in reset request register.; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: enum `hisilicon,hi3559av100-clock`, `hisilicon,hi3559av100-shub-clock`.
- `reg`: maxItems 2; minItems 1.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `2`; First cell is reset request register offset. Second cell is bit offset in reset request register..

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 59 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `hisilicon,hi3559av100-clock`, `hisilicon,hi3559av100-shub-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/hisilicon,hi3559av100-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/hisilicon,hi3559av100-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/idt,versaclock5.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/idt,versaclock5.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/idt,versaclock5.yaml` is a Devicetree binding schema for `IDT VersaClock 5 and 6 programmable I2C clock generators`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `idt,5p49v5923`, `idt,5p49v5925`, `idt,5p49v5933`, `idt,5p49v5935`, `idt,5p49v60`, `idt,5p49v6901`, `idt,5p49v6965`, `idt,5p49v6975`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The IDT VersaClock 5 and VersaClock 6 are programmable I2C clock generators providing from 3 to 12 output clocks. When referencing the provided clock in the DT using phandle and clock specifier, the following mapping applies: - 5P49V5923: 0 -- OUT0_SEL_I2CB 1 -- OUT1 2 -- OUT2 - 5P49V5933: 0 -- OUT0_SEL_I2CB 1 -- OUT1 2 -- OUT4 - other parts: 0 -- OUT0_SEL_I2CB 1 -- OUT1 2 -- OUT2 3 -- OUT3 4 -- OUT4 The idt,shutdown.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `idt,xtal-load-femtofarads`, `idt,shutdown`, `idt,output-enable-active`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `idt,5p49v5923`, `idt,5p49v5925`, `idt,5p49v5933`, `idt,5p49v5935`, `idt,5p49v60`, `idt,5p49v6901`, `idt,5p49v6965`, `idt,5p49v6975`.
- `reg`: enum `104`, `106`; I2C device address.
- `clocks`: maxItems 2; minItems 1.
- `clock-names`: maxItems 2; minItems 1.
- `#clock-cells`: const `1`.
- `idt,xtal-load-femtofarads`: Optional load capacitor for XTAL1 and XTAL2.
- `idt,shutdown`: enum `0`, `1`; If 1, this enables the shutdown functionality: the chip will be shut down if the SD/OE pin is driven high. If 0, this disables the shutdown functionality: the chip will never be shut down based on the value of the SD/OE ; ref `/schemas/types.yaml#/definitions/uint32`.
- `idt,output-enable-active`: enum `0`, `1`; If 1, this enables output when the SD/OE pin is high, and disables output when the SD/OE pin is low. If 0, this disables output when the SD/OE pin is high, and enables output when the SD/OE pin is low. This corresponds t; ref `/schemas/types.yaml#/definitions/uint32`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 195 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/types.yaml#/definitions/uint32`, DTS examples or descriptions reference `dt-bindings/clock/versaclock.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `idt,5p49v5923`, `idt,5p49v5925`, `idt,5p49v5933`, `idt,5p49v5935`, `idt,5p49v60`, `idt,5p49v6901`, `idt,5p49v6965`, `idt,5p49v6975`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/idt,versaclock5.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/idt,versaclock5.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/img,pistachio-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/img,pistachio-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/img,pistachio-clk.yaml` is a Devicetree binding schema for `Imagination Technologies Pistachio SoC clock controllers`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `img,pistachio-clk`, `img,pistachio-clk-periph`, `img,pistachio-cr-periph`, `img,pistachio-cr-top`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Pistachio has four clock controllers (core clock, peripheral clock, peripheral general control, and top general control) which are instantiated individually from the device-tree. Core clock controller: The core clock controller generates clocks for the CPU, RPU (WiFi + BT co-processor), audio, and several peripherals. Peripheral clock controller: The peripheral clock controller generates clocks for the DDR, ROM, and .

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 1 positional items.
- `reg`: maxItems 1.
- `clocks`: maxItems 3; minItems 1.
- `clock-names`: maxItems 3; minItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 136 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `img,pistachio-clk`, `img,pistachio-clk-periph`, `img,pistachio-cr-periph`, `img,pistachio-cr-top`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/img,pistachio-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/img,pistachio-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx1-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx1-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx1-clock.yaml` is a Devicetree binding schema for `Freescale i.MX1 CPUs Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx1-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imx1-clock.h for the full list of i.MX1 clock IDs..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx1-ccm`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 42 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/imx1-clock.h`, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx1-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx1-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx1-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx21-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx21-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx21-clock.yaml` is a Devicetree binding schema for `Freescale i.MX21 Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx21-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imx21-clock.h for the full list of i.MX21 clock IDs..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx21-ccm`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 42 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/imx21-clock.h`, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx21-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx21-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx21-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx23-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx23-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx23-clock.yaml` is a Devicetree binding schema for `Freescale i.MX23 Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx23-clkctrl`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. The following is a full list of i.MX23 clocks and IDs. Clock ID ------------------ ref_xtal 0 pll 1 ref_cpu 2 ref_emi 3 ref_pix 4 ref_io 5 saif_sel 6 lcdif_sel 7 gpmi_sel 8 ssp_sel 9 emi_sel 10 cpu 11 etm_sel 12 cpu_pll 13 cpu_xtal 14 hbus 15 xbus 16 lcdif_div 17 ssp_div 18 gpmi_div 19 emi_pll 20 emi_xtal 21 etm_d.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx23-clkctrl`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 85 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx23-clkctrl`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx23-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx23-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx25-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx25-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx25-clock.yaml` is a Devicetree binding schema for `Freescale i.MX25 Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx25-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. The following is a full list of i.MX25 clocks and IDs. Clock ID -------------------------- dummy 0 osc 1 mpll 2 upll 3 mpll_cpu_3_4 4 cpu_sel 5 cpu 6 ahb 7 usb_div 8 ipg 9 per0_sel 10 per1_sel 11 per2_sel 12 per3_sel 13 per4_sel 14 per5_sel 15 per6_sel 16 per7_sel 17 per8_sel 18 per9_sel 19 per10_sel 20 per11_sel .

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx25-ccm`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `interrupts`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 178 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx25-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx25-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx25-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx27-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx27-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx27-clock.yaml` is a Devicetree binding schema for `Freescale i.MX27 Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx27-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imx27-clock.h for the full list of i.MX27 clock IDs..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx27-ccm`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `interrupts`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 46 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/imx27-clock.h`, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx27-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx27-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx27-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx28-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx28-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx28-clock.yaml` is a Devicetree binding schema for `Freescale i.MX28 Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx28-clkctrl`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. The following is a full list of i.MX28 clocks and IDs. Clock ID ------------------ ref_xtal 0 pll0 1 pll1 2 pll2 3 ref_cpu 4 ref_emi 5 ref_io0 6 ref_io1 7 ref_pix 8 ref_hsadc 9 ref_gpmi 10 saif0_sel 11 saif1_sel 12 gpmi_sel 13 ssp0_sel 14 ssp1_sel 15 ssp2_sel 16 ssp3_sel 17 emi_sel 18 etm_sel 19 lcdif_sel 20 cpu 2.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx28-clkctrl`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 108 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx28-clkctrl`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx28-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx28-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx31-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx31-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx31-clock.yaml` is a Devicetree binding schema for `Freescale i.MX31 Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx31-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. The following is a full list of i.MX31 clocks and IDs. Clock ID ----------------------- dummy 0 ckih 1 ckil 2 mpll 3 spll 4 upll 5 mcu_main 6 hsp 7 ahb 8 nfc 9 ipg 10 per_div 11 per 12 csi_sel 13 fir_sel 14 csi_div 15 usb_div_pre 16 usb_div_post 17 fir_div_pre 18 fir_div_post 19 sdhc1_gate 20 sdhc2_gate 21 gpt_gat.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx31-ccm`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `interrupts`: CCM provides 2 interrupt requests, request 1 is to generate interrupt for DVFS when a frequency change is requested, request 2 is to generate interrupt for DPTC when a voltage change is requested.; 2 positional items.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 112 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx31-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx31-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx31-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx35-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx35-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx35-clock.yaml` is a Devicetree binding schema for `Freescale i.MX35 Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx35-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. The following is a full list of i.MX35 clocks and IDs. Clock ID --------------------------- ckih 0 mpll 1 ppll 2 mpll_075 3 arm 4 hsp 5 hsp_div 6 hsp_sel 7 ahb 8 ipg 9 arm_per_div 10 ahb_per_div 11 ipg_per 12 uart_sel 13 uart_div 14 esdhc_sel 15 esdhc1_div 16 esdhc2_div 17 esdhc3_div 18 spdif_sel 19 spdif_div_pre .

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx35-ccm`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `interrupts`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 131 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx35-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx35-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx35-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx5-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx5-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx5-clock.yaml` is a Devicetree binding schema for `Freescale i.MX5 Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx53-ccm`, `fsl,imx51-ccm`, `fsl,imx50-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imx5-clock.h for the full list of i.MX5 clock IDs..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `fsl,imx53-ccm`, `fsl,imx51-ccm`, `fsl,imx50-ccm`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `interrupts`: CCM provides 2 interrupt requests, request 1 is to generate interrupt for frequency or mux change, request 2 is to generate interrupt for oscillator read or PLL lock.; 2 positional items.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 58 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/imx5-clock.h`, `dt-bindings/interrupt-controller/arm-gic.h`, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx53-ccm`, `fsl,imx51-ccm`, `fsl,imx50-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx5-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx5-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6q-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6q-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6q-clock.yaml` is a Devicetree binding schema for `Freescale i.MX6 Quad Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx6q-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `interrupts`, `fsl,pmic-stby-poweroff`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx6q-ccm`.
- `reg`: maxItems 1.
- `clocks`: minItems 5; 6 positional items.
- `clock-names`: minItems 5; 6 positional items.
- `#clock-cells`: const `1`.
- `interrupts`: CCM provides 2 interrupt requests, request 1 is to generate interrupt for frequency or mux change, request 2 is to generate interrupt for oscillator read or PLL lock.; 2 positional items.
- `fsl,pmic-stby-poweroff`: Use this property if the SoC should be powered off by external power management IC (PMIC) triggered via PMIC_STBY_REQ signal. Boards that are designed to initiate poweroff on PMIC_ON_REQ signal should be using "syscon-po; ref `/schemas/types.yaml#/definitions/flag`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 78 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/types.yaml#/definitions/flag`, DTS examples or descriptions reference `dt-bindings/interrupt-controller/arm-gic.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx6q-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6q-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6q-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sl-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sl-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sl-clock.yaml` is a Devicetree binding schema for `Freescale i.MX6 SoloLite Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx6sl-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx6sl-ccm`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `interrupts`: CCM provides 2 interrupt requests, request 1 is to generate interrupt for frequency or mux change, request 2 is to generate interrupt for oscillator read or PLL lock.; 2 positional items.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 50 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/interrupt-controller/arm-gic.h`, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx6sl-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sl-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sl-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sll-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sll-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sll-clock.yaml` is a Devicetree binding schema for `Freescale i.MX6 SLL Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx6sll-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `#clock-cells`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx6sll-ccm`.
- `reg`: maxItems 1.
- `clocks`: 4 positional items.
- `clock-names`: 4 positional items.
- `#clock-cells`: const `1`.
- `interrupts`: CCM provides 2 interrupt requests, request 1 is to generate interrupt for frequency or mux change, request 2 is to generate interrupt for oscillator read or PLL lock.; 2 positional items.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 68 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/interrupt-controller/arm-gic.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx6sll-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sll-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sll-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sx-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sx-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sx-clock.yaml` is a Devicetree binding schema for `Freescale i.MX6 SoloX Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx6sx-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `#clock-cells`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx6sx-ccm`.
- `reg`: maxItems 1.
- `clocks`: 6 positional items.
- `clock-names`: 6 positional items.
- `#clock-cells`: const `1`.
- `interrupts`: CCM provides 2 interrupt requests, request 1 is to generate interrupt for frequency or mux change, request 2 is to generate interrupt for oscillator read or PLL lock.; 2 positional items.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 72 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/interrupt-controller/arm-gic.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx6sx-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sx-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6sx-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6ul-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6ul-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6ul-clock.yaml` is a Devicetree binding schema for `Freescale i.MX6 UltraLite Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx6ul-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `#clock-cells`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx6ul-ccm`.
- `reg`: maxItems 1.
- `clocks`: minItems 4; 5 positional items.
- `clock-names`: minItems 4; 5 positional items.
- `#clock-cells`: const `1`.
- `interrupts`: CCM provides 2 interrupt requests, request 1 is to generate interrupt for frequency or mux change, request 2 is to generate interrupt for oscillator read or PLL lock.; 2 positional items.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 72 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/interrupt-controller/arm-gic.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx6ul-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6ul-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx6ul-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7d-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7d-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7d-clock.yaml` is a Devicetree binding schema for `Freescale i.MX7 Dual Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx7d-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imx7d-clock.h for the full list of i.MX7 Dual clock IDs..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx7d-ccm`.
- `reg`: maxItems 1.
- `clocks`: 2 positional items.
- `clock-names`: 2 positional items.
- `#clock-cells`: const `1`.
- `interrupts`: 2 positional items.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 64 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/interrupt-controller/arm-gic.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx7d-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7d-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7d-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7ulp-pcc-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7ulp-pcc-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7ulp-pcc-clock.yaml` is a Devicetree binding schema for `Freescale i.MX7ULP Peripheral Clock Control (PCC) modules Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx7ulp-pcc2`, `fsl,imx7ulp-pcc3`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: i.MX7ULP Clock functions are under joint control of the System Clock Generation (SCG) modules, Peripheral Clock Control (PCC) modules, and Core Mode Controller (CMC)1 blocks The clocking scheme provides clear separation between M4 domain and A7 domain. Except for a few clock sources shared between two domains, such as the System Oscillator clock, the Slow IRC (SIRC), and and the Fast IRC clock (FIRCLK), clock sources.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `fsl,imx7ulp-pcc2`, `fsl,imx7ulp-pcc3`.
- `reg`: maxItems 1.
- `clocks`: 11 positional items.
- `clock-names`: 11 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 110 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/imx7ulp-clock.h`, `dt-bindings/interrupt-controller/arm-gic.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx7ulp-pcc2`, `fsl,imx7ulp-pcc3`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7ulp-pcc-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7ulp-pcc-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7ulp-scg-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7ulp-scg-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7ulp-scg-clock.yaml` is a Devicetree binding schema for `Freescale i.MX7ULP System Clock Generation (SCG) modules Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx7ulp-scg1`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: i.MX7ULP Clock functions are under joint control of the System Clock Generation (SCG) modules, Peripheral Clock Control (PCC) modules, and Core Mode Controller (CMC)1 blocks The clocking scheme provides clear separation between M4 domain and A7 domain. Except for a few clock sources shared between two domains, such as the System Oscillator clock, the Slow IRC (SIRC), and and the Fast IRC clock (FIRCLK), clock sources.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imx7ulp-scg1`.
- `reg`: maxItems 1.
- `clocks`: 5 positional items.
- `clock-names`: 5 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 88 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/imx7ulp-clock.h`, `dt-bindings/interrupt-controller/arm-gic.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx7ulp-scg1`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7ulp-scg-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx7ulp-scg-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8m-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8m-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8m-clock.yaml` is a Devicetree binding schema for `NXP i.MX8M Family Clock Control Module`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx8mm-ccm`, `fsl,imx8mn-ccm`, `fsl,imx8mp-ccm`, `fsl,imx8mq-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: NXP i.MX8M Mini/Nano/Plus/Quad clock control module is an integrated clock controller, which generates and supplies to all modules..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `interrupts`, `fsl,operating-mode`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imx8m-clock.h for the full list of i.MX8M clock IDs.; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `fsl,imx8mm-ccm`, `fsl,imx8mn-ccm`, `fsl,imx8mp-ccm`, `fsl,imx8mq-ccm`.
- `reg`: maxItems 1.
- `clocks`: maxItems 7; minItems 6.
- `clock-names`: maxItems 7; minItems 6.
- `#clock-cells`: const `1`; The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imx8m-clock.h for the full list of i.MX8M clock IDs..
- `interrupts`: maxItems 2.
- `fsl,operating-mode`: enum `nominal`, `overdrive`; The operating mode of the SoC. This affects the maximum clock rates that can safely be configured by the clock controller.; ref `/schemas/types.yaml#/definitions/string`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 2 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 133 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/types.yaml#/definitions/string`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx8mm-ccm`, `fsl,imx8mn-ccm`, `fsl,imx8mp-ccm`, `fsl,imx8mq-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8m-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8m-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8mp-audiomix.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8mp-audiomix.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8mp-audiomix.yaml` is a Devicetree binding schema for `NXP i.MX8MP AudioMIX Block Control`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx8mp-audio-blk-ctrl`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: NXP i.MX8M Plus AudioMIX is dedicated clock muxing and gating IP used to control Audio related clock on the SoC..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `power-domains`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `#reset-cells`, `power-domains`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imx8mp-clock.h for the full list of i.MX8MP IMX8MP_CLK_AUDIOMIX_ clock IDs.; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: const `fsl,imx8mp-audio-blk-ctrl`.
- `reg`: maxItems 1.
- `clocks`: maxItems 8; minItems 8.
- `clock-names`: 8 positional items.
- `#clock-cells`: const `1`; The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imx8mp-clock.h for the full list of i.MX8MP IMX8MP_CLK_AUDIOMIX_ clock IDs..
- `#reset-cells`: const `1`.
- `power-domains`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 84 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/imx8mp-clock.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `fsl,imx8mp-audio-blk-ctrl`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8mp-audiomix.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8mp-audiomix.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8qxp-lpcg.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8qxp-lpcg.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8qxp-lpcg.yaml` is a Devicetree binding schema for `NXP i.MX8QXP LPCG (Low-Power Clock Gating) Clock`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx8qxp-lpcg`, `fsl,imx8qm-lpcg`, `fsl,imx8qxp-lpcg-adma`, `fsl,imx8qxp-lpcg-conn`, `fsl,imx8qxp-lpcg-dc`, `fsl,imx8qxp-lpcg-dsp`, `fsl,imx8qxp-lpcg-gpu`, `fsl,imx8qxp-lpcg-hsio`, `fsl,imx8qxp-lpcg-img`, `fsl,imx8qxp-lpcg-lsio`, `fsl,imx8qxp-lpcg-vpu`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The Low-Power Clock Gate (LPCG) modules contain a local programming model to control the clock gates for the peripherals. An LPCG module is used to locally gate the clocks for the associated peripheral. This level of clock gating is provided after the clocks are generated by the SCU resources and clock controls. Thus even if the clock is enabled by these control bits, it might still not be running based on the base r.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`, `power-domains`, `clock-indices`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 3 oneOf alternatives.
- `reg`: maxItems 1.
- `clocks`: maxItems 8; minItems 1; Input parent clocks phandle array for each clock.
- `#clock-cells`: const `1`.
- `clock-output-names`: maxItems 8; minItems 1; Shall be the corresponding names of the outputs. NOTE this property must be specified in the same order as the clock-indices property..
- `power-domains`: maxItems 1.
- `clock-indices`: maxItems 8; minItems 1; An integer array indicating the bit offset for each clock. Refer to <include/dt-bindings/clock/imx8-lpcg.h> for the supported LPCG clock indices..

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 103 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/imx8-lpcg.h`, `dt-bindings/firmware/imx/rsrc.h`, `dt-bindings/interrupt-controller/arm-gic.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx8qxp-lpcg`, `fsl,imx8qm-lpcg`, `fsl,imx8qxp-lpcg-adma`, `fsl,imx8qxp-lpcg-conn`, `fsl,imx8qxp-lpcg-dc`, `fsl,imx8qxp-lpcg-dsp`, `fsl,imx8qxp-lpcg-gpu`, `fsl,imx8qxp-lpcg-hsio`, `fsl,imx8qxp-lpcg-img`, `fsl,imx8qxp-lpcg-lsio`, `fsl,imx8qxp-lpcg-vpu`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8qxp-lpcg.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8qxp-lpcg.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8ulp-cgc-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8ulp-cgc-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8ulp-cgc-clock.yaml` is a Devicetree binding schema for `NXP i.MX8ULP Clock Generation & Control(CGC) Module`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx8ulp-cgc1`, `fsl,imx8ulp-cgc2`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: On i.MX8ULP, The clock sources generation, distribution and management is under the control of several CGCs & PCCs modules. The CGC modules generate and distribute clocks on the device..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `fsl,imx8ulp-cgc1`, `fsl,imx8ulp-cgc2`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 43 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `fsl,imx8ulp-cgc1`, `fsl,imx8ulp-cgc2`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8ulp-cgc-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8ulp-cgc-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8ulp-pcc-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8ulp-pcc-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8ulp-pcc-clock.yaml` is a Devicetree binding schema for `NXP i.MX8ULP Peripheral Clock Controller(PCC) Module`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx8ulp-pcc3`, `fsl,imx8ulp-pcc4`, `fsl,imx8ulp-pcc5`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: On i.MX8ULP, The clock sources generation, distribution and management is under the control of several CGCs & PCCs modules. The PCC modules control software reset, clock selection, optional division and clock gating mode for peripherals..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`, `#reset-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: enum `fsl,imx8ulp-pcc3`, `fsl,imx8ulp-pcc4`, `fsl,imx8ulp-pcc5`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 50 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `fsl,imx8ulp-pcc3`, `fsl,imx8ulp-pcc4`, `fsl,imx8ulp-pcc5`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8ulp-pcc-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx8ulp-pcc-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx93-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx93-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx93-clock.yaml` is a Devicetree binding schema for `NXP i.MX93 Clock Control Module`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imx91-ccm`, `fsl,imx93-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: i.MX93 clock control module is an integrated clock controller, which includes clock generator, clock gate and supplies to all modules..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; See include/dt-bindings/clock/imx93-clock.h for the full list of i.MX93 clock IDs.; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `fsl,imx91-ccm`, `fsl,imx93-ccm`.
- `reg`: maxItems 1.
- `clocks`: specify the external clocks used by the CCM module.; 3 positional items.
- `clock-names`: specify the external clocks names used by the CCM module.; 3 positional items.
- `#clock-cells`: const `1`; See include/dt-bindings/clock/imx93-clock.h for the full list of i.MX93 clock IDs..

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 63 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imx91-ccm`, `fsl,imx93-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx93-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imx93-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imxrt1050-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imxrt1050-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imxrt1050-clock.yaml` is a Devicetree binding schema for `Freescale i.MXRT Clock Controller`. It documents and validates clock-provider nodes for NXP/Freescale i.MX and related clock infrastructure, with compatible contract `fsl,imxrt1050-ccm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/imxrt*-clock.h for the full list of i.MXRT clock IDs..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `interrupts`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `interrupts`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `fsl,imxrt1050-ccm`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1; 24m osc.
- `clock-names`: const `osc`.
- `#clock-cells`: const `1`.
- `interrupts`: maxItems 2.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 59 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/imxrt1050-clock.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `fsl,imxrt1050-ccm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imxrt1050-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/imxrt1050-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ingenic,cgu.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ingenic,cgu.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ingenic,cgu.yaml` is a Devicetree binding schema for `Ingenic SoCs CGU`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `ingenic,jz4740-cgu`, `ingenic,jz4725b-cgu`, `ingenic,jz4755-cgu`, `ingenic,jz4760-cgu`, `ingenic,jz4760b-cgu`, `ingenic,jz4770-cgu`, `ingenic,jz4780-cgu`, `ingenic,x1000-cgu`, `ingenic,x1830-cgu`, `simple-mfd`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The CGU in an Ingenic SoC provides all the clocks generated on-chip. It typically includes a variety of PLLs, multiplexers, dividers & gates in order to provide many different clock signals derived from only 2 external source clocks..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `#clock-cells`, `compatible`, `reg`, `clocks`, `clock-names`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `$nodename`, `#address-cells`, `#size-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: minItems 1; 2 positional items.
- `reg`: maxItems 1.
- `clocks`: 2 positional items.
- `clock-names`: 2 positional items.
- `#clock-cells`: const `1`.
- `$nodename`: present with inherited core-schema constraints.
- `#address-cells`: const `1`.
- `#size-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 132 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, schema references `/schemas/phy/ingenic,phy-usb.yaml#`, `/schemas/net/ingenic,mac.yaml#`, DTS examples or descriptions reference `dt-bindings/clock/ingenic,jz4770-cgu.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `ingenic,jz4740-cgu`, `ingenic,jz4725b-cgu`, `ingenic,jz4755-cgu`, `ingenic,jz4760-cgu`, `ingenic,jz4760b-cgu`, `ingenic,jz4770-cgu`, `ingenic,jz4780-cgu`, `ingenic,x1000-cgu`, `ingenic,x1830-cgu`, `simple-mfd`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ingenic,cgu.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/ingenic,cgu.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,agilex.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,agilex.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,agilex.yaml` is a Devicetree binding schema for `Intel SoCFPGA Agilex platform clock controller`. It documents and validates clock-provider nodes for Intel/SoCFPGA clock manager infrastructure, with compatible contract `intel,agilex-clkmgr`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The Intel Agilex Clock controller is an integrated clock controller, which generates and supplies to all modules..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `intel,agilex-clkmgr`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 46 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `intel,agilex-clkmgr`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,agilex.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,agilex.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,agilex5-clkmgr.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,agilex5-clkmgr.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,agilex5-clkmgr.yaml` is a Devicetree binding schema for `Intel SoCFPGA Agilex5 clock manager`. It documents and validates clock-provider nodes for Intel/SoCFPGA clock manager infrastructure, with compatible contract `intel,agilex5-clkmgr`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The Intel Agilex5 Clock Manager is an integrated clock controller, which generates and supplies clock to all the modules..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `intel,agilex5-clkmgr`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 40 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `intel,agilex5-clkmgr`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,agilex5-clkmgr.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,agilex5-clkmgr.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,cgu-lgm.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,cgu-lgm.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,cgu-lgm.yaml` is a Devicetree binding schema for `Intel Lightning Mountain SoC's Clock Controller(CGU)`. It documents and validates clock-provider nodes for Intel/SoCFPGA clock manager infrastructure, with compatible contract `intel,cgu-lgm`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Lightning Mountain(LGM) SoC's Clock Generation Unit(CGU) driver provides all means to access the CGU hardware module in order to generate a series of clocks for the whole system and individual peripherals. Please refer to include/dt-bindings/clock/intel,lgm-clk.h header file, it defines all available clocks as macros. These macros can be used in device tree sources..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `intel,cgu-lgm`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 46 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `intel,cgu-lgm`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,cgu-lgm.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,cgu-lgm.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,easic-n5x.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,easic-n5x.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,easic-n5x.yaml` is a Devicetree binding schema for `Intel SoCFPGA eASIC N5X platform clock controller`. It documents and validates clock-provider nodes for Intel/SoCFPGA clock manager infrastructure, with compatible contract `intel,easic-n5x-clkmgr`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The Intel eASIC N5X Clock controller is an integrated clock controller, which generates and supplies to all modules..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `intel,easic-n5x-clkmgr`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 46 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `intel,easic-n5x-clkmgr`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,easic-n5x.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,easic-n5x.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,stratix10.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,stratix10.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,stratix10.yaml` is a Devicetree binding schema for `Intel SoCFPGA Stratix10 platform clock controller`. It documents and validates clock-provider nodes for Intel/SoCFPGA clock manager infrastructure, with compatible contract `intel,stratix10-clkmgr`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `intel,stratix10-clkmgr`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 35 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `intel,stratix10-clkmgr`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,stratix10.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/intel,stratix10.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/loongson,ls1x-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/loongson,ls1x-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/loongson,ls1x-clk.yaml` is a Devicetree binding schema for `Loongson-1 Clock Controller`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `loongson,ls1b-clk`, `loongson,ls1c-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `loongson,ls1b-clk`, `loongson,ls1c-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 45 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `loongson,ls1b-clk`, `loongson,ls1c-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/loongson,ls1x-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/loongson,ls1x-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/loongson,ls2k-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/loongson,ls2k-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/loongson,ls2k-clk.yaml` is a Devicetree binding schema for `Loongson-2 SoC Clock Control Module`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `loongson,ls2k0300-clk`, `loongson,ls2k0500-clk`, `loongson,ls2k-clk`, `loongson,ls2k2000-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Loongson-2 SoC clock control module is an integrated clock controller, which generates and supplies to all modules..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/loongson,ls2k-clk.h for the full list of Loongson-2 SoC clock IDs.; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `loongson,ls2k0300-clk`, `loongson,ls2k0500-clk`, `loongson,ls2k-clk`, `loongson,ls2k2000-clk`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `clock-names`: 1 positional items.
- `#clock-cells`: const `1`; The clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. See include/dt-bindings/clock/loongson,ls2k-clk.h for the full list of Loongson-2 SoC clock IDs..

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 77 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `loongson,ls2k0300-clk`, `loongson,ls2k0500-clk`, `loongson,ls2k-clk`, `loongson,ls2k2000-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/loongson,ls2k-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/loongson,ls2k-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/lsi,axm5516-clks.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/lsi,axm5516-clks.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/lsi,axm5516-clks.yaml` is a Devicetree binding schema for `LSI AXM5516 Clock Controller`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `lsi,axm5516-clks`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: See <dt-bindings/clock/lsi,axxia-clock.h> for the list of supported clock IDs..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `lsi,axm5516-clks`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 43 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/lsi,axxia-clock.h`, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `lsi,axm5516-clks`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/lsi,axm5516-clks.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/lsi,axm5516-clks.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/lsi,nspire-cx-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/lsi,nspire-cx-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/lsi,nspire-cx-clock.yaml` is a Devicetree binding schema for `TI-NSPIRE Clocks`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `lsi,nspire-cx-ahb-divider`, `lsi,nspire-classic-ahb-divider`, `lsi,nspire-cx-clock`, `lsi,nspire-classic-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `0`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `lsi,nspire-cx-ahb-divider`, `lsi,nspire-classic-ahb-divider`, `lsi,nspire-cx-clock`, `lsi,nspire-classic-clock`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `0`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 33 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `lsi,nspire-cx-ahb-divider`, `lsi,nspire-classic-ahb-divider`, `lsi,nspire-cx-clock`, `lsi,nspire-classic-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/lsi,nspire-cx-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/lsi,nspire-cx-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,ap80x-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,ap80x-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,ap80x-clock.yaml` is a Devicetree binding schema for `Marvell Armada AP80x System Controller Clocks`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,ap806-clock`, `marvell,ap806-cpu-clock`, `marvell,ap807-clock`, `marvell,ap807-cpu-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The AP806/AP807 is one of the two core HW blocks of the Marvell Armada 7K/8K/931x SoCs. It contains system controllers, which provide several registers giving access to numerous features: clocks, pin-muxing and many other SoC configuration items..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `marvell,ap806-clock`, `marvell,ap806-cpu-clock`, `marvell,ap807-clock`, `marvell,ap807-cpu-clock`.
- `reg`: maxItems 1.
- `clocks`: 2 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 54 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `marvell,ap806-clock`, `marvell,ap806-cpu-clock`, `marvell,ap807-clock`, `marvell,ap807-cpu-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,ap80x-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,ap80x-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-370-corediv-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-370-corediv-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-370-corediv-clock.yaml` is a Devicetree binding schema for `Marvell MVEBU Core Divider Clock`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,armada-370-corediv-clock`, `marvell,armada-375-corediv-clock`, `marvell,armada-380-corediv-clock`, `marvell,mv98dx3236-corediv-clock`, `marvell,armada-390-corediv-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`, `clocks`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`, `clock-output-names`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 2 oneOf alternatives.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`.
- `clock-output-names`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 52 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `marvell,armada-370-corediv-clock`, `marvell,armada-375-corediv-clock`, `marvell,armada-380-corediv-clock`, `marvell,mv98dx3236-corediv-clock`, `marvell,armada-390-corediv-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-370-corediv-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-370-corediv-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-periph-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-periph-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-periph-clock.yaml` is a Devicetree binding schema for `Marvell Armada 37xx SoCs Peripheral Clocks`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,armada-3700-periph-clock-sb`, `marvell,armada-3700-periph-clock-nb`, `syscon`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Marvell Armada 37xx SoCs provide peripheral clocks which are used as clock source for the peripheral of the SoC. There are two different blocks associated to north bridge and south bridge. The following is a list of provided IDs for Armada 3700 North bridge clocks: ID Clock name Description ----------------------------------- 0 mmc MMC controller 1 sata_host Sata Host 2 sec_at Security AT 3 sac_dap Security DAP 4 tse.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 2 oneOf alternatives.
- `reg`: maxItems 1.
- `clocks`: 5 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 96 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `marvell,armada-3700-periph-clock-sb`, `marvell,armada-3700-periph-clock-nb`, `syscon`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-periph-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-periph-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-tbg-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-tbg-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-tbg-clock.yaml` is a Devicetree binding schema for `Marvell Armada 3700 Time Base Generator Clock`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,armada-3700-tbg-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Marvell Armada 37xx SoCs provide Time Base Generator clocks which are used as parent clocks for the peripheral clocks. The TBG clock consumer should specify the desired clock by having the clock ID in its "clocks" phandle cell. The following is a list of provided IDs and clock names on Armada 3700: 0 = TBG A P 1 = TBG B P 2 = TBG A S 3 = TBG B S.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `marvell,armada-3700-tbg-clock`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 54 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `marvell,armada-3700-tbg-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-tbg-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-tbg-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-uart-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-uart-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-uart-clock.yaml` is a Devicetree binding schema for `Marvell Armada 3720 UART clocks`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,armada-3700-uart-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `marvell,armada-3700-uart-clock`.
- `reg`: 2 positional items.
- `clocks`: List of parent clocks suitable for UART from following set: "TBG-A-P", "TBG-B-P", "TBG-A-S", "TBG-B-S", "xtal" UART clock can use one from this set and when more are provided then kernel would choose and configure the mo.
- `clock-names`: minItems 1; 5 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 59 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `marvell,armada-3700-uart-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-uart-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-3700-uart-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-xp-cpu-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-xp-cpu-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-xp-cpu-clock.yaml` is a Devicetree binding schema for `Marvell EBU CPU Clock`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,armada-xp-cpu-clock`, `marvell,mv98dx3236-cpu-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`, `clocks`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `marvell,armada-xp-cpu-clock`, `marvell,mv98dx3236-cpu-clock`.
- `reg`: 2 positional items.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 44 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `marvell,armada-xp-cpu-clock`, `marvell,mv98dx3236-cpu-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-xp-cpu-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,armada-xp-cpu-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,berlin2-clk.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,berlin2-clk.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,berlin2-clk.yaml` is a Devicetree binding schema for `Marvell Berlin Clock Controller`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,berlin2-clk`, `marvell,berlin2q-clk`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Clock related registers are spread among the chip control registers. Berlin clock node should be a sub-node of the chip controller node. Marvell Berlin2 (BG2, BG2CD, BG2Q) SoCs share the same IP for PLLs and clocks, with some minor differences in features and register layout..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`, `clocks`, `clock-names`. Important properties include `compatible`, `clocks`, `clock-names`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `marvell,berlin2-clk`, `marvell,berlin2q-clk`.
- `clocks`: maxItems 1.
- `clock-names`: 1 positional items.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 51 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `marvell,berlin2-clk`, `marvell,berlin2q-clk`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,berlin2-clk.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,berlin2-clk.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,cp110-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,cp110-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,cp110-clock.yaml` is a Devicetree binding schema for `Marvell Armada CP110 System Controller Clocks`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,cp110-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The CP110 is one of the two core HW blocks of the Marvell Armada 7K/8K/931x SoCs. It contains system controllers, which provide several registers giving access to numerous features: clocks, pin-muxing and many other SoC configuration items..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `#clock-cells`. Important properties include `compatible`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `2`; The first cell must be 0 or 1. 0 for the core clocks and 1 for the gateable clocks. The second cell identifies the particular core clock or gateable clocks. The following clocks are available: - Core clocks - 0 0 APLL - ; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `marvell,cp110-clock`.
- `#clock-cells`: const `2`; The first cell must be 0 or 1. 0 for the core clocks and 1 for the gateable clocks. The second cell identifies the particular core clock or gateable clocks. The following clocks are available: - Core clocks - 0 0 APLL - .

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 70 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling.

### Integration Points
Integration is through compatible matching for `marvell,cp110-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,cp110-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,cp110-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,dove-divider-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,dove-divider-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,dove-divider-clock.yaml` is a Devicetree binding schema for `Marvell Dove PLL Divider Clock`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,dove-divider-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Marvell Dove has a 2GHz PLL, which feeds into a set of dividers to provide high speed clocks for a number of peripherals. These dividers are part of the PMU, and thus this node should be a child of the PMU node. The following clocks are provided: ID Clock ------------- 0 AXI bus clock 1 GPU clock 2 VMeta clock 3 LCD clock.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `marvell,dove-divider-clock`.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 50 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `marvell,dove-divider-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,dove-divider-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,dove-divider-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mmp2-audio-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mmp2-audio-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mmp2-audio-clock.yaml` is a Devicetree binding schema for `Marvell MMP2 Audio Clock Controller`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,mmp2-audio-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The audio clock controller generates and supplies the clocks to the audio codec. Each clock is assigned an identifier and client nodes use this identifier to specify the clock which they consume. All these identifiers could be found in <dt-bindings/clock/marvell,mmp2-audio.h>..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `power-domains`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `marvell,mmp2-audio-clock`.
- `reg`: maxItems 1.
- `clocks`: 4 positional items.
- `clock-names`: 4 positional items.
- `#clock-cells`: const `1`.
- `power-domains`: maxItems 1.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 75 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/marvell,mmp2-audio.h`, `dt-bindings/clock/marvell,mmp2.h`, `dt-bindings/power/marvell,mmp2.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `marvell,mmp2-audio-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mmp2-audio-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mmp2-audio-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mmp2-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mmp2-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mmp2-clock.yaml` is a Devicetree binding schema for `Marvell MMP2 and MMP3 Clock Controller`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,mmp2-clock`, `marvell,mmp3-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The clock subsystem on MMP2 or MMP3 generates and supplies clock to various controllers within the SoC. Each clock is assigned an identifier and client nodes use this identifier to specify the clock which they consume. All these identifiers could be found in <dt-bindings/clock/marvell,mmp2.h>..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `reg-names`, `#clock-cells`, `#reset-cells`, `#power-domain-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `#reset-cells`, `reg-names`, `#power-domain-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: enum `marvell,mmp2-clock`, `marvell,mmp3-clock`.
- `reg`: 3 positional items.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.
- `reg-names`: 3 positional items.
- `#power-domain-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 69 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/marvell,mmp2.h`, MMIO resource description through `reg`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `marvell,mmp2-clock`, `marvell,mmp3-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mmp2-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,mmp2-clock.yaml -->

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

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,pxa1908.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,pxa1908.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,pxa1908.yaml` is a Devicetree binding schema for `Marvell PXA1908 Clock Controllers`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,pxa1908-apbc`, `marvell,pxa1908-apbcp`, `marvell,pxa1908-mpmu`, `marvell,pxa1908-apmu`, `syscon`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The PXA1908 clock subsystem generates and supplies clock to various controllers within the PXA1908 SoC. The PXA1908 contains numerous clock controller blocks, with the ones currently supported being APBC, APBCP, MPMU and APMU roughly corresponding to internal buses. All these clock identifiers could be found in <include/dt-bindings/marvell,pxa1908.h>..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `#power-domain-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 2 oneOf alternatives.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `#power-domain-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The file also uses conditional or composed schema clauses (`if`/`then`/`else`, `allOf`, `oneOf`, or `anyOf`), so validation can change depending on the selected compatible string or referenced common schema. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 66 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `marvell,pxa1908-apbc`, `marvell,pxa1908-apbcp`, `marvell,pxa1908-mpmu`, `marvell,pxa1908-apmu`, `syscon`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Conditional compatibility rules are easy to weaken accidentally when adding a new SoC variant.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,pxa1908.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell,pxa1908.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell-armada-370-gating-clock.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell-armada-370-gating-clock.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell-armada-370-gating-clock.yaml` is a Devicetree binding schema for `Marvell EBU SoC gating-clock`. It documents and validates clock-provider nodes for Marvell clock infrastructure, with compatible contract `marvell,armada-370-gating-clock`, `marvell,armada-375-gating-clock`, `marvell,armada-380-gating-clock`, `marvell,armada-390-gating-clock`, `marvell,armada-xp-gating-clock`, `marvell,mv98dx3236-gating-clock`, `marvell,dove-gating-clock`, `marvell,kirkwood-gating-clock`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Marvell Armada 370/375/380/385/39x/XP, Dove and Kirkwood allow some peripheral clocks to be gated to save some power. The clock ID is directly mapped to the corresponding clock gating control bit in HW to ease manual clock lookup in datasheet. The following is a list of provided IDs for Armada 370: ID Clock Peripheral ----------------------------------- 0 Audio AC97 Cntrl 1 pex0_en PCIe 0 Clock out 2 pex1_en PCIe 1 C.

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: enum `marvell,armada-370-gating-clock`, `marvell,armada-375-gating-clock`, `marvell,armada-380-gating-clock`, `marvell,armada-390-gating-clock`, `marvell,armada-xp-gating-clock`, `marvell,mv98dx3236-gating-clock`, `marvell,dove-gating-clock`, `marvell,kirkwood-gating-clock`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 227 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `marvell,armada-370-gating-clock`, `marvell,armada-375-gating-clock`, `marvell,armada-380-gating-clock`, `marvell,armada-390-gating-clock`, `marvell,armada-xp-gating-clock`, `marvell,mv98dx3236-gating-clock`, `marvell,dove-gating-clock`, `marvell,kirkwood-gating-clock`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell-armada-370-gating-clock.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/marvell-armada-370-gating-clock.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/maxim,max9485.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/maxim,max9485.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/maxim,max9485.yaml` is a Devicetree binding schema for `Maxim MAX9485 Programmable Audio Clock Generator`. It documents and validates clock-provider nodes for Linux common clock framework and Devicetree clock provider infrastructure, with compatible contract `maxim,max9485`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: Maxim MAX9485 Programmable Audio Clock Generator exposes 4 clocks in total: - MAX9485_MCLKOUT: A gated, buffered output of the input clock of 27 MHz - MAX9485_CLKOUT: A PLL that can be configured to 16 different discrete frequencies - MAX9485_CLKOUT[1,2]: Two gated outputs for MAX9485_CLKOUT MAX9485_CLKOUT[1,2] are children of MAX9485_CLKOUT which upchain all rate set requests..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`. Important properties include `compatible`, `reg`, `clocks`, `clock-names`, `#clock-cells`, `clock-output-names`, `reset-gpios`, `vdd-supply`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: const `maxim,max9485`.
- `reg`: maxItems 1.
- `clocks`: maxItems 1; Input clock. Must provide 27 MHz.
- `clock-names`: 1 positional items.
- `#clock-cells`: const `1`.
- `clock-output-names`: Name of output clocks, as defined in common clock bindings; 4 positional items.
- `reset-gpios`: GPIO descriptor connected to the #RESET input pin.
- `vdd-supply`: A regulator node for Vdd.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 82 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.
`clock-output-names` is descriptive DT data used by providers and debug tooling; consumers should normally use phandles and numeric specifiers rather than depending on names.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/gpio/gpio.h`, MMIO resource description through `reg`, parent clock phandles through `clocks`.

### Integration Points
Integration is through compatible matching for `maxim,max9485`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock output name lists can go stale when hardware outputs are added or reordered; numeric IDs and binding headers must remain authoritative.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/maxim,max9485.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/maxim,max9485.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,apmixedsys.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,apmixedsys.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,apmixedsys.yaml` is a Devicetree binding schema for `MediaTek AP Mixedsys Controller`. It documents and validates clock-provider nodes for MediaTek clock/reset infrastructure, with compatible contract `mediatek,mt6797-apmixedsys`, `mediatek,mt7622-apmixedsys`, `mediatek,mt7981-apmixedsys`, `mediatek,mt7986-apmixedsys`, `mediatek,mt7988-apmixedsys`, `mediatek,mt8135-apmixedsys`, `mediatek,mt8173-apmixedsys`, `mediatek,mt8516-apmixedsys`, `mediatek,mt7623-apmixedsys`, `mediatek,mt2701-apmixedsys`, `syscon`, `mediatek,mt2712-apmixedsys`, and 7 more. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The Mediatek apmixedsys controller provides PLLs to the system. The clock values can be found in <dt-bindings/clock/mt*-clk.h> and <dt-bindings/clock/mediatek,mt*-apmixedsys.h>..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `compatible`, `reg`, `#clock-cells`. Important properties include `compatible`, `reg`, `#clock-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
- `compatible`: 3 oneOf alternatives.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 66 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, DTS examples or descriptions reference `dt-bindings/clock/mt*-clk.h`, `dt-bindings/clock/mediatek,mt*-apmixedsys.h`, MMIO resource description through `reg`.

### Integration Points
Integration is through compatible matching for `mediatek,mt6797-apmixedsys`, `mediatek,mt7622-apmixedsys`, `mediatek,mt7981-apmixedsys`, `mediatek,mt7986-apmixedsys`, `mediatek,mt7988-apmixedsys`, `mediatek,mt8135-apmixedsys`, `mediatek,mt8173-apmixedsys`, `mediatek,mt8516-apmixedsys`, `mediatek,mt7623-apmixedsys`, `mediatek,mt2701-apmixedsys`, `syscon`, `mediatek,mt2712-apmixedsys`, and 7 more, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,apmixedsys.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
- Header-level tests should verify that dt-bindings clock/reset IDs referenced by DTS files match the provider driver's exported clock/reset tables.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,apmixedsys.yaml -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,ethsys.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,ethsys.yaml

### Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,ethsys.yaml` is a Devicetree binding schema for `Mediatek ethsys controller`. It documents and validates clock-provider nodes for MediaTek clock/reset infrastructure, with compatible contract `mediatek,mt2701-ethsys`, `mediatek,mt7622-ethsys`, `mediatek,mt7629-ethsys`, `mediatek,mt7981-ethsys`, `mediatek,mt7986-ethsys`, `mediatek,mt7988-ethsys`, `syscon`, `mediatek,mt7623-ethsys`. The file is declarative YAML consumed by dt-schema and the kernel Devicetree build; it does not implement a runtime clock driver itself. The schema description says: The available clocks are defined in dt-bindings/clock/mt*-clk.h..

### Important APIs, Types, And Functions
The externally visible API is the node contract encoded by JSON-schema properties rather than C functions. Required properties are `reg`, `#clock-cells`, `#reset-cells`. Important properties include `compatible`, `reg`, `#clock-cells`, `#reset-cells`.
`#clock-cells` is constrained as `#clock-cells`: const `1`; this defines how consumers encode clock phandle specifiers.
`#reset-cells` is constrained as `#reset-cells`: const `1`; this defines reset-controller specifiers when the node also exposes resets.
- `compatible`: 2 oneOf alternatives.
- `reg`: maxItems 1.
- `#clock-cells`: const `1`.
- `#reset-cells`: const `1`.

### Control Flow
Validation starts when dt-schema loads the `$id` and applies the Devicetree core meta-schema, then checks the node's `compatible` value, required properties, per-property item counts, and the strict property policy. `additionalProperties` is `False` and `unevaluatedProperties` is `not specified`, so unknown node fields are rejected or tightly constrained. The examples block provides 1 DTS snippet(s), which dt_binding_check compiles against the schema as executable validation fixtures.
At boot, the generated DTB state is consumed by the OF clock provider path: platform code matches the compatible string, maps any `reg` range, obtains parent `clocks` by phandle, and registers one or more common-clock-framework outputs for consumers.

### State And Persistence
The schema has no mutable runtime state; its persistent artifact is the source YAML plus the DTB nodes that pass it. The file contains 55 source lines. Runtime state lives in the matched clock-controller driver and underlying MMIO registers, while persistent configuration such as parent clocks, output names, fixed rates, reset specifiers, and compatible fallbacks is stored in board or SoC DTS files.

### Dependencies
Devicetree core schema, Linux common clock framework, dt-schema tooling, MMIO resource description through `reg`, reset-controller binding conventions.

### Integration Points
Integration is through compatible matching for `mediatek,mt2701-ethsys`, `mediatek,mt7622-ethsys`, `mediatek,mt7629-ethsys`, `mediatek,mt7981-ethsys`, `mediatek,mt7986-ethsys`, `mediatek,mt7988-ethsys`, `syscon`, `mediatek,mt7623-ethsys`, Devicetree source files under `arch/*/boot/dts`, and platform clock drivers under the kernel `drivers/clk` family. Consumers use the node as a clock provider via phandles and `#clock-cells`; if reset cells are present, reset-controller consumers use the same node for reset IDs. The binding also integrates with `make dt_binding_check` for schema-only validation and `make dtbs_check` for checking real board/SoC DTS nodes against this contract.

### Risks
- A mismatch between `#clock-cells` and consumer phandle arguments will pass through DTS authoring until dtbs_check or runtime lookup exposes the error.
- Clock/reset combo nodes need reset ID headers and driver reset registration to stay aligned with the schema.
- Strict property rejection is useful for catching typos, but it also means any legitimate new board property requires a schema update first.

### Test Signals
- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,ethsys.yaml` should validate this schema and its examples.
- Real DTS coverage should be checked with `make dtbs_check` so compatible-specific required properties, parent clocks, reset cells, and register ranges are exercised.
- Driver probe tests or boot logs should confirm that each documented compatible registers the expected clock outputs and that consumers can resolve phandles with the declared cell count.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/clock/mediatek,ethsys.yaml -->

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
