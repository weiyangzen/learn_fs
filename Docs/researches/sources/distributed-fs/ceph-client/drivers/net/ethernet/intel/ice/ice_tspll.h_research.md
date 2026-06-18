# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/ice/ice_tspll.h

Purpose: declares TSPLL parameter structures, E825-C CGU constants, and exported TSPLL/SyncE helper prototypes used by the ice PTP and DPLL integration code.

Important APIs and types: `struct ice_tspll_params_e82x` stores the E82x table-driven reference pre-divider, post-PLL divider, feedback divider, and fractional divider. Constants name CGU recovered-clock mux selections (`ICE_CGU_NET_REF_CLK0`, `ICE_CGU_REF_CLK_BYP0`, `ICE_CGU_REF_CLK_BYP1`) and fixed E825 TSPLL programming values. Exported functions initialize TSPLL, configure E825-C 1PPS output, query/configure bypass mux activity, and set SyncE ETH divider values.

Control flow role: the header is consumed by `ice_tspll.c` and callers that need TSPLL initialization or SyncE output programming. It does not enforce locking itself, but the implementation documents bypass mux and divider configuration as protected by the PF DPLL lock.

State and persistence: no direct state is stored here. The constants and struct shape define how `ice_tspll.c` writes hardware CGU registers and how selected frequencies map to register fields.

Dependencies and integration: depends on `struct ice_hw`, `enum ice_synce_clk`, and TSPLL frequency/source definitions from `ice_type.h` and related PTP headers included by C files. It is part of the PTP/SyncE hardware support boundary rather than the network datapath.

Risks: constants are hardware contract values; changing them breaks register programming. The E82x parameter struct must stay synchronized with the frequency table and CGU field widths. Callers must pass valid output enums and hold required locks for DPLL-related paths.

Test signals: compile coverage for all users, TSPLL init on supported and unsupported MAC types, DPLL/SyncE tests for both outputs, and hardware validation that generated 1PPS/recovered-clock outputs match selected link speed and source.
