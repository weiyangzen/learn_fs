# sources/distributed-fs/ceph-client/drivers/clk/socfpga/clk-periph-a10.c

Purpose: Arria10 peripheral/free clock helper.

Important APIs/types/functions: `clk_periclk_recalc_rate()`, `clk_periclk_get_parent()`, `__socfpga_periph_init()`, and `socfpga_a10_periph_init()`.

Control flow: parses node register, optional divider register, fixed divider, output name, and parents; registers a peripheral clock with recalc/get-parent ops and publishes a simple provider.

State and persistence behavior: per-clock register/divider metadata; hardware holds parent and divider state.

Dependencies/integration points: global Arria10 clock-manager base, shared `clk.h`, CCF, OF properties, and special parent decoding for MPU/NOC/SDMMC free clocks.

Risks: name-based parent logic returns zero for unexpected names; base mapping must precede this init; parent count is limited.

Test signals: Arria10 boot, free-clock parent decoding, fixed/register divider rates, and provider registration.
