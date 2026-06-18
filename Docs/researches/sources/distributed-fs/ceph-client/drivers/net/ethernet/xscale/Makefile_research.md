<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Makefile -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Makefile

Purpose: Defines build order for the Intel XScale IXP Ethernet driver objects.

Important APIs/types/functions: If `CONFIG_PTP_1588_CLOCK_IXP46X` is set, `ptp_ixp46x.o` is added before `ixp4xx_eth.o`; `ixp4xx_eth.o` is built according to `CONFIG_IXP4XX_ETH`.

Control flow: Kbuild conditionally links the PTP clock object first to avoid deferred probing, then links the Ethernet driver. When `IXP4XX_ETH=m`, these objects participate in module build according to Kconfig linkage.

State and persistence behavior: No runtime state. The main persistence is build ordering, which affects whether the Ethernet probe can find the PTP clock provider without deferral.

Dependencies and integration points: Consumes symbols from the sibling Kconfig and coordinates the exported `ixp46x_ptp_find()` provider with the Ethernet consumer in `ixp4xx_eth.c`.

Risks and test signals: Build and boot tests should verify the stated link order prevents avoidable probe deferral when PTP is enabled. Also verify PTP-disabled builds compile `ixp4xx_eth.c` against the inline `ixp46x_ptp_find()` stub in `ixp46x_ts.h`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/xscale/Makefile -->
