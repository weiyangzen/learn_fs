# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ixgbevf/Makefile

## Purpose
This Makefile defines how the Intel 82599 VF ethernet driver object is built by Kbuild.

## Important APIs and build rules
- `obj-$(CONFIG_IXGBEVF) += ixgbevf.o` builds the VF driver when the main config option is enabled.
- `ixgbevf-y := vf.o mbx.o ethtool.o ixgbevf_main.o` defines the always-linked objects.
- `ixgbevf-$(CONFIG_IXGBEVF_IPSEC) += ipsec.o` conditionally links IPsec offload support.

## Control flow and integration
Kbuild aggregates the listed objects into `ixgbevf.o`. Runtime entry points come from `ixgbevf_main.o`, with hardware support in `vf.o`, mailbox support in `mbx.o`, ethtool support in `ethtool.o`, and optional XFRM/IPsec offload in `ipsec.o`.

## State and persistence behavior
There is no runtime state. Build-time state is controlled by kernel configuration symbols.

## Dependencies
The file depends on Kbuild variable conventions and the availability of the referenced source objects in the same directory.

## Risks
If `CONFIG_IXGBEVF_IPSEC` is enabled without required XFRM/crypto dependencies, link or compile errors would surface. Removing an object here can silently drop a feature from the built driver.

## Test signals
Build with `CONFIG_IXGBEVF=y/m`, with and without `CONFIG_IXGBEVF_IPSEC`, and verify resulting module symbols include ethtool and optional IPsec hooks as expected.
