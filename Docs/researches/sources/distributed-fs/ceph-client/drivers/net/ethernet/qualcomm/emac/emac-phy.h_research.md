# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-phy.h

### Purpose
`emac-phy.h` declares the Qualcomm EMAC PHY configuration entry point.

### Important APIs, Types, And Functions
It forward-declares `struct emac_adapter` and declares `int emac_phy_config(struct platform_device *pdev, struct emac_adapter *adpt);`.

### Control Flow
The header has no executable control flow. It allows the core EMAC driver to call PHY/MDIO setup without exposing MDIO register details.

### State, Persistence, And Dependencies
No state is stored here. The declaration depends on `struct platform_device` being visible through surrounding includes, and `emac_adapter` is intentionally forward-declared to avoid pulling in the full adapter definition.

### Integration Points
`emac.h` includes this header, making `emac_phy_config()` available to the platform driver and tying the PHY implementation into the single `qcom-emac` object.

### Risks
Because this header omits a direct platform-device include, include order matters. Any signature change must be reflected in `emac-phy.c` and all callers.

### Test Signals
Build coverage is the main signal: compile EMAC with normal configs, include-order changes, and static analysis to ensure the prototype matches the implementation.
