# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3528.c

Purpose: RK3528 reset-controller LUT. It describes reset ID to CRU SOFTRST register/bit mappings for core, bus, VPU, PCIe, GPU, encoder/decoder, VO, HDMI, USB, DDR, and peripheral domains.

Important APIs/types/functions: `RK3528_CRU_RESET_OFFSET()` creates high-word reset bit indexes, `rk3528_register_offset[]` is the sparse binding-ID lookup table, and `rk3528_rst_init()` registers the table.

Control flow: SoC clock init invokes `rk3528_rst_init()`, which calls `rockchip_register_softrst_lut(np, rk3528_register_offset, ARRAY_SIZE(...), reg_base + RK3528_SOFTRST_CON(0), ROCKCHIP_SOFTRST_HIWORD_MASK)`. Common reset ops later translate reset IDs through the LUT before writing the soft-reset bank.

State and persistence: local state is immutable after registration. Asserted reset bits persist in CRU hardware until deasserted by reset consumers or firmware.

Dependencies and integration: RK3528 reset dt-binding IDs, `clk.h` RK3528 CRU macros, and `softrst.c`. It is consumed by device-tree reset phandles on RK3528 platforms.

Risks: table correctness is hardware critical; bad entries can reset unrelated blocks. The broad range through SOFTRST_CON46 increases risk of binding-table drift. PCIe, HDMI, USB PHY, DDR PHY, and media resets often have ordering requirements outside this file, so consumers must sequence clocks/resets/power domains correctly.

Test signals: compare against vendor TRM/register dumps, boot with all reset consumers enabled, exercise PCIe/USB/display/video/storage reset cycles, and verify no kernel warnings from missing reset IDs.
