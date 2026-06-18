# sources/distributed-fs/ceph-client/drivers/clk/sunxi-ng/ccu-sun50i-h616.c

Purpose: main CCU driver for Allwinner H616-family SoCs. It is derived from H6 but adapts PLL layout, audio PLL modeling, GPU clock handling, module gates, and reset coverage for H616.

Important APIs, types, and functions: defines CPUX, DDR0/DDR1, peripheral, GPU, video0/1/2, VE, DE, and audio PLLs; fixed-factor audio and video outputs; CPU/AXI/PSI/AHB/APB/MBUS roots; module clocks and gates; `sun50i_h616_ccu_clks`, `sun50i_h616_hw_clks`, `sun50i_h616_ccu_resets`, `sun50i_h616_ccu_desc`, PLL/mux notifiers for CPU and GPU, and `sun50i_h616_ccu_probe()`.

Control flow: probe maps registers, enables lock and output-enable bits on all PLLs, clears video PLL test dividers, normalizes OHCI 12 MHz muxes, configures audio PLL M0/M1 for SDM use, programs GPU1 input divider for a safe 400 MHz default, selects HDMI CEC’s usable parent, registers the CCU descriptor, then installs CPU and GPU mux/PLL notifiers for safe rate changes and relocking.

State and persistence: state is MMIO register bits for PLL factors, gates, muxes, resets, and lock enables. Software state is static tables plus devm-managed framework registrations.

Dependencies and integration points: binds `allwinner,sun50i-h616-ccu`, uses Sunxi CCU primitives and DT binding IDs, and feeds CPUfreq, GPU, DRAM/MBUS, MMC, USB, display/TCON, HDMI/CEC, CSI, VE, audio, bus gates, and reset consumers.

Risks and test signals: risks cluster around variant differences from H6: extra DDR/video PLLs, PLL output-enable bit handling, GPU notifier correctness, audio SDM dividers, and reset ID alignment. Test with clk summary, cpufreq and GPU DVFS/rate changes, HDMI CEC, USB OHCI/EHCI, MMC, display/audio bring-up, reset-controller consumers, and boot logs for PLL lock failures.
