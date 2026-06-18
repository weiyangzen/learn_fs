# sources/distributed-fs/ceph-client/drivers/pci/controller/dwc/pcie-nxp-s32g.c

Purpose: This is the NXP S32G DesignWare PCIe root-complex driver. It configures S32G controller registers, per-port SerDes PHYs, root-port mode, LTSSM, Gen3/SRIS-related DWC settings, ACE coherency boundaries, runtime PM, and DWC host integration.

Important APIs, types, and functions: `struct s32g_pcie` embeds `struct dw_pcie`, controller register base, and parsed port list. `struct s32g_pcie_port` stores a SerDes PHY. DWC link ops are `s32g_pcie_start_link()` and `s32g_pcie_stop_link()`. Host initialization is `s32g_init_pcie_controller()`. PHY lifecycle is handled by `s32g_init_pcie_phy()` and `s32g_deinit_pcie_phy()`. Port parsing is `s32g_pcie_parse_ports()` and `s32g_pcie_parse_port()`.

Control flow: Probe allocates state, maps `ctrl`, parses child `pci` nodes for PHYs and optional `num-lanes`, enables runtime PM, disables LTSSM, initializes each SerDes PHY in PCIe mode and powers it on, sets host ops and `pp->use_atu_msg`, then calls `dw_pcie_host_init()`. Host init sets Root Port device type, clears SRIS mode to use default CRNS, resets DWC ACE coherency registers so peripheral space below 0x80000000 is non-coherent and DDR above it is memory, enables SRIS deskew and Gen3 phase 2/3 equalization, and returns. DWC start/stop toggles the LTSSM bit.

State and persistence behavior: State is volatile. Hardware registers keep LTSSM, device type, SRIS, coherency, and DWC Gen3 setup while powered. The ports list owns PHY lifecycle until deinit. Runtime PM is active after successful probe. Suspend/resume delegates to DWC noirq helpers.

Dependencies and integration points: Uses DWC host core, Linux PHY framework with `phy_set_mode_ext(PHY_MODE_PCIE, 0)`, runtime PM, OF child parsing, and S32G control registers. DWC coherency registers from `pcie-designware.h` are programmed directly.

Risks: ACE coherency setup is required for MSI/peripheral traffic because Ncore can drop coherent transactions to peripheral space. Hard-coded DDR boundary at 0x80000000 must match platform memory layout. PHY error unwinding deletes the ports list, so later cleanup must avoid double-use. The driver assumes one Root Port for `num-lanes` propagation. `pp->use_atu_msg` affects PME/message ATU behavior and should not be removed casually.

Test signals: Test S32G2 probe with valid `pci` child nodes, SerDes PHY init/mode/power sequencing, no-child error path, `num-lanes` propagation, coherency register programming, MSI delivery, LTSSM start/stop, Gen3 link training, runtime PM suspend/resume, and PHY failure unwinds across multiple ports.
