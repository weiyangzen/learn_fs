# sources/distributed-fs/ceph-client/drivers/media/platform/samsung/exynos-gsc/gsc-regs.c

## Purpose
`gsc-regs.c` is the low-level G-Scaler register programming layer. It converts the active `struct gsc_ctx` source/destination frames, controls, scaler ratios, paths, and DMA addresses into MMIO writes defined by `gsc-regs.h`.

## Important APIs, Types, and Functions
Reset and interrupt helpers include `gsc_hw_set_sw_reset()`, `gsc_wait_reset()`, `gsc_hw_set_frm_done_irq_mask()`, and `gsc_hw_set_gsc_irq_enable()`. Buffer helpers program masks and addresses with `gsc_hw_set_input_buf_masking()`, `gsc_hw_set_output_buf_masking()`, `gsc_hw_set_input_addr()`, and `gsc_hw_set_output_addr()`. Pipeline setup is handled by `gsc_hw_set_input_path()`, `gsc_hw_set_in_size()`, `gsc_hw_set_in_image_format()`, `gsc_hw_set_output_path()`, `gsc_hw_set_out_size()`, `gsc_hw_set_out_image_format()`, `gsc_hw_set_prescaler()`, `gsc_hw_set_mainscaler()`, `gsc_hw_set_rotation()`, `gsc_hw_set_global_alpha()`, and `gsc_hw_set_sfr_update()`.

## Control Flow
The m2m run path writes DMA addresses for the selected buffer slot and, when parameters are dirty, enables buffer slots and interrupts, computes scaler data in the core layer, then calls these helpers in input, output, scaler, rotation, and alpha order. Each helper reads the relevant control register, clears only the fields it owns, sets format/path/rotation bits from `ctx`, and writes the result back. `gsc_hw_set_sfr_update()` is the final handoff that tells hardware to latch shadow registers.

## State and Persistence
State is entirely MMIO-backed and volatile. The helper functions do not keep a software shadow, so correctness depends on clearing masks before setting new fields and on the caller serializing access with the device spinlock. Reset polling waits up to 50 ms for `GSC_SW_RESET` to clear.

## Dependencies and Integration Points
The file depends on Linux `readl()`/`writel()`, delay helpers, `gsc-core.h` frame/control structures, and the register field macros in `gsc-regs.h`. It is consumed by the GSC mem2mem and core interrupt/control paths.

## Risks and Edge Cases
Format decisions are tightly coupled to `gsc_fmt` fields such as `num_comp`, `num_planes`, `depth`, chroma order, and tiled state; inconsistent format descriptors will program invalid hardware combinations. Rotation swaps output scaled dimensions for 90/270 degrees. RGB color range selection depends on V4L2 colorspace. Output local path forces YUV444 rather than DMA layout. Address writes cast DMA addresses to register-width values and assume the hardware-visible address fits the register layout.

## Test Signals
Tests should observe reset completion, IRQ mask/enable toggles, correct MMIO fields for single-, two-, and three-plane formats, tiled NV12 handling, chroma order variants, RGB565/RGB32 range and alpha fields, 0/90/180/270 rotations plus flips, scaler ratio register values, and shadow register update before hardware enable.
