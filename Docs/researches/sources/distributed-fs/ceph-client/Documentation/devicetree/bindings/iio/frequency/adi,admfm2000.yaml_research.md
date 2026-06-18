<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml

### Purpose
`adi,admfm2000.yaml` defines the devicetree schema for ADMFM2000 Dual Microwave Down Converter. It is an IIO frequency binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. The schema description adds: Dual microwave down converter module with input RF and LO frequency ranges from 0.5 to 32 GHz and an output IF frequency range from 0.1 to 8 GHz. It consists of a LNA, mixer, IF filter, DSA, and IF amplifier for each down conversion path. Maintainer coverage is Kim Seer Paller <kimseer.paller@analog.com>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/frequency/adi,admfm2000.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `adi,admfm2000`. Top-level required properties are `compatible`. Important property contracts include: `#address-cells` (const `1`); `#size-cells` (const `0`)
Child-node API is expressed through `patternProperties`: `^channel@[0-1]$` (Represents a channel of the device.); required `reg`, `switch-gpios`, `attenuation-gpios`.
Local reusable definitions are none. Provider or bus cell contracts are `#address-cells` (const `1`); `#size-cells` (const `0`).

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are no external `$ref` entries. Integration hints from the schema and examples are: standard devicetree node matching. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO frequency drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Nested child-node schemas add risk because missing `#address-cells`, `#size-cells`, `reg`, or phandle links can pass local review but fail dtbs_check for real boards. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/frequency/adi,admfm2000.yaml -->
