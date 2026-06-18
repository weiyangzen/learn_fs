# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml`, a YAML devicetree binding titled "SMSC USB3503 High-Speed Hub Controller". It is a USB hub binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `smsc,usb3503.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Dongjin Kim <tobetter@gmail.com>.

## Important APIs, Types, And Schema Surface
Accepts 3 compatible string(s): `smsc,usb3503`, `smsc,usb3503a`, `smsc,usb3803`.

Required top-level fields: `compatible`.

Primary declared properties:
- `compatible`: enum `smsc,usb3503`, `smsc,usb3503a`, `smsc,usb3803`
- `reg`: items ?..1
- `connect-gpios`: items ?..1; GPIO for connect
- `intn-gpios`: items ?..1; GPIO for interrupt
- `reset-gpios`: items ?..1; GPIO for reset
- `bypass-gpios`: items ?..1; GPIO for bypass. Control signal to select between HUB MODE and BYPASS MODE.
- `disabled-ports`: refers to `/schemas/types.yaml#/definitions/uint32-array`; items 1..3; Specifies the ports unused using their port number. Do not describe this property if all ports have to be enabled.
- `initial-mode`: refers to `/schemas/types.yaml#/definitions/uint32`; Specifies initial mode. 1 for Hub mode, 2 for standby mode and 3 for bypass mode. In bypass mode the downstream port 3 is conne...
- `clocks`: items ?..1; Clock used for driving REFCLK signal. If not provided the driver assumes that clock signal is always available, its rate is spe...
- `clock-names`: constant `refclk`
- `refclk-frequency`: refers to `/schemas/types.yaml#/definitions/uint32`; Frequency of the REFCLK signal as defined by REF_SEL pins. If not provided, driver will not set rate of the REFCLK signal and a...

External schema dependencies: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

The schema contains 2 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 3 inline example block(s), including node(s) `usb-hub@8, `i2c, `usb-hub@8, `usb-hub`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/smsc,usb3503.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 11 top-level declared propert(ies), 1 required field(s), 2 external reference(s), and 2 conditional branch(es).
