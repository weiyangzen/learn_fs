# sources/distributed-fs/ceph-client/drivers/net/ethernet/ti/Makefile

## Purpose
This Makefile maps TI ethernet Kconfig symbols to objects and composite modules. It defines shared CPSW components, K3 AM65 CPSW module composition, Keystone NETCP modules, ICSSG/ICSSM components, and standalone legacy drivers.

## Important APIs, Types, and Functions
Important build variables include `ti-cpsw-common-y`, `ti-cpsw-priv-y`, `ti-cpsw-ale-y`, `ti-cpsw-sl-y`, `ti_cpsw-y`, `ti_cpsw_new-y`, `keystone_netcp-y`, `keystone_netcp_ethss-y`, `ti-am65-cpsw-nuss-y`, `icssg-prueth-y`, `icssg-prueth-sr1-y`, and `icssg-y`. The researched `am65-cpsw-ethtool.c` is linked through `ti-am65-cpsw-nuss-y := am65-cpsw-nuss.o am65-cpsw-ethtool.o`.

## Control Flow and State
There is no runtime state. Build composition determines which translation units share module scope. `ti-am65-cpsw-nuss-$(CONFIG_TI_AM65_CPSW_QOS)` conditionally includes `am65-cpsw-qos.o`, and `ti-am65-cpsw-nuss-$(CONFIG_TI_K3_AM65_CPSW_SWITCHDEV)` conditionally includes switchdev support. The base AM65 module always includes the ethtool implementation.

## Dependencies and Integration Points
The Makefile integrates Kconfig selections with shared support code such as ALE, CPDMA, CPTS, CPTS for AM65, K3 CPPI descriptor pools, ICSSG classifiers/stats/config, and switchdev objects. It is the linkage point ensuring ethtool ops can reference AM65 NUSS headers and optional QoS symbols guarded by Kconfig checks.

## Risks and Test Signals
Object-list drift can produce unresolved references or missing feature registration. Conditional AM65 QoS/switchdev object inclusion should match Kconfig feature guards in code. Test signals include `CONFIG_TI_K3_AM65_CPSW_NUSS=m/y` builds with `CONFIG_TI_AM65_CPSW_QOS` on/off, switchdev on/off, and build checks for shared objects not being duplicated across incompatible modules.
