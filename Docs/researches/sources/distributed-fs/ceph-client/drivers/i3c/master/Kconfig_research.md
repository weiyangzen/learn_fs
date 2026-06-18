# sources/distributed-fs/ceph-client/drivers/i3c/master/Kconfig

Purpose: Kconfig options for I3C master controller drivers.

Important APIs/types/functions: Defines `ADI_I3C_MASTER`, `CDNS_I3C_MASTER`, `DW_I3C_MASTER`, `AST2600_I3C_MASTER`, `SVC_I3C_MASTER`, `MIPI_I3C_HCI`, `MIPI_I3C_HCI_PCI`, and `RENESAS_I3C`.

Control flow: Options are visible under top-level I3C and gate compilation of controller drivers. Some options select helper subsystems, such as `MFD_SYSCON` for AST2600 and `MFD_CORE` for HCI PCI.

State and persistence: Chosen tristate values decide built-in or module output for each controller.

Dependencies/integration: HAS_IOMEM, architecture exclusions, ASPEED/COMPILE_TEST, PCI, MFD, and the master-driver Makefile. AST2600 depends on DesignWare because it wraps the DW common driver.

Risks: ALPHA/PARISC exclusions are tied to `{read,write}sl()` availability. Incorrect dependencies can expose drivers that cannot link or run. AST2600 must track DW common symbol availability.

Test signals: Kconfig visibility and build matrix across native and `COMPILE_TEST` configs; verify module names and dependency closure.
