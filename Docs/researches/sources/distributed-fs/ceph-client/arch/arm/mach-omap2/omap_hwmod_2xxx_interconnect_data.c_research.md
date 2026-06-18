# sources/distributed-fs/ceph-client/arch/arm/mach-omap2/omap_hwmod_2xxx_interconnect_data.c

Purpose: Defines common OMAP2xxx OCP interconnect links shared by OMAP2420 and OMAP2430. These `struct omap_hwmod_ocp_if` records express which bus master can access which slave module, which interface clock gates that path, which initiators use the path, and selected legacy firewall metadata.

Important descriptors: core bus links include L3 main to L4 CORE, MPU to L3 main, DSS to L3, and L4 CORE to L4 WKUP. Peripheral links cover L4 CORE to UART1-3, McSPI1-2, timers3-12, DSS core/dispc/rfbi/venc, RNG, SHAM, and AES. Several display links include OMAP2 L3/L4 firewall region or permission data; VENC also uses `OCPIF_SWSUP_IDLE`. Most peripheral paths list both `OCP_USER_MPU` and `OCP_USER_SDMA`, while the MPU to L3 link is MPU-only.

Control flow: no code executes in this file. OMAP2420 and OMAP2430 init arrays include these link objects and pass them to `omap_hwmod_register_links()`. The hwmod core uses each link to register master/slave hwmods, append the link to the slave's `slave_ports`, count slave ports, find the MPU runtime port, initialize interface clocks, and add/remove sleep dependencies while enabling or idling modules.

State and persistence: the descriptors are static and become runtime list nodes after registration. The `_int_flags` field is set by `_register_link()` to prevent duplicate registration if a common link appears in multiple init arrays. Interface clock names persist into `clk_get()` lookups and can affect whether accesses are possible during setup and runtime PM.

Dependencies and integration: depends on common OMAP2 L3/L4 hwmod objects, common OMAP2 IP block objects, and firewall constants from `l3_2xxx.h` and `l4_2xxx.h`. It is an integration bridge between common module descriptors and chip-specific OMAP2420/2430 arrays.

Risks: incorrect `user` bits can remove sleep dependencies and allow smart-idle while an initiator is active. Incorrect interface clock names will cause `_init_interface_clks()` warnings and may prevent register access. Duplicate link reuse relies on `_OCPIF_INT_FLAGS_REGISTERED`; if the same static object is shared across incompatible boot paths, previous registration state matters. Legacy firewall metadata is descriptive here and easy to confuse with `omap_hwmod_ocp_if.flags` because both mention firewall concepts.

Test signals: OMAP2420/2430 boot should register these common links without duplicate or invalid-link warnings, resolve interface clocks for UART/McSPI/timer/DSS/crypto modules, and expose MPU runtime ports for all accessible slaves. Runtime tests should cover SDMA and MPU users for timers, UARTs, display, and crypto, plus display idle behavior on the VENC link with software-supervised interface idle.
