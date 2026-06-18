<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,sparx5.h -->
# sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,sparx5.h

Purpose: Supplies the DT clock IDs for Microchip Sparx5.

Important APIs, types, and functions: Defines `CLK_ID_CORE`, `CLK_ID_DDR`, `CLK_ID_CPU2`, `CLK_ID_ARM2`, `CLK_ID_AUX1` through `CLK_ID_AUX4`, `CLK_ID_SYNCE`, and `N_CLOCKS`. No functions or types are declared.

Control flow: There is no runtime control flow. Sparx5 clock provider code registers clocks corresponding to these IDs for DT consumers.

State and persistence: IDs are persistent ABI. Runtime rate and enable state is owned by the Sparx5 clock controller driver and hardware registers.

Dependencies and integration points: Used by Sparx5 DTS files and by consumers needing core, DDR, CPU/ARM auxiliary, and SyncE clocks.

Risks and test signals: Risks are simple but binding-visible: changing order or count breaks existing DTBs. Test with `dtbs_check`, clock provider probe, `N_CLOCKS` array bounds, and platform checks for networking, CPU auxiliary clocks, DDR clock reporting, and SyncE consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/dt-bindings/clock/microchip,sparx5.h -->
