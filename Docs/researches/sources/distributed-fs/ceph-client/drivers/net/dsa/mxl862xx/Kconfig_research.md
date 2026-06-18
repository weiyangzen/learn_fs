# sources/distributed-fs/ceph-client/drivers/net/dsa/mxl862xx/Kconfig

## Purpose
Adds the kernel configuration option for the MaxLinear MxL862xx DSA switch driver.

## Important APIs, Types, and Functions
Defines `config NET_DSA_MXL862` as a tristate named "MaxLinear MxL862xx". It depends on `NET_DSA` and selects `CRC16` and `NET_DSA_TAG_MXL_862XX`.

## Control Flow and State
No runtime logic. Build-time state determines whether the driver is omitted, built-in, or modular, and ensures required CRC and tag-protocol support are selected.

## Dependencies and Integration Points
Integrates with the kernel Kconfig tree under DSA drivers. The selected tag protocol is required for packets between CPU and switch ports, while CRC16 is used by the host command transport.

## Risks and Test Signals
Risks include missing dependencies for MDIO/PHY features in other files or selecting a tagger that is not present. Test signals include `oldconfig`, built-in and module builds, and runtime DSA probe with MxL86252/MxL86282 hardware.
