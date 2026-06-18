<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs-rzn1-miic.h -->
# sources/distributed-fs/ceph-client/include/linux/pcs-rzn1-miic.h

## Purpose
`include/linux/pcs-rzn1-miic.h` declares helpers for the Renesas RZ/N1 MIIC PCS implementation. It exposes a small create/destroy interface that lets a MAC or platform driver instantiate a phylink PCS from a device and device-tree node.

## Important APIs, Types, and Functions
`miic_create(struct device *dev, struct device_node *np)` creates a `struct phylink_pcs` associated with the given device and device-tree node. `miic_destroy(struct phylink_pcs *pcs)` releases the created PCS object. The header forward-declares `struct phylink` and `struct device_node`; it uses `struct device` without an explicit local include, relying on includers or implementation context to provide it.

## Control Flow
During probe, a Renesas networking driver locates the MIIC node, calls `miic_create()`, wires the returned PCS into phylink, and destroys it on remove or probe failure. Runtime link configuration and state reporting are delegated through phylink PCS methods implemented outside this header.

## State and Persistence Behavior
No state is stored in the header. The PCS instance created by `miic_create()` persists until `miic_destroy()`. The caller owns lifetime sequencing relative to phylink registration and network device teardown.

## Dependencies and Integration Points
The interface integrates with the phylink subsystem, OF/device-tree descriptions, Renesas RZ/N1 MIIC hardware support, and MAC drivers that need a PCS object separate from the Ethernet MAC. It likely pairs with DT bindings under `include/dt-bindings/net/pcs-rzn1-miic.h` and the corresponding driver implementation.

## Risks
Risks include missing forward declaration or include coverage for `struct device` in unusual include orders, invalid device-tree nodes, mismatched create/destroy ownership, and phylink callbacks racing teardown. The interface is minimal, so consumers must rely on implementation behavior for error returns and supported link modes.

## Test Signals
Build tests for all MIIC users catch include-order issues. Runtime tests should cover probe from valid and invalid device-tree nodes, phylink attach/detach, interface mode transitions supported by MIIC, link up/down reporting, module or platform-driver remove, and probe-error unwinding.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs-rzn1-miic.h -->
