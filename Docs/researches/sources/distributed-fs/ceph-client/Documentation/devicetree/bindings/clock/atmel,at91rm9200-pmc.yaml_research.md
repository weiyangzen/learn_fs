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
