<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-i2c.h -->
# sources/distributed-fs/ceph-client/include/linux/mdio/mdio-i2c.h

## Purpose
This header defines the MDIO-over-I2C bridge allocation API.

## Important APIs, types, and functions
`enum mdio_i2c_proto` identifies supported bridge protocols: none, Marvell Clause 22, Clause 45, and RollBall. `mdio_i2c_alloc()` creates an unregistered `mii_bus` backed by an I2C adapter and selected protocol.

## Control flow
A driver calls `mdio_i2c_alloc()` with parent device, I2C adapter, and protocol, then registers the returned MDIO bus with phylib. MDIO transactions are translated into I2C operations by the implementation.

## State and persistence
The header stores no state. Runtime bus state is in the allocated `mii_bus`; target PHY state persists in hardware.

## Dependencies and integration points
It integrates I2C adapters with MDIO/phylib consumers, especially SFP modules and PHYs behind protocol-specific I2C management bridges.

## Risks and test signals
Risks include selecting the wrong protocol, adapter lifetime bugs, unsupported Clause 45 access, and I2C transfer failures surfacing as MDIO errors. Test allocation failure, each protocol variant, bus register/unregister, PHY ID reads, and I2C error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/mdio/mdio-i2c.h -->
