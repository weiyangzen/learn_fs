# sources/distributed-fs/ceph-client/drivers/net/ethernet/broadcom/bnge/Makefile

Purpose: Declares how the Broadcom `bng_en` driver is built when `CONFIG_BNGE` is enabled.

Important APIs/types/functions: It produces `bng_en.o` from core, devlink, HWRM, resource-memory, resource, netdev, ethtool, auxiliary RDMA, TX/RX, and link objects: `bnge_core.o`, `bnge_devlink.o`, `bnge_hwrm.o`, `bnge_hwrm_lib.o`, `bnge_rmem.o`, `bnge_resc.o`, `bnge_netdev.o`, `bnge_ethtool.o`, `bnge_auxr.o`, `bnge_txrx.o`, and `bnge_link.o`.

Control flow: Build-time only. It determines which compilation units are linked into the single module/object and therefore which symbols can satisfy cross-file calls used by the researched files.

State/persistence: No runtime state. Build composition persists through Kbuild dependency evaluation.

Dependencies/integration: Depends on Kconfig symbol `CONFIG_BNGE` and the listed sibling source files. The researched files rely on unlisted siblings for HWRM, netdev, resources, TX/RX, and link behavior.

Risks/test signals: Missing an object here would surface as link errors or absent runtime functionality. Test with `CONFIG_BNGE=m` and `=y`, clean incremental builds, and modpost symbol export checks for auxiliary RDMA functions.
