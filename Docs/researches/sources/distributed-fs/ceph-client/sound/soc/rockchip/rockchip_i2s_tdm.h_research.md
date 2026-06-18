# sources/distributed-fs/ceph-client/sound/soc/rockchip/rockchip_i2s_tdm.h

Purpose: Register and GRF macro header for the Rockchip I2S/TDM controller driver.

Important APIs, types, and functions: Defines TXCR/RXCR fields including per-path lane routing, CKR, FIFO, DMA, interrupt, XFER/CLR, TDM frame controls, CLKDIV, register offsets, HIWORD update helper, and SoC-specific GRF clock-routing constants for PX30, RK1808, RK3308, RK3568, and RV1126.

Control flow: No executable code. `rockchip_i2s_tdm.c` uses these macros for regmap updates, route validation, TDM slot programming, and SoC init writes.

State and persistence: No runtime state. Constants encode hardware ABI for multiple SoC families.

Dependencies and integration: Includes `linux/hw_bitfield.h` for `FIELD_PREP_WM16_CONST` and uses Linux bit macros. Integrates with device-tree match data in the TDM driver.

Risks and edge cases: Base I2S and TDM headers use similar names with different IO direction encodings, so accidental inclusion misuse can misroute pins. HIWORD update constants must match GRF write-mask conventions. TDM frame macros subtract one from widths, so callers must validate nonzero slot/frame widths.

Test signals: Compile coverage across all supported SoCs plus register dump validation for TRCM TX-only/RX-only, IO multiplex, TDM slot width, and lane routing.
