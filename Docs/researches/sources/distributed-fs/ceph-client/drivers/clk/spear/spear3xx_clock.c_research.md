# sources/distributed-fs/ceph-client/drivers/clk/spear/spear3xx_clock.c

## Purpose
Initializes the common clock tree for ST SPEAr300/310/320 family machines. It registers oscillator roots, PLL/VCO clocks, synthesizers, muxes, dividers, gates, RAS clocks, and machine-specific fixed-factor or muxed peripheral clocks.

## Important APIs, Types, And Functions
The main entry point is `spear3xx_clk_init(void __iomem *misc_base, void __iomem *soc_config_base)`. It uses common clock framework helpers plus SPEAr-specific helpers from `clk.h`: `clk_register_vco_pll`, `clk_register_aux`, and `clk_register_gpt`. Local rate tables `pll_rtbl`, `aux_rtbl`, and `gpt_rtbl` encode supported PLL, auxiliary synth, and GPT synth settings. Conditional helpers `spear300_clk_init`, `spear310_clk_init`, and `spear320_clk_init` add per-machine device clock aliases.

## Control Flow
Initialization registers 32 kHz and 24 MHz oscillators, creates the fixed 48 MHz `pll3_clk`, configures PLL1/PLL2 from MISC registers, derives CPU/AHB/APB/DDR clocks, then walks through UART, FIRDA, GPT, generic synth, USB, AHB, APB, and RAS gate registration. The final `of_machine_is_compatible` branch selects SPEAr300, SPEAr310, or SPEAr320 additions; SPEAr320 also programs mux parents for I2S, SDHCI, SMII, and UARTx clocks and forces UART1/UART2 to `ras_apb_clk`.

## State And Persistence
State is persisted in the hardware clock-control registers under `misc_base` and, for SPEAr320, `soc_config_base`. The driver also installs global clkdev lookup entries. A single static spinlock serializes register updates among the registered clock operations.

## Dependencies And Integration Points
Depends on the Linux common clock framework, clkdev lookup, device tree machine compatibles, and SPEAr helper clock implementations in the sibling `clk-*` files. Integration is by string aliases such as `d0000000.serial`, `fc980000.gpio`, `70000000.sdhci`, and RAS clock names consumed by platform devices.

## Risks And Edge Cases
The code assumes valid MMIO bases and does little error checking after clock registration, so a failed registration can leave later aliases pointing at error clocks. Register bit definitions and parent arrays must match silicon; wrong mux masks can select reserved parents. SPEAr320 has special enforced UART parents that can surprise rate changes. Conditional machine blocks mean build configuration affects available aliases.

## Test Signals
Useful signals are boot-time clock registration without warnings, `/sys/kernel/debug/clk/clk_summary` parent/rate sanity, successful probe of UART/I2C/GPIO/USB/storage devices on each SPEAr3xx variant, and exercising rate changes on UART/FIRDA/GPT/generic synth clocks.
