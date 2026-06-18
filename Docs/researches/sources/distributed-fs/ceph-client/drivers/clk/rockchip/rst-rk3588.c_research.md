# sources/distributed-fs/ceph-client/drivers/clk/rockchip/rst-rk3588.c

Purpose: RK3588 reset-controller LUT. It maps reset IDs to main CRU, PHPTOPCRU, PMU1CRU, and SECURECRU soft-reset bits for one of the largest Rockchip clock/reset domains.

Important APIs/types/functions: `RK3588_CRU_RESET_OFFSET()`, `RK3588_PHPTOPCRU_RESET_OFFSET()`, `RK3588_SECURECRU_RESET_OFFSET()`, `RK3588_PMU1CRU_RESET_OFFSET()`, `rk3588_register_offset[]`, and `rk3588_rst_init()`. The table includes comments for several resets missing in the TRM but still exposed.

Control flow: SoC clock setup calls `rk3588_rst_init()`, registering the LUT with `rockchip_register_softrst_lut()` at `RK3588_SOFTRST_CON(0)` and high-word mask mode. Reset consumers later assert/deassert through common reset ops.

State and persistence: immutable mapping table plus hardware CRU reset bits. No local dynamic state.

Dependencies and integration: RK3588 reset dt-bindings, `clk.h` RK3588 offsets, common Rockchip reset controller, and DT consumers for USB/USBDP, DCPHY, audio, bus, UART/I2C/SPI/CAN, DDR, NPU, storage, PCIe/SATA, RKVDEC/RKVENC, VI/CSI, VOP/HDMI/DP, GPU, AV1, secure crypto, PMU, and TRNG blocks.

Risks: multi-island offsets and large sparse table are error-prone. Entries noted as missing from TRM require silicon/vendor validation. DDR and display/PHY reset sequencing is high impact. Wrong secure reset entries can affect boot/security services.

Test signals: comprehensive boot on RK3588 boards, reset API smoke tests for all active DT consumers, PCIe/USB/display/media/GPU/NPU exercise, suspend/resume, register tracing for missing-TRM entries, and binding coverage checks.
