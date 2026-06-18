<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs/pcs-mtk-lynxi.h -->
# sources/distributed-fs/ceph-client/include/linux/pcs/pcs-mtk-lynxi.h

## Purpose
`include/linux/pcs/pcs-mtk-lynxi.h` declares the MediaTek LynxI PCS factory interface for phylink users. It allows a MediaTek Ethernet driver to create a PCS object from device, firmware node, regmap, and an analog register offset/value selector, then destroy it during teardown.

## Important APIs, Types, and Functions
`mtk_pcs_lynxi_create(struct device *dev, struct fwnode_handle *fwnode, struct regmap *regmap, u32 ana_rgc3)` returns a `struct phylink_pcs *` for the MediaTek LynxI PCS. `mtk_pcs_lynxi_destroy(struct phylink_pcs *pcs)` releases it. The API exposes `regmap` because the PCS implementation shares register access with a parent system controller or Ethernet block, and `ana_rgc3` identifies the analog control register context needed by the implementation.

## Control Flow
A MediaTek MAC driver builds or obtains its `regmap`, locates firmware data, calls `mtk_pcs_lynxi_create()` during probe, attaches the returned PCS to phylink, and calls `mtk_pcs_lynxi_destroy()` after detaching phylink or on probe failure. Runtime link setup flows through the returned `phylink_pcs` operations.

## State and Persistence Behavior
The header stores no state. The created PCS object persists across the network device lifetime and likely retains references or pointers to device, firmware node/regmap context, and register offsets. Lifetime and ordering are caller-managed.

## Dependencies and Integration Points
The header includes `linux/phylink.h` and `linux/regmap.h`, integrating with phylink, firmware-node based hardware description, regmap-backed register access, and MediaTek Ethernet drivers.

## Risks
Passing the wrong `regmap` or `ana_rgc3` value can direct PCS operations at the wrong registers. Destroying the PCS before phylink is detached can leave callbacks with stale state. As with other PCS factory headers, error-return conventions must be followed from the implementation.

## Test Signals
Build coverage for MediaTek Ethernet users, probe/remove with valid firmware data, phylink link-mode changes, autonegotiation behavior, register access tracing for expected `regmap` offsets, suspend/resume where applicable, and leak/error-path tests around create/destroy are useful signals.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/pcs/pcs-mtk-lynxi.h -->
