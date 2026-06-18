# sources/distributed-fs/ceph-client/drivers/mmc/host/mmci_stm32_sdmmc.c Research

## sources/distributed-fs/ceph-client/drivers/mmc/host/mmci_stm32_sdmmc.c

### Purpose
`mmci_stm32_sdmmc.c` implements the STM32 SDMMC variant layer for the common MMCI driver. It replaces generic DMA-engine handling with STM32 internal DMA, supplies STM32 clock and power programming, handles STM32 busy detection and signal-voltage switching, and optionally performs high-speed tuning through an external delay block.

### Important APIs, Types, And Functions
The external entry point is `sdmmc_variant_init(struct mmci_host *host)`. Local state types are `struct sdmmc_idma`, `struct sdmmc_lli_desc`, `struct sdmmc_dlyb`, and `struct sdmmc_tuning_ops`. IDMA functions include `sdmmc_idma_validate_data()`, `sdmmc_idma_prep_data()`, `sdmmc_idma_unprep_data()`, `sdmmc_idma_setup()`, `sdmmc_idma_start()`, `sdmmc_idma_error()`, and `sdmmc_idma_finalize()`. Variant callbacks include `mmci_sdmmc_set_clkreg()`, `mmci_sdmmc_set_pwrreg()`, `sdmmc_get_dctrl_cfg()`, `sdmmc_busy_complete()`, `sdmmc_pre_sig_volt_vswitch()`, `sdmmc_post_sig_volt_switch()`, and `sdmmc_execute_tuning()`.

### Control Flow
Initialization installs `sdmmc_variant_ops`, snapshots the current power register, maps an optional second MMIO resource for the delay block, chooses MP15 or MP25 tuning ops by compatible string, stores it in `host->variant_priv`, and wires `execute_tuning` into the shared MMC ops. Data validation decides whether the scatterlist can be used directly by IDMA; unaligned offsets or non-final unaligned lengths allocate and enable a coherent bounce buffer. Preparation maps SGs or copies write data into the bounce buffer. `sdmmc_idma_start()` enables either simple base-address IDMA or linked-list IDMA descriptors depending on variant support, SG count, and bounce usage. Completion disables IDMA and unmaps/copies read data when no pre-request cookie remains. Clock setup calculates STM32 divisors, DDR flags, bus width bits, high-speed bus-speed bits, and extra clock-select flags. Power setup uses reset for power-off, power-cycle state to avoid back-powering through signal lines, then power-off and power-on transitions on `MMC_POWER_ON`.

### State, Persistence, And Dependencies
Variant private state holds IDMA descriptor memory, bounce buffer DMA address, and delay-block configuration. Persistent hardware state includes STM32 IDMA registers, FIFO threshold, clock register, power-cycle/voltage-switch bits, delay-block control/configuration, and busy-end interrupt masks. The file depends on MMCI core state, MMC tuning helpers, coherent DMA allocation, DMA mapping, `readl_relaxed_poll_timeout()`, reset control, OF resource mapping, and STM32 SDMMC register definitions from `mmci.h`.

### Integration Points
The callbacks are selected by STM32 SDMMC `variant_data` entries in `mmci.c`. `sdmmc_get_dctrl_cfg()` cooperates with core request flow by selecting STM32 block, SDIO, stream, or block-stop modes and by programming revision-3 FIFO thresholds for SDR104/HS200. Busy detection plugs into `mmci_cmd_irq()` through `.busy_complete`. Voltage switching plugs into `mmci_sig_volt_switch()` before and after regulator changes. Tuning uses `mmc_send_tuning()` to scan delay phases and stores the selected delay in hardware.

### Risks
IDMA alignment constraints are subtle: the last SG element has weaker size rules than earlier entries, while offset alignment always matters. Bounce-buffer allocation uses `host->mmc->max_req_size`, so transfer limit configuration must be correct before validation. Linked-list descriptors rely on coherent descriptor memory and exact end-of-list flags. Power-off asserts/deasserts reset and then writes power-cycle state, so reset availability and register cache restoration must match the core. Tuning can fail if the delay block is absent, not locked, or has no valid window; high-speed modes above 50 MHz depend on this path. Voltage switch handling waits up to 10 ms and must clear both voltage-switch and clock-stop flags.

### Test Signals
Test direct and bounce-buffer DMA, single-SG and multi-SG linked-list IDMA, odd SDIO block-stop modes, SDR104/HS200 tuning, MP15 and MP25 delay blocks, power-off/on cycles, R1B busy completion, voltage switch to 1.8 V, and runtime suspend/resume through the MMCI core. Fault injection should cover DMA mapping failure, delay-lock timeout, no tuning window, and IDMA error cleanup.
