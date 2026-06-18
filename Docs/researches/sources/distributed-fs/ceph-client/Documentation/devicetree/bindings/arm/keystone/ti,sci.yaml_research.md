<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,sci.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,sci.yaml

## Purpose
This schema describes the TI-SCI system controller node used by Keystone/K3 SoCs to communicate with firmware managing clocks, resets, power domains, and other SoC resources.

## Important APIs, Types, And Functions
It validates `system-controller@...`, compatible strings `ti,k2g-sci` or `ti,am654-sci`, optional debug `reg`/`reg-names`, required mailbox names `rx` and `tx`, `mboxes`, optional `ti,host-id`, and child nodes `power-controller`, `clock-controller`, and `reset-controller` via dedicated `$ref`s.

## Control Flow
Validation requires compatible and mailbox wiring, then delegates child validation to the TI SCI PM domain, clock, and reset schemas. `additionalProperties: false` keeps the parent controller strict.

## State And Persistence
The DT stores mailbox endpoints, host identity, optional debug region, and child function nodes. Runtime state is held by the TI-SCI firmware and Linux protocol clients.

## Dependencies And Integration Points
It depends on mailbox providers, secure proxy/message manager nodes, and child schemas under `/schemas/soc/ti`, `/schemas/clock`, and `/schemas/reset`.

## Risks
Reversed mailboxes or wrong host IDs can break all firmware-mediated resources. Optional child nodes must remain compatible with the parent protocol node or subsystem drivers will not bind.

## Test Signals
`dt_binding_check` validates examples and child `$ref`s. Runtime probes of TI-SCI, power domains, clocks, and resets are strong integration signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/arm/keystone/ti,sci.yaml -->
