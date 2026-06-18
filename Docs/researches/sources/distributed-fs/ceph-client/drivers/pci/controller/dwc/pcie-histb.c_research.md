# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-histb.c

Purpose: This is the HiSilicon STB DesignWare PCIe root-complex driver for `hi3798cv200-pcie`. It controls STB system registers, DBI access sideband enable bits, Root Port config operations, link-up/LTSSM detection, clocks, resets, optional regulator, optional PHY, and endpoint reset GPIO.

Important APIs, types, and functions: `struct histb_pcie` stores a pointer to `struct dw_pcie`, four clocks, optional PHY and regulator, three resets, control register base, and reset GPIO. Vendor DBI callbacks are `histb_pcie_read_dbi()` and `histb_pcie_write_dbi()`, using sideband functions `histb_pcie_dbi_r_mode()` and `histb_pcie_dbi_w_mode()`. Host callbacks include `histb_pcie_host_init()`, `histb_pcie_start_link()`, and `histb_pcie_link_up()`. Local Root Port config ops are `histb_pcie_rd_own_conf()` and `histb_pcie_wr_own_conf()`.

Control flow: Probe allocates wrapper and DWC structures, maps `control` and `rc-dbi`, obtains optional `vpcie`, reset GPIO, clocks, resets, and optional PHY, then powers/enables the host. `histb_pcie_host_enable()` enables regulator, releases endpoint reset GPIO, enables bus/sys/pipe/aux clocks, pulses soft/sys/bus resets, and returns. DWC host init calls `histb_pcie_host_init()`, which installs custom bridge ops and sets RC work mode. Link start sets the LTSSM enable bit. Link-up requires XMLH link-up, RDLH link-up, and LTSSM state active.

State and persistence behavior: Runtime state consists of mapped hardware registers, clock/reset/regulator/PHY enablement, and DWC host state. DBI reads/writes temporarily toggle sideband enable bits and do not persist beyond each transaction. Remove disables host resources and exits the PHY. There is no persistent storage.

Dependencies and integration points: Uses DWC host core, PCI bridge ops, Linux clocks, resets, optional regulator, GPIO, PHY, platform resources, and HiSTB system registers. It integrates custom root-bus config access by assigning `pp->bridge->ops`.

Risks: The driver must gate DBI access through separate read/write sideband bits; missing disable could expose unintended register access, while missing enable breaks config cycles. Error handling in probe jumps to PHY exit but does not call `histb_pcie_host_disable()` after a `dw_pcie_host_init()` failure, so changes there need care. `gpiod_set_consumer_name()` is called on an optional descriptor and depends on GPIO helper behavior. Link-up uses three conditions, preventing false positives but making hardware status bit changes visible as enumeration failures.

Test signals: Validate STB probe with and without optional regulator/PHY, clock/reset sequencing, Root Port config slot filtering, DBI sideband read/write, RC mode selection, LTSSM link-up detection, remove cleanup, and failures at each clock/reset/regulator acquisition point.
