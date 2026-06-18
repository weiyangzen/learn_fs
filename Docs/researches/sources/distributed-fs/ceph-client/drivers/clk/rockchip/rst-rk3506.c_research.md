# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3506.c

Purpose: reset-controller lookup table for RK3506. It maps public `dt-bindings/reset/rockchip,rk3506-cru.h` reset IDs to CRU soft-reset register/bit positions.

Important APIs/types/functions: `RK3506_CRU_RESET_OFFSET(id, reg, bit)` computes LUT entries as `reg * 16 + bit`; `rk3506_register_offset[]` holds sparse indexed reset mappings; `rk3506_rst_init()` registers the LUT with `rockchip_register_softrst_lut()`.

Control flow: the clock driver calls `rk3506_rst_init(np, reg_base)`. That registers a reset controller at `reg_base + RK3506_SOFTRST_CON(0)` using `ROCKCHIP_SOFTRST_HIWORD_MASK`, so reset assert/deassert writes use Rockchip high-word mask semantics.

State and persistence: no mutable local state after init. Reset state is in hardware soft-reset registers. The common reset controller stores the LUT pointer and maps consumer reset IDs through it.

Dependencies and integration: Linux reset-controller framework through `softrst.c`, RK3506 reset dt-bindings, and RK3506 CRU offset macros from `clk.h`.

Risks: the table skips unused registers and IDs; an unlisted binding ID has a zero default if still within array bounds, which can accidentally target SOFTRST_CON00 bit 0 if bindings and table diverge. Wrong register/bit values can hold CPU, bus, DDR, USB, audio, GPIO, storage, or video blocks in reset.

Test signals: reset phandle users for UART/I2C/SPI/GPIO/audio/storage/USB/video probe successfully, targeted reset pulses affect only intended blocks, and dt-binding max ID coverage matches `ARRAY_SIZE(rk3506_register_offset)`.
