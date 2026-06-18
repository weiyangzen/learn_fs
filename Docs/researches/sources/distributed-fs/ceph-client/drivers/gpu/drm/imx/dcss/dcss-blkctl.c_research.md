<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-blkctl.c -->
## sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-blkctl.c

Purpose: Implements DCSS block-control setup for clock/reset release and output clock-source selection.

Important APIs/types/functions: Exports `dcss_blkctl_init()` and `dcss_blkctl_cfg()`. Defines `struct dcss_blkctl`.

Control flow: Init allocates state, maps the block-control register space, stores it on `dcss->blkctl`, and calls config. Config selects HDMI or MIPI clocking based on `dcss->hdmi_output`, then sets reset bits for bus/APB/pixel/RTR clocks.

State and persistence behavior: Stores `dcss` pointer and mapped base. Register state is re-applied on device runtime/system resume through `dcss_blkctl_cfg()`.

Dependencies: DCSS low-level MMIO helpers from `dcss-dev.h`, device-managed allocation/ioremap, and OF-derived output type.

Integration points: Called during `dcss_submodules_init()` and on every DCSS resume before context-loader resume.

Risks: Output selection uses a boolean derived from the remote bridge compatible. Wrong detection can select the wrong pixel clock path. Reset bits must match SoC integration.

Test signals: Probe with HDMI and MIPI/DSI remote nodes, resume reconfiguration, and successful display output after reset release.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/gpu/drm/imx/dcss/dcss-blkctl.c -->
