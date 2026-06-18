<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm-iproc.c -->
# sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm-iproc.c

Purpose: Broadcom iProc MDIO mux controller that provides a parent MDIO bus and child mux buses for internal/external selections.

Important APIs/types/functions: `struct iproc_mdiomux_desc` stores mux handle, base, device, mii_bus, and core clock. Core functions are `mdio_mux_iproc_config`, `start_miim_ops`, C22/C45 callbacks, `mdio_mux_iproc_switch_fn`, probe/remove, and PM suspend/resume.

Control flow: probe maps registers, handles legacy unaligned base resources, obtains/enables optional core clock, registers a parent mii_bus with C22/C45 callbacks, initializes child buses via `mdio_mux_init`, then configures scan/clock registers. Switch function encodes desired child as internal/external and bus ID. Transactions reset/clear ctrl, wait stat done state transitions, program param/address/control registers, and return read data or status.

State and persistence: runtime state includes current mux child in mdio-mux core, clock enable, hardware rate/selection registers, and mii_bus objects. PM disables/re-enables clock and reconfigures registers.

Dependencies/integration: depends on `MDIO_BUS_MUX`, OF MDIO, clocks, iopoll, platform MMIO, and phylib. Compatible string is `brcm,mdio-mux-iproc`.

Risks and test signals: risks include resource alignment compatibility, param register bit accumulation, PM restore, clock rate assumptions, and child bus registration failure cleanup. Tests should cover C22/C45 transactions, internal/external child switching, suspend/resume, and malformed child `reg` values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/mdio/mdio-mux-bcm-iproc.c -->
