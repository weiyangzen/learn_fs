<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/net/can/can-transceiver.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/net/can/can-transceiver.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/net/can/can-transceiver.yaml` defines the CAN transceiver binding titled `CAN transceiver`. CAN transceiver generic properties bindings It is a Linux Devicetree YAML schema used to validate DTS/DTB nodes and to document the firmware ABI consumed before the kernel creates the corresponding CAN network device.

## Important APIs, Types, and Functions
The public interface is the YAML/dt-schema ABI, not C-callable functions. `compatible` uses a composed compatible schema with 0 tokens: no directly declared compatible constants. Top-level properties are `max-bitrate`. Top-level required properties are none declared; required keys found in nested schemas include none. Pattern properties are none. Collected numeric/item constraints include `minimum=1`. The highest-risk API details are clock and interrupt ordering, `can-transceiver` links, bit-rate capability properties, controller-specific compatible fallbacks, register windows, and optional timestamp/DMA resources. Important property roles: `max-bitrate` models CAN controller or transceiver capability.

## Control Flow
Control flow is declarative schema evaluation. During `make dt_binding_check` or `make dtbs_check`, dt-schema loads the YAML, resolves `$ref` entries, matches by `$id`, `$nodename`, `compatible`, or fragment inclusion, checks required properties, evaluates no top-level conditionals, validates examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the YAML itself does not execute. Firmware provides a DTB node for the CAN transceiver binding; Linux driver core or bus code matches a driver, then subsystem helpers consume the validated resources. Child schemas such as `ports`, `ethernet-ports`, MDIO children, or CAN transceiver links guide later parsing by DSA, phylink, PHYLIB, Bluetooth, or SocketCAN drivers.

## State and Persistence Behavior
The schema stores no mutable kernel state and writes no persistent data. Persistence is the Devicetree ABI: compatible strings, property names, array order, phandle cell counts, child-node names, and example layouts are contracts carried by DTS sources and deployed DTBs. Runtime state is owned by drivers after probe, including netdev registration, bit-timing programming, bus-off/error counters, transceiver enablement, RX/TX mailboxes, and SocketCAN state; this file only constrains how hardware and board wiring are represented.

## Dependencies and Integration Points
Maintainers listed: Rob Herring <robh@kernel.org>. Direct schema dependencies are `/schemas/types.yaml#/definitions/uint32`. Integration points include the Linux CAN and SocketCAN stack, platform/SPI controllers, clocks, resets, interrupt controllers, transceiver phandles, regulator supplies, pinctrl, and board DTS CAN nodes. The binding participates in schema example extraction, Linux OF matching, and board DTS validation. Compatible scan found driver-side files: no direct in-tree driver match found by compatible scan. In-tree DTS users found by compatible scan: no in-tree DTS user found by compatible scan. The file contains 0 embedded examples.

## Risks
Primary risks are incompatible ABI changes to clock and interrupt ordering, `can-transceiver` links, bit-rate capability properties, controller-specific compatible fallbacks, register windows, and optional timestamp/DMA resources, mismatches between documented compatibles and driver OF match tables, resource-order changes that pass schema review but break probe, and stale examples. This schema permits extra top-level properties. Additional risk signals: CAN timing and transceiver capability units must match driver expectations.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/net/can/can-transceiver.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/net/can/can-transceiver.yaml` against affected board DTS files. The schema has 0 example blocks, so example compilation is part of the signal. Review every compatible against driver `of_match_table` entries and exercise negative schema cases for missing required resources, bad child names, wrong `reg` values, and misspelled vendor properties. Runtime signals are CAN interface registration, loopback or bus traffic tests, bus-off recovery, interrupt delivery, and transceiver enable tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/net/can/can-transceiver.yaml -->
