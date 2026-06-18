# sources/distributed-fs/ceph-client/drivers/clk/qcom/gcc-apq8084.c

## Purpose

`gcc-apq8084.c` is the global clock controller driver for Qualcomm APQ8084, matched by `qcom,gcc-apq8084`. It publishes APQ8084 GCC clocks, resets, and GDSC power domains for platform peripherals including BLSP QUP/UART, BAM DMA, crypto engines, PCIe, SATA, SDCC, TSIF, UFS, USB HS/HSIC/USB3, PDM, PRNG, NoC, and MMSS GPLL vote support.

The file follows the older Qualcomm GCC style: basic `struct clk_pll` PLLs with vote clocks, `clk_rcg2` roots with frequency tables, direct branch gates, voted branches, GDSCs, and a large reset map.

## Important APIs, Types, And Data

Core types are `struct clk_pll`, `struct clk_regmap`, `struct clk_rcg2`, `struct clk_branch`, `struct gdsc`, `struct qcom_reset_map`, `struct regmap_config`, and `struct qcom_cc_desc`.

Three GPLLs are modeled as `clk_pll` objects: `gpll0`, the main general PLL parent used by most peripheral RCGs; `gpll1`, used by HSIC-related clocks; and `gpll4`, used by SDCC high-rate options. Each PLL also has a vote clock (`gpll0_vote`, `gpll1_vote`, `gpll4_vote`) sharing the vote register at `0x1480`. Parent maps connect XO, GPLL votes, external SATA/PCIe pipe sources, and sleep clock inputs. RCG definitions provide rate tables for UFS AXI, USB3 master/mock UTMI, BLSP I2C/SPI/UART, crypto engines, GP clocks, PCIe aux/pipe, PDM, SATA, SDCC, TSIF, USB HS, and USB HSIC.

The main public registration tables are `gcc_apq8084_clocks[]`, `gcc_apq8084_gdscs[]`, `gcc_apq8084_resets[]`, and `gcc_apq8084_desc`.

## Control Flow

The driver is registered through a manual init/exit pair. `core_initcall(gcc_apq8084_init)` registers `gcc_apq8084_driver` early. The platform bus matches `qcom,gcc-apq8084`. `gcc_apq8084_probe()` registers the board XO clock as `xo_board` at 19.2 MHz by calling `qcom_cc_register_board_clk(dev, "xo_board", "xo", 19200000)`, registers the sleep clock through `qcom_cc_register_sleep_clk()`, and then calls `qcom_cc_probe()` with `gcc_apq8084_desc`. The common probe path maps the register space, registers clocks, resets, and GDSCs, and exposes them to CCF, reset-controller, and genpd consumers.

Once registered, individual consumer operations flow through CCF ops: `clk_pll_ops`, `clk_pll_vote_ops`, `clk_rcg2_ops`, `clk_rcg2_floor_ops`, `clk_branch2_ops`, and `clk_branch_simple_ops`.

## State And Persistence

The driver itself stores no mutable software state beyond static clock descriptors. Hardware registers hold all persistent state: PLL L/M/N/config/mode/status registers, vote registers, RCG command/config registers, branch CBCR bits, halt status, reset bits, and GDSC power-domain state. The board and sleep clocks registered during probe become CCF objects used as parents by the GCC tree.

Voted branches are significant state: many AHB/AXI clocks use shared enable registers such as `0x1484` with `BRANCH_HALT_VOTED`, while the actual halt register is peripheral-specific. The MMSS GPLL0 vote uses a simple branch object to expose a vote path to the display/multimedia subsystem.

## Dependencies And Integration Points

This file depends on Qualcomm common clock infrastructure: `common.h`, `clk-regmap.h`, `clk-pll.h`, `clk-rcg.h`, `clk-branch.h`, `reset.h`, and `gdsc.h`. It also depends on APQ8084 clock and reset binding headers. Devicetree must provide `qcom,gcc-apq8084`, the `xo` input, and external parents for PCIe pipe, SATA ASIC/RX, UFS symbol clocks, and sleep clock paths where used.

The driver integrates with CCF consumers, reset-controller consumers, genpd consumers, storage and interconnect-facing drivers, and USB, PCIe, BLSP, crypto, PDM, TSIF, and PRNG drivers.

## Risks And Test Signals

The largest risk is index alignment with two binding headers. `gcc_apq8084_clocks[]`, `gcc_apq8084_gdscs[]`, and `gcc_apq8084_resets[]` are sparse arrays keyed by ABI constants. Register offsets are dense and repetitive, and the file mixes direct gates and voted gates, so using the wrong halt policy can cause false halt timeouts or premature success. External parent names such as `pcie_pipe`, `sata_asic0_clk`, `sata_rx_clk`, UFS symbol sources, `sleep_clk`, and `xo_board` must match devicetree and board-clock registration.

Build coverage should compile this driver with both APQ8084 binding headers and `CONFIG_COMMON_CLK_QCOM`. Probe tests should check that `xo_board` and `sleep_clk` register successfully and that `qcom_cc_probe()` does not fail. Runtime validation should use `/sys/kernel/debug/clk/clk_summary` to inspect PLL vote enables, BLSP rates, SDCC floor-rate behavior, USB/PCIe/SATA/UFS branches, and MMSS GPLL0 vote behavior. Power-domain tests should attach/detach PCIe and USB consumers and verify GDSC state transitions.
