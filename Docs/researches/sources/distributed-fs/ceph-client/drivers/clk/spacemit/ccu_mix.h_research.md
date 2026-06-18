# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.h Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.h -->
# sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.h

Purpose: defines the descriptor structures, parent helpers, and declaration macros for SpacemiT gate/factor/mux/div composite clocks.

Important APIs and control flow: `struct ccu_gate_config`, `ccu_factor_config`, `ccu_mux_config`, `ccu_div_config`, and `ccu_mix` describe optional sub-blocks around an embedded `ccu_common`. Parent helpers support both local hardware parents (`CCU_PARENT_HW`) and firmware-name parents (`CCU_PARENT_NAME`). Macros such as `CCU_GATE_DEFINE`, `CCU_FACTOR_DEFINE`, `CCU_MUX_DEFINE`, `CCU_DIV_DEFINE`, `CCU_MUX_GATE_DEFINE`, `CCU_MUX_DIV_GATE_DEFINE`, `CCU_MUX_DIV_GATE_FC_DEFINE`, `CCU_MUX_DIV_GATE_SPLIT_FC_DEFINE`, `CCU_MUX_DIV_FC_DEFINE`, and `CCU_MUX_FC_DEFINE` generate static descriptors with the correct operation table and register fields.

State and persistence behavior: macro-generated descriptors are static in SoC files. The header stores only configuration metadata; runtime state remains in hardware registers. FC-enabled macros record either a shared control/FC register or split control and FC registers, plus a bit mask to poll.

Dependencies and integration points: depends on CCF parent-data initializers and the exported operation tables from `ccu_mix.c`. It is the main declarative interface used by K1/K3 SoC tables and must match the `ccu_common` embedding expected by the common probe.

Risks and test signals: risks include copy/paste argument-order mistakes in large SoC tables, register-field overlap when multiple clocks share a register, no compile-time validation of mux/div widths, parent-data arrays needing stable storage duration, and split-FC macros being easy to misconfigure. Test signals include CCF registration of every generated clock, parent lists matching DT bindings and hardware docs, correct FC register use for display/CPU/high-speed clocks, and static analysis or boot logs catching invalid masks or parent counts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/clk/spacemit/ccu_mix.h -->
