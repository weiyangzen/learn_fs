# sources/distributed-fs/ceph-client/drivers/bcma/driver_gmac_cmn.c

Purpose: this small file initializes the BCMA GBIT MAC COMMON core state.

Important APIs, types, and functions: it defines `bcma_core_gmac_cmn_init`, which initializes `gc->phy_mutex` in `struct bcma_drv_gmac_cmn`.

Control flow: the function is a straight-line initializer with no guards, allocations, or return value.

State and persistence: persistent state is the initialized mutex embedded in the GMAC common driver struct. No hardware registers are touched here.

Dependencies and integration points: it depends on `bcma_private.h`, public BCMA structures, and Linux mutex initialization. Ethernet/PHY code using the GMAC common core expects this mutex before serializing PHY access.

Risks: calling this repeatedly on an active mutex would be unsafe if users hold or wait on it. The simplicity means most correctness depends on callers invoking it before any PHY operations.

Test signals: network bring-up paths using the GMAC common core should not warn about uninitialized locking and should serialize PHY operations correctly.
