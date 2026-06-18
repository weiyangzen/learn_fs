<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/net/brcm,bcm6368-mdio-mux.yaml -->
# sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/net/brcm,bcm6368-mdio-mux.yaml

## Purpose
`sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/net/brcm,bcm6368-mdio-mux.yaml` defines the MDIO bus or MDIO mux binding titled `Broadcom BCM6368 MDIO bus multiplexer`. This MDIO bus multiplexer defines buses that could be internal as well as external to SoCs. It is a Linux Devicetree YAML schema used to validate DTS/DTB nodes and to document the firmware ABI consumed before the kernel creates the corresponding MDIO controller or mux.

## Important APIs, Types, and Functions
The public interface is the YAML/dt-schema ABI, not C-callable functions. `compatible` uses a single `const` with 1 token: `brcm,bcm6368-mdio-mux`. Top-level properties are `compatible`, `reg`. Top-level required properties are `compatible`, `reg`; required keys found in nested schemas include `compatible`, `reg`. Pattern properties are none. Collected numeric/item constraints include `maxItems=1`. The highest-risk API details are child bus address cells, mux child selection, register windows, clock/reset requirements, compatible fallbacks, and PHY node validation. Important property roles: `compatible` selects the OF match table and stable hardware ABI; `reg` carries MMIO ranges, bus addresses, chip selects, or switch port indexes.

## Control Flow
Control flow is declarative schema evaluation. During `make dt_binding_check` or `make dtbs_check`, dt-schema loads the YAML, resolves `$ref` entries, matches by `$id`, `$nodename`, `compatible`, or fragment inclusion, checks required properties, evaluates `allOf`, validates examples, and enforces `additionalProperties` or `unevaluatedProperties`. At runtime the YAML itself does not execute. Firmware provides a DTB node for the MDIO bus or MDIO mux binding; Linux driver core or bus code matches a driver, then subsystem helpers consume the validated resources. Child schemas such as `ports`, `ethernet-ports`, MDIO children, or CAN transceiver links guide later parsing by DSA, phylink, PHYLIB, Bluetooth, or SocketCAN drivers.

## State and Persistence Behavior
The schema stores no mutable kernel state and writes no persistent data. Persistence is the Devicetree ABI: compatible strings, property names, array order, phandle cell counts, child-node names, and example layouts are contracts carried by DTS sources and deployed DTBs. Runtime state is owned by drivers after probe, including MDIO bus registration, mux selection state, PHY discovery, link status polling, and PHY register access; this file only constrains how hardware and board wiring are represented.

## Dependencies and Integration Points
Maintainers listed: Alvaro Fernandez Rojas <noltari@gmail.com>. Direct schema dependencies are `mdio-mux.yaml#`. Integration points include MDIO bus registration, PHYLIB, phylink, Ethernet MAC drivers, child PHY nodes, syscon/regmap helpers where referenced, clocks/resets, and board DTS bus topology. The binding participates in schema example extraction, Linux OF matching, and board DTS validation. Compatible scan found driver-side files: `sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm6368.c`. In-tree DTS users found by compatible scan: no in-tree DTS user found by compatible scan. The file contains 1 embedded example.

## Risks
Primary risks are incompatible ABI changes to child bus address cells, mux child selection, register windows, clock/reset requirements, compatible fallbacks, and PHY node validation, mismatches between documented compatibles and driver OF match tables, resource-order changes that pass schema review but break probe, and stale examples. This schema closes composed schemas with `unevaluatedProperties: false`. Additional risk signals: conditional branches can validate one silicon variant while rejecting another.

## Test Signals
Run `make dt_binding_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/net/brcm,bcm6368-mdio-mux.yaml` for targeted schema validation and `make dtbs_check DT_SCHEMA_FILES=Documentation/devicetree/bindings/net/brcm,bcm6368-mdio-mux.yaml` against affected board DTS files. The schema has 1 example block, so example compilation is part of the signal. Review every compatible against driver `of_match_table` entries and exercise negative schema cases for missing required resources, bad child names, wrong `reg` values, and misspelled vendor properties. Runtime signals are PHY discovery, mux channel switching, phylink attachment, and real-board link polling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/Documentation/devicetree/bindings/net/brcm,bcm6368-mdio-mux.yaml -->
