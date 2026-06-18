<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml -->
## sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml

### Purpose
`invensense,mpu3050.yaml` defines the devicetree schema for Invensense MPU-3050 Gyroscope. It is an IIO gyroscope binding under the Linux IIO devicetree bindings: it validates DTS/DTB nodes and documents the firmware ABI consumed by Linux drivers, but it does not contain executable runtime code. Maintainer coverage is Linus Walleij <linusw@kernel.org>.

### Important APIs, Types, And Functions
The exported interface is the YAML/dt-schema contract rather than C functions. The schema id is `http://devicetree.org/schemas/iio/gyroscope/invensense,mpu3050.yaml#` and the meta-schema is `http://devicetree.org/meta-schemas/core.yaml#`. Compatible matching covers `invensense,mpu3050`. Top-level required properties are `compatible`, `reg`. Important property contracts include: `reg` (max 1 item(s)); `vdd-supply` allowed with common binding semantics; `vlogic-supply` allowed with common binding semantics; `interrupts` (max 1 item(s); Interrupt mapping for the trigger interrupt from the internal oscillator.); `mount-matrix` allowed with common binding semantics; `i2c-gate` (ref `/schemas/i2c/i2c-controller.yaml`; The MPU-3050 will pass through and forward the I2C signals from the incoming I2C bus, alternatively drive traffic to...)
No child-node `patternProperties` are declared, so validation focuses on the device node itself and shared bus/provider properties.
Local reusable definitions are none. Provider or bus cell contracts are no provider cell property at top level.

### Control Flow
During `make dt_binding_check`, dt-schema parses this file, validates it against the core meta-schema, compiles the 1 example block(s), and checks that node properties satisfy the compatible selector, `required` list, item-count limits, enums, numeric ranges, and referenced common schemas. Runtime boot flow is indirect: firmware supplies a node with one of the compatibles, the relevant Linux IIO or support driver matches it through its OF table, then consumes validated resources such as `reg`, clocks, interrupts, GPIOs, supplies, and vendor tuning properties. This schema has 0 top-level `allOf` entry(s), 0 conditional `if` branch(es), 0 `oneOf` occurrence(s), and 0 `anyOf` occurrence(s), so variant-specific behavior is handled declaratively before driver probe.

### State, Persistence, And Dependencies
The file persists no kernel state. Its durable state is the devicetree ABI: compatible strings, property names, cell counts, child-node names, and allowed numeric/string values that board DTS files and firmware DTBs may carry for years. Dependencies are `/schemas/i2c/i2c-controller.yaml`. Integration hints from the schema and examples are: I2C; interrupt-capable; regulator supplies: `vdd-supply`, `vlogic-supply`. Unknown property handling uses `unevaluatedProperties: false`, so adding board-specific fields generally requires a binding update rather than ad-hoc DTS data.

### Integration Points
This binding integrates with Linux IIO gyroscope drivers, board `.dts`/SoC `.dtsi` files, bus controllers, regulator/clock/GPIO/interrupt providers, and dt-schema shared bindings. Device-tree authors must keep property order and naming aligned with the driver lookups, especially for resource arrays such as `reg`, `clocks`, `clock-names`, `interrupts`, GPIO lists, child sensor/channel nodes, and Analog Devices/TI/Bosch/etc. vendor properties. The reconciliation target for this research is `Docs/researches/sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml_research.md`.

### Risks
Primary risk is ABI drift: removing a compatible, tightening a range, changing a `required` property, or altering provider cell counts can break existing DTS files or bootloader-provided DTBs even when the driver still works. Compatible aliases and fallback `items`/`oneOf` forms need review so older silicon names keep matching the intended driver path. Examples can also go stale when shared bindings, include paths, or driver resource requirements change.

### Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml` in a kernel tree with dt-schema installed to validate the schema and compile its examples. Run `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml` against affected board DTS files to verify real nodes. Review signals include every compatible having an intentional driver or legacy match, all required resources appearing in examples, referenced schemas resolving, `unevaluatedProperties` behavior rejecting typos, and unit-bearing vendor properties matching driver parsing and datasheet units.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/iio/gyroscope/invensense,mpu3050.yaml -->
