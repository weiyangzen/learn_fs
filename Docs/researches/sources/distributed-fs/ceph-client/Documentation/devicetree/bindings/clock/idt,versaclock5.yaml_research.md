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
