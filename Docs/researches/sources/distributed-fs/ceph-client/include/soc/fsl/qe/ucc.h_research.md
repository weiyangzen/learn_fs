# sources/distributed-fs/ceph-client/include/soc/fsl/qe/ucc.h

Purpose: declares common UCC utility APIs for selecting fast/slow mode and configuring QE mux clock/routing features.

Important APIs and types: `UCC_MAX_NUM` defines eight UCCs. `enum ucc_speed_type` maps fast/slow selections to GUEMR RX/TX mode bits. APIs include `ucc_set_type()`, `ucc_set_qe_mux_mii_mng()`, `ucc_set_qe_mux_rxtx()`, `ucc_set_tdm_rxtx_clk()`, `ucc_set_tdm_rxtx_sync()`, and `ucc_mux_set_grant_tsa_bkpt()`. Inline wrappers set grant, TSA, and breakpoint bits through the shared mux helper.

Control flow: protocol drivers configure a UCC as fast or slow, route clocks/sync signals for TX/RX, optionally set MII management routing, and enable grant/TSA/breakpoint mux bits before protocol-specific initialization.

State and persistence: state is QE mux/GUEMR hardware configuration and no persistent software state.

Dependencies and integration points: includes QE memory-map/core headers and uses `enum qe_clock` and `enum comm_dir`. It is shared by UCC fast, slow, Ethernet, serial, and TDM users.

Risks and test signals: risks include invalid UCC numbers, mux conflicts between protocols, wrong direction clock routing, and missing synchronization around shared CMX registers. Test each UCC index, fast/slow transitions, MII management muxing, TDM clock/sync routing, and concurrent configuration paths.
