# sources/distributed-fs/ceph-client/net/l3mdev/Kconfig

## Purpose
This Kconfig entry exposes `NET_L3_MASTER_DEV`, the core networking glue needed by L3 master devices such as VRF. It controls whether the l3mdev API is available to route lookup code and device drivers.

## Important APIs, Types, and Functions
The file defines one bool symbol, `NET_L3_MASTER_DEV`, with prompt `L3 Master device support`. It depends on `INET || IPV6`, so it is only meaningful when IPv4 or IPv6 networking is present.

## Control Flow
Kconfig selection is compile-time only. If enabled, the l3mdev object is built by the directory Makefile and the exported l3mdev helpers become available to other networking code.

## State and Persistence
No runtime state is stored here. The selected value persists only through kernel configuration and determines compilation of the related object.

## Dependencies and Integration Points
The dependency on `INET || IPV6` aligns l3mdev support with IP routing consumers. VRF and similar drivers rely on the symbol to access L3 master lookup, FIB table, and flow update helpers.

## Risks and Edge Cases
If code assumes l3mdev helpers exist without the symbol dependency, build failures or missing route isolation support can result. The help text is intentionally broad and does not select a concrete VRF driver.

## Test Signals
Build matrix coverage should include IPv4-only, IPv6-only, dual-stack, and neither-stack configurations to confirm the symbol appears and l3mdev users compile as expected.
