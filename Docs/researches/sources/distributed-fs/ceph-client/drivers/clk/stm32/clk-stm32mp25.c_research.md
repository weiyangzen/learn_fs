# sources/distributed-fs/ceph-client/drivers/clk/stm32/clk-stm32mp25.c

## Purpose

`clk-stm32mp25.c` is the STM32MP25 RCC driver. It extends the MP21-style shared-core model to the larger MP25 clock tree, including PCIe, Ethernet switch, USB3/PCIe PHY, GPU, DSI/LVDS/video, more serial buses, and additional reset lines.

## Important APIs, Types, And Functions

- Parent-data arrays describe ADC12/ADC3, USB2 PHYs, USB3/PCIe PHY, DSI lane/PHY, LVDS PHY, DTS, and MCO parents using indexed upstream clocks and one internal hardware parent reference.
- `stm32mp25_muxes[]` covers ADC, display PHY, DTS, MCO, USB2, and USB3/PCIe PHY selectors.
- `stm32mp25_gates[]` maps MP25 bus and kernel gates across timers, serial, storage, networking, crypto, media, USB, GPU, PCIe, and display.
- `stm32_rcc_get_access()` is the RCC CID/security access checker shared conceptually with MP21.
- `stm32mp25_check_security()` grants RIFSC clocks through a cached `struct stm32_firewall`; `-ENODEV` from firewall grant is treated as access allowed, but probe itself requires the firewall lookup to succeed.
- `stm32mp25_clock_cfg[]` maps MP25 binding IDs to gate/composite clocks and security IDs.
- `stm32mp25_reset_cfg[]` enumerates explicit reset lines up to `STM32MP25_LAST_RESET`.

## Control Flow

The platform driver binds `st,stm32mp25-rcc` at `core_initcall`. Probe maps RCC MMIO, obtains the firewall handle with `stm32_firewall_get_firewall()`, and invokes `stm32_rcc_init()`. The shared core initializes reset-controller state from the explicit reset table, then registers only clocks whose RIFSC or RCC CID checks allow access.

The clock table exposes bus and kernel gates for expanded MP25 peripherals: PCIe, Ethernet 1/2 and Ethernet switch/ACM, ADC12/ADC3, CCI, OSPIIOM, ADF/MDF, I2C1-8, I3C1-4, SPI1-8, UART/USART/LPUART, timers including TIM20, USB2/USB3/USBT-C, GPU, DSI/LVDS/LTDC, CSI/DCMIPP, VDEC/VENC, crypto, RNG, PKA, SAES, SDMMC, and MCO/DTS composites.

## State And Persistence Behavior

Persistent state resides in RCC registers for gates, muxes, resets, and security/CID/semaphore policy. A file-scope `struct stm32_firewall firewall` stores the discovered firewall provider for security checks. Gate counters live in `stm32mp25_cpt_gate[]`. Registered clock availability reflects access policy at probe time.

## Dependencies And Integration Points

The driver depends on the STM32 firewall bus API, shared STM32 clock/reset helpers, `stm32mp25_rcc.h`, and MP25 clock/reset binding headers. It integrates with CCF and reset-controller consumers for high-speed I/O, display/media, storage, serial, crypto, and networking blocks.

## Risks And Edge Cases

Firewall handling differs subtly from MP21: probe returns an error if `stm32_firewall_get_firewall()` fails, while individual RIFSC grants tolerate `-ENODEV`. The `CK_MCO2` entry uses `MP25_RIF_RCC_MCO1` as its security ID, which looks suspicious because `MP25_RIF_RCC_MCO2` is defined; this deserves hardware or binding review. Dense reset and clock tables are vulnerable to off-by-one binding mistakes. DSI lane parentage references `ck_ker_ltdc.hw`, so registration order and internal parent availability matter. Expanded media/PCIe/USB/GPU clocks increase the blast radius of incorrect gate or security IDs.

## Test Signals

Build with STM32MP25 bindings. Boot an MP25 board and verify RCC probe, firewall access decisions, and clock-summary entries for PCIe, USB2/USB3, Ethernet switch, GPU, DSI/LVDS/LTDC, VDEC/VENC, SDMMC, serial buses, timers, ADC, crypto, and MCO. Exercise reset consumers for PCIe, USB3/PHY, Ethernet switch, GPU, display/media, SDMMC DLLs, watchdog kernel resets, and serial blocks. Specifically test MCO2 access/security behavior.
