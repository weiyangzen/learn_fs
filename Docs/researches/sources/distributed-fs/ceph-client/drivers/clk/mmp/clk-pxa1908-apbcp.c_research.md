# sources/distributed-fs/ceph-client/drivers/clk/mmp/clk-pxa1908-apbcp.c

Purpose: platform driver for the PXA1908 APBCP clock block, covering UART2, TWSI2, and AICER/RIPC clocks.

Important APIs/functions: `pxa1908_apbcp_probe` maps the register resource, initializes a 4-clock onecell provider, and calls `pxa1908_apb_p_periph_clk_init`. Static tables define one UART2 mux and three gates.

Control flow: probe registers the UART2 mux first, then all gates, so `uart2_clk` can use `uart2_mux` as parent. The provider serves binding IDs from `dt-bindings/clock/marvell,pxa1908.h`.

State and persistence: device-managed allocation/MMIO; gate and mux state is persistent hardware state.

Dependencies and integration: depends on platform-device matching `marvell,pxa1908-apbcp`, CCF, MMP helper tables, and parent clocks from the MPMU provider.

Risks: small onecell size makes binding ID drift immediately harmful. The RIPC/AICER gate has no parent and custom enable value `0x2`, so consumer assumptions about parent rate may fail.

Test signals: UART2 and TWSI2 DT clock acquisition, APBCP provider registration, and register-level gate toggling checks.
