# sources/distributed-fs/ceph-client/drivers/gpu/drm/amd/display/dc/dce/dce_clock_source.h

Purpose: declares the DCE/DCN clock-source wrapper, register/mask/shift lists for PLL resync and DP DTO programming, constructors for several hardware generations, and the video-optimized pixel-rate table interface.

Important APIs and types: `TO_DCE110_CLK_SRC()` downcasts `struct clock_source`. Register-list macros cover DCE PLL/resync registers and DCN1/DCN2/DCN3/DCN401 DTO phase/modulo/pixel-rate-control layouts. `struct dce110_clk_src_regs`, `struct dce110_clk_src_shift`, and `struct dce110_clk_src_mask` describe register metadata. `struct dce110_clk_src` embeds `struct clock_source`, BIOS pointer, spread-spectrum arrays for DP/HDMI/DVI/LVDS, external/reference clocks, and two PLL calculator objects. Constructors select function tables by generation. `struct pixel_rate_range_table_entry` and `look_up_in_video_optimized_rate_tlb()` expose 1000/1001 rate mapping.

Control flow and integration: resource builders include this header to construct clock sources with ASIC-specific register tables. The generic clock-source API then calls the function table set by the constructor. The header is the generation-compatibility surface between DC resource construction, BIOS programming, and `dce_clock_source.c`.

State and persistence: describes in-memory state only; hardware state is programmed by the C file through supplied register addresses. Spread-spectrum pointers and counts persist for the lifetime of the clock-source object.

Dependencies and risks: depends on `../inc/clock_source.h`, `MAX_PIPES`, BIOS/clock-source types, and generated register macros. Risks center on maintaining many generation-specific register list macros; a wrong `pllid`/pipe index mapping can route DTO programming to the wrong pipe. Compile-time coverage across ASIC families and runtime register tracing for each constructor are key test signals.
