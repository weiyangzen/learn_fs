# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/mmhubbub/dcn32/dcn32_mmhubbub.c

Purpose: implements DCN3.2 MMHUBBUB/MCIF writeback behavior, reusing DCN2.0 helpers where compatible and adding memory warmup support.

Important APIs/functions: `dcn32_mmhubbub_construct` installs `dcn32_mmhubbub_funcs`. Private helpers `mmhubbub32_warmup_mcif`, `mmhubbub32_config_mcif_buf`, and `mmhubbub32_config_mcif_arb` override warmup, buffer, and arbitration behavior.

Control flow: warmup shifts base address/region/increment by 5 bits, enables warmup with software interrupt, waits for completion, acknowledges, then disables warmup. Buffer setup writes four luma/chroma address pairs and sizes/pitch but omits some DCN20 offset/warmup-pitch programming. Arbitration writes time-per-pixel, urgent watermarks through `MCIF_WB_WATERMARK`, p-state watermarks through `MCIF_WB_NB_PSTATE_LATENCY_WATERMARK`, max scaled time, slice size, and larger DCN32 arbitration units.

State/persistence: uses `struct dcn30_mmhubbub` base object with DCN32 register maps. Hardware state persists in MCIF and MMHUBBUB warmup registers.

Dependencies/integration: reuses `mmhubbub2_enable_mcif`, `disable`, `config_irq`, and `dump_frame`; depends on `dcn32_mmhubbub.h`, `dcn30_mmhubbub`, `reg_helper`, `resource`, and `mcif_wb`.

Risks: warmup waits can time out; address/increment units must match hardware. Changed watermark mask registers from DCN20 make copy/paste regressions likely. Reused DCN20 dump/IRQ helpers must remain field-compatible.

Test signals: memory warmup completion/timeout, writeback capture on DCN3.2, watermark programming, arbitration slice values, and function-table compatibility with generic `mcif_wb` users.
