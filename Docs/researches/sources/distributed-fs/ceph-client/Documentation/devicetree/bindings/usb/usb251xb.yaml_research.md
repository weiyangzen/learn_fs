# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml`, a YAML devicetree binding titled "Microchip USB 2.0 Hi-Speed Hub Controller". It is a USB hub binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `usb251xb.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Richard Leitner <richard.leitner@skidata.com>.

## Important APIs, Types, And Schema Surface
Accepts 10 compatible string(s): `microchip,usb2422`, `microchip,usb2512b`, `microchip,usb2512bi`, `microchip,usb2513b`, `microchip,usb2513bi`, `microchip,usb2514b`, `microchip,usb2514bi`, `microchip,usb2517`, `microchip,usb2517i`, `microchip,usb251xb`.

Required top-level fields: `compatible`.

Primary declared properties:
- `compatible`: enum `microchip,usb2422`, `microchip,usb2512b`, `microchip,usb2512bi`, `microchip,usb2513b`, `microchip,usb2513bi`, `microchip,usb2514b`, `microchip,usb2514bi`, `microchip,usb2517`...
- `reg`: items ?..1
- `reset-gpios`: Should specify the gpio for hub reset
- `vdd-supply`: Should specify the phandle to the regulator supplying vdd
- `skip-config`: refers to `/schemas/types.yaml#/definitions/flag`; Skip Hub configuration, but only send the USB-Attach command
- `vendor-id`: refers to `/schemas/types.yaml#/definitions/uint16`; default `1060`; Set USB Vendor ID of the hub
- `product-id`: refers to `/schemas/types.yaml#/definitions/uint16`; Set USB Product ID of the hub
- `device-id`: refers to `/schemas/types.yaml#/definitions/uint16`; default `2995`; Set USB Device ID of the hub
- `language-id`: refers to `/schemas/types.yaml#/definitions/uint16`; default `0`; Set USB Language ID
- `manufacturer`: refers to `/schemas/types.yaml#/definitions/string`; Set USB Manufacturer string (max 31 characters long)
- `product`: refers to `/schemas/types.yaml#/definitions/string`; Set USB Product string (max 31 characters long)
- `serial`: refers to `/schemas/types.yaml#/definitions/string`; Set USB Serial string (max 31 characters long)
- `bus-powered`: refers to `/schemas/types.yaml#/definitions/flag`; selects between self- and bus-powered operation (boolean, default is self-powered)
- `self-powered`: refers to `/schemas/types.yaml#/definitions/flag`; selects between self- and bus-powered operation (boolean, default is self-powered)
- `disable-hi-speed`: refers to `/schemas/types.yaml#/definitions/flag`; disable USB Hi-Speed support (boolean)
- `multi-tt`: refers to `/schemas/types.yaml#/definitions/flag`; selects between multi- and single-transaction-translator (boolean, default is multi-tt)
- `single-tt`: refers to `/schemas/types.yaml#/definitions/flag`; selects between multi- and single-transaction-translator (boolean, default is multi-tt)
- `disable-eop`: refers to `/schemas/types.yaml#/definitions/flag`; disable End of Packet generation in full-speed mode (boolean)
- Additional declared properties include `ganged-sensing`, `individual-sensing`, `ganged-port-switching`, `individual-port-switching`, `dynamic-power-switching`, `oc-delay-us`, `compound-device`, `port-mapping-mode`, `led-usb-mode`, `led-speed-mode`, `string-support`, `non-removable-ports`, `sp-disabled-ports`, `bp-disabled-ports`, `sp-max-total-current-microamp`, `bp-max-total-current-microamp`, ...

External schema dependencies: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint16`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8-array`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint16`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8-array`.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: false` closes the top-level node after declared properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint16`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8-array`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
Contains 2 inline example block(s), including node(s) `i2c, `usb-hub@2c, `usb-hub@2d, `usb-hub`.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- Adding a new DTS user should use one of the documented compatible strings or update this schema in the same change.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/usb251xb.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 38 top-level declared propert(ies), 1 required field(s), 5 external reference(s), and 0 conditional branch(es).
