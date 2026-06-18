# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml

## Scope
This report covers `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml`, a YAML devicetree binding titled "Synopsys DesignWare USB3 Controller common properties". It is a USB host/controller binding; its executable behavior is the dt-schema validation contract consumed by kernel binding checks and by DTS authors, not runtime C code.

## Purpose
The schema documents and validates the hardware description for `snps,dwc3-common.yaml` nodes. It constrains compatible strings, register ranges, interrupts, clocks, supplies, graph ports, child nodes, and vendor-specific knobs so the matching Linux driver can discover hardware resources through Open Firmware/devicetree APIs. Maintainer ownership is Felipe Balbi <balbi@kernel.org>.

## Important APIs, Types, And Schema Surface
No direct compatible list is declared here; matching is inherited or pattern-based.

Required top-level fields: `compatible`, `reg`.

Primary declared properties:
- `extcon`: items ?..1; deprecated
- `usb-phy`: items 1..?
- `phys`: items 1..19
- `phy-names`: items 1..19
- `snps,usb2-lpm-disable`: type `boolean`; Indicate if we don't want to enable USB2 HW LPM for host mode.
- `snps,usb3_lpm_capable`: type `boolean`; Determines if platform is USB3 LPM capable
- `snps,usb2-gadget-lpm-disable`: type `boolean`; Indicate if we don't want to enable USB2 HW LPM for gadget mode.
- `snps,reserved-endpoints`: refers to `/schemas/types.yaml#/definitions/uint8-array`; items 1..30; Reserve endpoints for other needs, e.g, for tracing control and output. When set, the driver will avoid using them for the regu...
- `snps,dis-start-transfer-quirk`: type `boolean`; When set, disable isoc START TRANSFER command failure SW work-around for DWC_usb31 version 1.70a-ea06 and prior.
- `snps,disable_scramble_quirk`: type `boolean`; True when SW should disable data scrambling. Only really useful for FPGA builds.
- `snps,has-lpm-erratum`: type `boolean`; True when DWC3 was configured with LPM Erratum enabled
- `snps,lpm-nyet-threshold`: refers to `/schemas/types.yaml#/definitions/uint8`; LPM NYET threshold
- `snps,u2exit_lfps_quirk`: type `boolean`; Set if we want to enable u2exit lfps quirk
- `snps,u2ss_inp3_quirk`: type `boolean`; Set if we enable P3 OK for U2/SS Inactive quirk
- `snps,req_p1p2p3_quirk`: type `boolean`; When set, the core will always request for P1/P2/P3 transition sequence.
- `snps,del_p1p2p3_quirk`: type `boolean`; When set core will delay P1/P2/P3 until a certain amount of 8B10B errors occur.
- `snps,del_phy_power_chg_quirk`: type `boolean`; When set core will delay PHY power change from P0 to P1/P2/P3.
- `snps,lfps_filter_quirk`: type `boolean`; When set core will filter LFPS reception.
- Additional declared properties include `snps,rx_detect_poll_quirk`, `snps,tx_de_emphasis_quirk`, `snps,tx_de_emphasis`, `snps,dis_u3_susphy_quirk`, `snps,dis_u2_susphy_quirk`, `snps,dis_enblslpm_quirk`, `snps,dis-u1-entry-quirk`, `snps,dis-u2-entry-quirk`, `snps,dis_rxdet_inp3_quirk`, `snps,dis-u2-freeclk-exists-quirk`, `snps,dis-del-phy-power-chg-quirk`, `snps,dis-tx-ipgap-linecheck-quirk`, `snps,parkmode-disable-ss-quirk`, `snps,parkmode-disable-hs-quirk`, `snps,dis_metastability_quirk`, `snps,dis-split-quirk`, ...

External schema dependencies: `/schemas/connector/usb-connector.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8`, `/schemas/types.yaml#/definitions/uint8-array`, `usb-drd.yaml#`, `usb-xhci.yaml#`, `usb.yaml#`.

## Control Flow
Validation is declarative: dt-schema selects the document by `$id`, `select`, `compatible`, or include context, then evaluates `properties`, `required`, and closure rules against DTS nodes.

Referenced schemas extend validation through `/schemas/connector/usb-connector.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8`, and 4 more.

The schema contains 1 conditional branch(es); these specialize clock, interrupt, reset, role, or compatible requirements for particular SoC/device variants.

In kernel runtime terms, the control flow is: firmware exposes a node matching this schema, platform/USB/virtio/w1/watchdog discovery matches the `compatible` value or bus ID, the driver reads resources named here with OF helpers, and subsystem registration proceeds only if mandatory resources are present and coherent.

## State And Persistence Behavior
The file is persistent source-controlled schema state. It does not store runtime device state, but it defines the persistent ABI between DTS files, firmware, bootloaders, and Linux drivers. Changes to compatible strings, required properties, item ordering, or closure rules affect long-lived DTBs and must preserve backwards compatibility unless a binding is explicitly deprecated.

`additionalProperties: true` intentionally leaves room for inherited PCI/USB/device properties.

## Dependencies And Integration Points
The binding integrates with the devicetree core meta-schema through `$schema`, with its `$id` namespace, and with `make dt_binding_check` / `make dtbs_check`. Schema references are: `/schemas/connector/usb-connector.yaml#`, `/schemas/graph.yaml#/properties/port`, `/schemas/graph.yaml#/properties/ports`, `/schemas/types.yaml#/definitions/flag`, `/schemas/types.yaml#/definitions/string`, `/schemas/types.yaml#/definitions/uint32`, `/schemas/types.yaml#/definitions/uint32-array`, `/schemas/types.yaml#/definitions/uint8`, `/schemas/types.yaml#/definitions/uint8-array`, `usb-drd.yaml#`, `usb-xhci.yaml#`, `usb.yaml#`.

USB integration points include the USB core, xHCI/DWC3/MUSB/host-controller or Type-C connector subsystems as applicable, graph endpoint links for role/orientation/mode switching when present, PHY/regulator/clock/reset providers, and board DTS files that instantiate the controller, hub, switch, or connector.

## Risks And Edge Cases
- Conditional branches are easy to regress when adding a new compatible because clock, interrupt, reset, supply, or fallback requirements may need variant-specific updates.
- Referenced schemas can tighten validation independently; changes in common USB, graph, connector, PCI, or watchdog schemas may make this binding stricter without local edits.
- Removing or reordering required resource arrays can break existing drivers that index clocks, interrupts, registers, PHYs, or supplies by position/name.

## Test Signals
No inline DTS example is present; validation depends on in-tree DTS users and dt_binding_check schema compilation.

- `make dt_binding_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml` should compile this schema and validate inline examples.
- `make dtbs_check DT_SCHEMA_FILES=sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml` should validate real DTS users against this binding.
- YAML parsing should preserve `$id`, `$schema`, `maintainers`, `properties`, `required`, and closure keywords without duplicate-key warnings.
- Referenced schemas should be available in the binding tree so local `$ref` resolution does not fail.
- For each new compatible, run dtbs_check on at least one DTS that exercises the relevant conditional branch.

## Notes For Future Changes
Treat `sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/usb/snps,dwc3-common.yaml` as ABI documentation. Prefer additive compatibles/properties, keep examples synchronized with required fields, and use common schemas instead of duplicating generic USB/virtio/w1/watchdog rules. The current schema has 58 top-level declared propert(ies), 2 required field(s), 12 external reference(s), and 1 conditional branch(es).
