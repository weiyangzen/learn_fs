# subset-b-004272 Research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmci.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/mmci.c

### Purpose
`mmci.c` is the Linux MMC core-facing driver for ARM PrimeCell PL180/PL181-compatible Multimedia Card Interface controllers and a family of derived ST, STM32, Ux500, and Qualcomm SDCC integrations. It registers an AMBA driver, maps the controller register block, exposes `struct mmc_host_ops`, handles command/data request sequencing, and funnels hardware differences through `struct variant_data` plus `struct mmci_host_ops` callbacks declared in `mmci.h`. It is the common base used by the companion Qualcomm DML and STM32 SDMMC variant files in this work item.

### Important APIs, Types, And Functions
The primary exported-to-core API is `mmci_ops`, whose callbacks include `mmci_request()`, `mmci_pre_request()`, `mmci_post_request()`, `mmci_set_ios()`, `mmci_get_cd()`, `mmci_sig_volt_switch()`, and conditionally SDIO IRQ/card-busy callbacks. Driver lifecycle is `mmci_probe()`, `mmci_remove()`, runtime PM through `mmci_runtime_suspend()`/`mmci_runtime_resume()`, and AMBA matching through `mmci_ids[]`. Request internals are split across `mmci_start_command()`, `mmci_start_data()`, `mmci_cmd_irq()`, `mmci_data_irq()`, `mmci_pio_irq()`, `mmci_irq()`, `mmci_irq_thread()`, and `mmci_request_end()`. DMA-engine support is implemented by `mmci_dmae_setup()`, `mmci_dmae_prep_data()`, `mmci_dmae_start()`, `mmci_dmae_finalize()`, `mmci_dmae_error()`, and `mmci_dmae_unprep_data()`. Variant initialization uses `mmci_variant_init()`, `ux500_variant_init()`, `ux500v2_variant_init()`, `qcom_variant_init()`, and `sdmmc_variant_init()`.

### Control Flow
Probe allocates `struct mmc_host`/`struct mmci_host`, parses DT and ST-specific properties, acquires pinctrl when the variant lacks a hardware open-drain bit, enables the AMBA clock, maps registers, calls the variant `init` callback, derives `f_min`/`f_max`, obtains regulators/reset, programs MMC capabilities and transfer limits, requests command/data IRQs, enables the base interrupt mask, configures DMA, registers the MMC host, then lets runtime PM autosuspend the device. Requests enter `mmci_request()`: data is validated, preprepared DMA can be consumed through `mmci_get_next_data()`, read/datactrl-first transfers call `mmci_start_data()` before the command, and SBC or main command is issued with `mmci_start_command()`. IRQ handling reads masked status, clears handled bits, optionally runs PIO service on the same IRQ, then processes command and data completion in variant-selected order. Data completion finalizes DMA or PIO, sets bytes transferred, issues STOP/CMD12 when needed, or completes the request. Command completion decodes responses and command errors, handles R1B busy detection, starts data for write-after-command variants, advances SBC to the main command, or completes the request.

### State, Persistence, And Dependencies
Runtime state is held in `struct mmci_host`: current `mrq`, `cmd`, `data`, cached power/clock/datactrl registers, busy-detect state/status, PIO iterator, DMA private data, next DMA cookie, regulator-enable state, pinctrl handles, reset control, and delayed work for Ux500 busy timeout. Persistent hardware-visible state includes power/clock/data-control registers, interrupt masks, stop-abort command state, regulator state, and variant-specific signal-direction/clock-select bits parsed from DT. Suspend saves/gates interrupts and, for no-power-register variants, writes power/clock/datactrl to zero; resume restores cached register values and interrupt masks. Dependencies include the MMC core, AMBA bus, clock/reset/regulator/pinctrl/GPIO frameworks, DMA engine, scatterlist helpers, runtime PM, and optional companion variant objects selected by Kconfig.

### Integration Points
The `variant_data` table maps AMBA IDs to controller behavior: ARM PL180/181, extended FIFO variants, U300/Nomadik/Ux500, STM32 PL18x and STM32 SDMMC revisions, and Qualcomm SDCC. `mmci.h` register definitions and variant callbacks are the internal contract with `mmci_qcom_dml.c` and `mmci_stm32_sdmmc.c`. Device tree integration flows through `mmc_of_parse()` plus ST properties such as `st,sig-dir-*`, `st,neg-edge`, and `st,use-ckin`. DMA integration uses named `"rx"`/`"tx"` channels. MMC core integration exposes command queue pre/post request cookie handling, CMD23, busy wait, signal-voltage switching, card-detect/write-protect GPIOs, SDIO interrupt support on capable variants, and runtime/system sleep PM.

### Risks
The largest risk is state-machine ordering: datactrl-first, read-before-command, write-after-command, SBC, stop-abort, DMA fallback, and busy-detect variants all share the same IRQ paths. Incorrect interrupt ordering or mask handling can complete a request before data, lose busy-end status, or leave a DMA transfer mapped. DMA fallback is deliberately dynamic; a buggy DMA controller can force permanent PIO fallback after FIFO residue is detected. R1B busy timeout on variants with `busy_timeout` can require a threaded reset path, so reset restoration must preserve cached clock/power state. Global mutation of `mmci_ops` for card-busy and SDIO callbacks is subtle because the static ops object is shared by all instances. PIO logic must handle odd SDIO byte counts even though the FIFO is 32-bit. DT properties and variant flags must match silicon or clock divisors, open-drain behavior, signal direction, data length limits, and IDMA/DML hooks can be wrong.

### Test Signals
Useful signals include probe on every AMBA ID family, `mmc_test` block read/write and multi-block stop cases, SDIO small odd-length PIO transfers, DMA and forced-DMA-failure fallback, pre/post request cookie reuse, CMD23/SBC paths, R1B busy commands with timeout injection, SD voltage switching, card-detect/write-protect GPIOs, runtime suspend/resume with cached register restore, and SDIO IRQ enable/ack behavior. For variant coverage, test Ux500 busy double-IRQ behavior, STM32 datactrl-first and voltage-switch paths through the companion variant, and Qualcomm DML DMA start sequencing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmci.h -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/mmci.h

### Purpose
`mmci.h` is the private register, bitfield, variant, and host-state contract for the PrimeCell MMCI driver family. It defines the PL180/181 register map, ST/STM32/Qualcomm register extensions, interrupt masks, FIFO/DMA constants, the variant description used by `mmci.c`, callback operations overridden by companion variant files, and the full `struct mmci_host` runtime state.

### Important APIs, Types, And Functions
Important types are `enum mmci_busy_state`, `struct variant_data`, `struct mmci_host_ops`, and `struct mmci_host`. `variant_data` encodes clock register values, command response encoding, data-control quirks, FIFO sizes, DMA restrictions, busy-detection bits, IRQ layout, open-drain bits, STM32 IDMA geometry, SDIO IRQ support, and the per-variant `init()` callback. `mmci_host_ops` is the callback table for data validation/preparation, DMA setup/start/finalization/error, clock/power writes, data-control configuration, busy completion, and signal-voltage switching. Function prototypes expose core helpers to variant files: `mmci_write_clkreg()`, `mmci_write_pwrreg()`, `mmci_dmae_*()`, `qcom_variant_init()`, and `sdmmc_variant_init()`.

### Control Flow
This header has no executable control flow except the inline `mmci_dctrl_blksz()`, which encodes the current data block size as `(ffs(blksz) - 1) << 4` for classic data-control registers. At runtime, `mmci.c` selects a `variant_data` from AMBA match data, calls its `init()`, and then uses the resulting `mmci_host_ops` table for request-specific behavior. Companion files implement `qcom_variant_init()` and `sdmmc_variant_init()` only when their Kconfig options are enabled; otherwise static inline no-op stubs keep `mmci.c` buildable.

### State, Persistence, And Dependencies
`struct mmci_host` documents all persistent per-controller state: MMIO base/physical address, current request command/data, stop-abort command, clock and regulator handles, spinlock, cached clock/power/data-control registers, busy-detect state, mask1 cache, variant-private pointer, pinctrl open-drain state, hardware designer/revision, PIO scatterlist iterator and byte count, DMA progress/private data, next pre-request cookie, and delayed Ux500 busy work. The register constants define the persistent hardware state written by `mmci.c` and variant files, including power, clock, command, data timer/length/control, status/clear/masks, FIFO count/data, and STM32 IDMA descriptors.

### Integration Points
The header is consumed by `mmci.c`, `mmci_qcom_dml.c`, and `mmci_stm32_sdmmc.c`. It also bridges to external kernel subsystems through forward declarations and types from MMC, DMA engine, clock, reset, pinctrl, and platform data headers included by users. Conditional prototypes bind to `CONFIG_DMA_ENGINE`, `CONFIG_MMC_QCOM_DML`, and `CONFIG_MMC_STM32_SDMMC`, making the base driver compile across configurations while preserving variant hooks.

### Risks
Most fields are low-level hardware contracts, so bit drift is high impact. A wrong mask can corrupt clocking, response decoding, SDIO IRQ delivery, or busy-detect completion. `variant_data` contains many one-bit booleans with similar names; mixing `busy_detect`, `busy_timeout`, `datactrl_first`, `datacnt_useless`, or `dma_lli` changes core control flow. `mmci_dctrl_blksz()` assumes power-of-two block sizes and relies on prior validation for variants that cannot handle arbitrary sizes. Because `struct mmci_host_ops` instances are mutable in `mmci.c`, callback ownership must remain carefully scoped.

### Test Signals
Header validation is indirect: build all Kconfig combinations with and without DMA engine, Qualcomm DML, and STM32 SDMMC; boot probe each variant ID; verify register values written for bus width, DDR timing, SDIO mode, busy detection, IDMA, and DML. Static review should compare register offsets/bitfields against TRMs for PL180/181, Ux500, STM32 SDMMC, and Qualcomm SDCC.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmci_qcom_dml.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/mmci_qcom_dml.c

### Purpose
`mmci_qcom_dml.c` supplies the Qualcomm-specific Data Mover Lite glue for the common MMCI driver. Qualcomm SDCC integrations use the normal MMCI DMA-engine path plus an SDCC-local DML block at `host->base + 0x800` to connect producer/consumer CRCI signaling and BAM pipe IDs for read/write DMA transfers.

### Important APIs, Types, And Functions
The only externally visible function is `qcom_variant_init(struct mmci_host *host)`, which installs `qcom_variant_ops`. The callback table overrides `.prep_data`, `.unprep_data`, `.get_datactrl_cfg`, `.get_next_data`, `.dma_setup`, `.dma_release`, `.dma_start`, `.dma_finalize`, and `.dma_error`. Key helpers are `qcom_dma_setup()`, `qcom_dma_start()`, `of_get_dml_pipe_index()`, and `qcom_get_dctrl_cfg()`. Register definitions cover `DML_CONFIG`, reset/start registers, producer/consumer pipe sizes, pipe IDs, and producer BAM block/transaction sizes.

### Control Flow
During MMCI probe, the Qualcomm `variant_data` calls `qcom_variant_init()`, replacing the base ops. `qcom_dma_setup()` first calls `mmci_dmae_setup()` to acquire standard `"rx"`/`"tx"` DMA channels. It then reads the DMA phandle arguments named `"tx"` and `"rx"` to derive the consumer and producer DML pipe IDs; missing IDs cause DMA release and setup failure. On success it resets DML, disables CRCI bypass/direct/infinite modes, programs producer/consumer logical pipe sizes to 4096 bytes, writes the pipe ID register, and uses `mb()` to order initialization. Per transfer, `qcom_dma_start()` delegates descriptor submission to `mmci_dmae_start()`, then programs DML for producer mode on reads or consumer mode on writes, sets block and transaction sizes for reads, toggles `PRODUCER_TRANS_END_EN`, starts the selected DML side, and finishes with `wmb()` before the MMCI data path is triggered by the core.

### State, Persistence, And Dependencies
This file stores no separate private structure; it uses `host->base`, `host->data`, `host->mmc`, and the DMA-engine private data allocated by `mmci_dmae_setup()`. Persistent hardware state is the DML configuration, pipe IDs, logical pipe sizes, block size, transaction size, and producer/consumer start registers. Dependencies are DT `"dmas"`/`"dma-names"` properties, the DMA engine path in `mmci.c`, MMC data flags, and Qualcomm SDCC hardware layout with DML at offset `0x800`.

### Integration Points
The file integrates through the MMCI variant hook selected by the Qualcomm AMBA ID in `mmci.c`. It assumes both the standard MMCI DMA channels and DML pipe IDs refer to the same hardware data path. `qcom_get_dctrl_cfg()` differs from classic MMCI by encoding the block size directly as `host->data->blksz << 4`, matching the Qualcomm variant flag that accepts arbitrary block sizes.

### Risks
DML and DMA ordering is the core risk: the BAM/DML producer or consumer must be configured before the MMCI data-control register starts the transfer. Pipe ID extraction assumes the first DMA phandle argument is the BAM pipe ID; malformed DT silently disables DMA. The setup path returns `-EINVAL` for several distinct failures, reducing diagnosability. Read and write paths use different CRCI and producer-end semantics; swapping `"rx"`/`"tx"` names or pipe IDs can hang DMA rather than fail cleanly. There is no PIO-specific DML bypass programming here, so fallback behavior depends on reset/default DML state after failed setup.

### Test Signals
Validate with Qualcomm SDCC hardware using DMA reads and writes, including multi-block transfers and arbitrary block sizes. DT tests should cover missing `"rx"`/`"tx"` names, bad phandles, and swapped pipe IDs. Instrumentation should confirm DML reset/setup occurs once at probe, producer registers are used for reads, consumer start is used for writes, `mmci_dmae_start()` errors abort before DML starts, and PIO fallback still works when DML setup fails.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmci_qcom_dml.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmci_stm32_sdmmc.c -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mmci_stm32_sdmmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/moxart-mmc.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/moxart-mmc.c

### Purpose
`moxart-mmc.c` is a platform MMC host driver for MOXA ART/Faraday FTSdc010-style controllers. It implements a relatively synchronous request path around a memory-mapped command/data FIFO controller, optional DMA-engine channels, card-change interrupt handling, power/clock/bus-width programming, and basic write-protect reporting.

### Important APIs, Types, And Functions
The core state is `struct moxart_host`, which keeps the MMIO base, physical register address, DMA channels/descriptors, current MMC request, scatterlist cursor, completions for DMA/PIO, transfer length/remain counters, FIFO width, timeout/rate/sysclk, and removal/DMA flags. MMC callbacks are `moxart_request()`, `moxart_set_ios()`, and `moxart_get_ro()` through `moxart_ops`. Important helpers are `moxart_prepare_data()`, `moxart_send_command()`, `moxart_transfer_dma()`, `moxart_transfer_pio()`, `moxart_irq()`, `moxart_wait_for_status()`, and scatterlist cursor helpers.

### Control Flow
Probe allocates the MMC host, maps the resource, parses DT, reads the clock, discovers FIFO width from `REG_FEATURE`, tries to request `"tx"` and `"rx"` DMA channels, configures DMA slave addresses if available, sets MMC limits and 4-bit capability, resets the controller, requests the IRQ, and registers the host. A request initializes completions, stores `host->mrq`, checks the card-detect status bit, prepares data if present, sends the command by polling response status, then either performs DMA synchronously or waits for PIO completion driven by FIFO interrupts. After transfer, it checks removal, waits for data completion/error status, sets data errors, sends an explicit stop command if present, unlocks, and calls `mmc_request_done()`. The IRQ records card removal, terminates DMA if needed, signals detect change, and services FIFO under/overrun bits for PIO transfers.

### State, Persistence, And Dependencies
Persistent driver state includes current request, SG cursor, `data_len`, `data_remain`, `rate`, `fifo_width`, DMA availability, and `is_removed`. Hardware state is programmed through command, argument, response, data-control/timer/length, interrupt-mask, power-control, clock-control, and bus-width registers. The driver depends on platform DT resources, `mmc_of_parse()`, clock framework, DMA engine, DMA mapping, completions, spinlocks, and MMC core helpers.

### Integration Points
The OF match table binds `"moxa,moxart-mmc"` and `"faraday,ftsdc010"`. DMA channel names are `"tx"` and `"rx"`; when either is missing, the driver falls back to PIO unless probe deferral is required. The MMC core receives CMD/data completions through synchronous request completion. Card detection is controller-internal through `CARD_CHANGE`/`CARD_DETECT` rather than an MMC GPIO helper, while write protect is read from `WRITE_PROT`.

### Risks
The request path holds the host spinlock while polling command/data status, but drops it for DMA/PIO waits; races around card removal, `host->mrq`, and completions are therefore important. DMA completion timeout is not explicitly checked before setting `bytes_xfered = data_len`, so DMA hangs may be underreported until later data status. PIO assumes 32-bit word access and power-of-two block sizes enforced by `BUG_ON()`. Card-detect logic treats `CARD_DETECT` during request as timeout, so polarity assumptions must match hardware. Removal sets `host->mrq = NULL` in IRQ, which can race with in-flight PIO waiting. There is no runtime PM or regulator handling.

### Test Signals
Run probe with and without DMA channels, 1-bit and 4-bit bus modes, power off/on, write-protect readout, card insertion/removal during PIO and DMA, single/multi-block reads and writes, data CRC/timeout injection, stop-command paths, and transfer sizes below/above FIFO width. DMA timeout behavior should be checked carefully because completion timeout return value is ignored.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/moxart-mmc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mtk-sd.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/mtk-sd.c

### Purpose
`mtk-sd.c` is the MediaTek MSDC platform MMC/SD/SDIO/eMMC host driver. It supports many SoC generations through compatibility data, implements a DMA descriptor request engine, command/data IRQ state machine, SDIO IRQ and wake support, voltage switching, HS200/SDR104/HS400 tuning, optional CQHCI hardware command queue, optional MMC host software queue, runtime PM, and register save/restore.

### Important APIs, Types, And Functions
Key state types are `struct msdc_host`, `struct mtk_mmc_compatible`, `struct msdc_dma`, GPD/BD DMA descriptors, `struct msdc_save_para`, `struct msdc_tune_para`, and `struct msdc_delay_phase`. MMC callbacks are collected in `mt_msdc_ops`: request/pre/post, set_ios, card detect, voltage switch, card busy, SDIO IRQ enable/ack, tuning, HS400 tuning, enhanced strobe, and hardware reset. CQE hooks are `msdc_cqe_enable()`, `msdc_cqe_disable()`, `msdc_cqe_pre_enable()`, and `msdc_cqe_post_disable()`. Core request functions include `msdc_prepare_data()`, `msdc_dma_setup()`, `msdc_ops_request()`, `msdc_start_command()`, `msdc_cmd_done()`, `msdc_start_data()`, `msdc_data_xfer_done()`, `msdc_request_done()`, and `msdc_irq()`.

### Control Flow
Probe validates DT, allocates the host, parses MMC properties, maps base and optional top registers, gets regulators, clocks, reset, pinctrl states, optional SDIO wake IRQ, SoC tuning properties, and optional crypto clock. It sets transfer limits and DMA mask, allocates coherent GPD/BD descriptor arrays, ungates clocks, initializes hardware patch bits and SDIO/card-detect mode, initializes CQHCI or HSQ when enabled, requests the IRQ, enables runtime PM, and registers the MMC host. Requests always prepare DMA mappings, start SBC or main command, and then transition via IRQ: command completion captures responses/errors, auto-CMD status, and starts data when needed; data completion stops DMA, checks timeout/CRC/descriptor errors, updates bytes transferred, sends stop when needed, unmaps data, resets hardware on error, and completes through MMC core or HSQ finalization. A delayed work item simulates command/data timeouts if hardware IRQs do not arrive.

### State, Persistence, And Dependencies
`struct msdc_host` keeps current request/command/data, error flags, MMIO bases, DMA descriptors and mask, timeout settings, pinctrl states, delayed timeout work, IRQs, reset, multiple clocks, regulator-enable state, current timing/mclk/source clock, tuning parameters and saved tune results, HS400 mode flags, internal card-detect/SDIO/CQE/HSQ flags, saved registers, and CQE timer state. Persistent hardware state includes MSDC clock mode/dividers, SDC bus width/timeouts, DMA descriptors/registers, patch bits, pad tuning/top registers, CQE registers, interrupt masks, and SDIO wake/card-detect configuration. Dependencies include MMC core, `cqhci`, `mmc_hsq`, DMA mapping, pinctrl, regulators, clocks, resets, runtime/system PM, wake IRQ helpers, and many DT properties.

### Integration Points
The OF match table maps MediaTek SoCs (`mt2701`, `mt2712`, `mt6779`, `mt6795`, `mt7620`, `mt7622`, `mt7986/mt7988`, `mt8135`, `mt8173`, `mt8183`, `mt8189`, `mt8196`, `mt8516`) to `mtk_mmc_compatible` feature flags. DT supplies `"source"`, `"hclk"`, optional clock gates, reset `"hrst"`, pinctrl states, optional `"sdio_wakeup"` IRQ, tuning delay properties, and `"supports-cqe"`. The driver integrates with hardware CQE when present, or host software queue for eMMC/SD when SDIO is disabled. SDIO IRQ support can either keep runtime PM active or use a dedicated wake IRQ and `state_eint` pinctrl.

### Risks
The driver has a large hardware-variant matrix. Incorrect compatibility flags can choose the wrong clock divider bit layout, top-register usage, 64-bit DMA address handling, async FIFO behavior, stop-clock workaround, RX/TX enhancement, or SPM resource release. DMA descriptor checksums, high-4 address bits, and BD end-of-list flags are hand-built and must match mapped SG entries. Request timeout work races with normal IRQ completion and relies on `host->cmd`/`host->data` state. Tuning scans many phase combinations and can select marginal windows if `tuning_step`, internal delays, or top-base register layout are wrong. Runtime suspend saves/restores many registers and changes SDIO pinctrl/wake state; missing a register can break resume only in high-speed modes. CQE recovery must stop DMA and reset hardware without corrupting non-CQE fallback paths.

### Test Signals
High-value tests include probe on representative old/new SoCs, DMA reads/writes with many SG entries and 36-bit addresses, CMD23/SBC and auto-CMD23 behavior, SDIO IRQ recheck and wake IRQ paths, card-detect internal and GPIO modes, voltage switch with pinctrl changes, CQE enable/disable/recovery, HSQ request completion, delayed timeout injection, runtime suspend/resume after HS200/HS400 tuning, and error injection for command timeout/CRC, data timeout/CRC, and descriptor checksum/protect errors. Tuning should be validated across SDR50/SDR104/HS200/HS400 and with both top-base and legacy pad-tune layouts.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mtk-sd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mvsdio.c -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/mvsdio.c

### Purpose
`mvsdio.c` is the Marvell Orion SDIO/MMC/SD host driver. It drives a register interface described by `mvsdio.h`, supports one-fragment DMA or PIO fallback, handles controller-specific FIFO quirks, programs Marvell MBUS DRAM windows, provides SDIO card interrupt delivery, and exposes basic clock/power/bus-width control to the MMC core.

### Important APIs, Types, And Functions
The core state is `struct mvsd_host`, with MMIO base, current request, spinlock, cached transfer mode/interrupt/host-control registers, PIO buffer state, SG fragment count, clock timing, timeout timer, MMC host, device, and clock. MMC callbacks in `mvsd_ops` are `mvsd_request()`, `mvsd_set_ios()`, `mvsd_enable_sdio_irq()`, and GPIO write-protect. Major helpers are `mvsd_setup_data()`, `mvsd_finish_cmd()`, `mvsd_finish_data()`, `mvsd_irq()`, `mvsd_timeout_timer()`, `mvsd_power_up()`, `mvsd_power_down()`, and `mv_conf_mbus_windows()`.

### Control Flow
Probe requires DT, gets IRQ and clock, allocates the host, sets MMC limits, derives `base_clock`, parses MMC properties, maps registers, optionally programs MBUS windows from `mv_mbus_dram_info()`, powers the controller down, requests the IRQ, initializes the timeout timer, and registers the host. A request builds command, transfer, and interrupt masks, configures data if present, selects PIO when forced or when block size/SG offset/write alignment is unsafe for DMA, writes argument and command registers, enables normal/error interrupts, and arms a timer using command busy timeout or 5 seconds. IRQ first services PIO FIFO RX/TX events, then on command/data/auto-CMD/error completion disables interrupts, deletes the timer, finishes command and data, and completes the MMC request. The timer resets hardware and completes the request with timeout if no expected interrupt arrives.

### State, Persistence, And Dependencies
Runtime state is the current request plus cached `xfer_mode`, `intr_en`, `ctrl`, PIO pointer/size, SG DMA fragment count, `ns_per_clk`, and current clock. Hardware state includes block size/count, DMA address registers, argument/command, transfer mode, host-control timeout/bus mode, clock divisor, interrupt status/enables, reset, and optional MBUS remap windows. Dependencies include MMC core, clock framework, platform DT, Marvell MBUS helpers, DMA mapping, timers, unaligned access helpers, and register definitions from `mvsdio.h`. Module parameters `maxfreq` and `nodma` alter max clock and DMA usage.

### Integration Points
The OF compatible is `"marvell,orion-sdio"`. The driver uses GPIO helpers for write-protect and card-detect behavior parsed by `mmc_of_parse()`, but SDIO card interrupts are controller-native via `MVSD_NOR_CARD_INT`. MBUS window programming connects the controller DMA master to system DRAM. The MMC core sees `max_segs = 1`, large single-segment request limits, and controller-supported 3.2-3.4 V OCR.

### Risks
DMA is limited and alignment-sensitive: unaligned block sizes, unaligned offsets, and host-to-card buffers not 64-byte aligned fall back to PIO. `mvsd_setup_data()` maps only one SG address into hardware despite recording mapped fragments, consistent with `max_segs = 1`; violating that limit would be dangerous. FIFO behavior has documented quirks: FIFO_EMPTY may lag after unusual block sizes, RX FIFO 8-word status misses exactly-32-byte tails, and TX_FIFO_8W is unreliable. The timeout path calls finish helpers after reset while holding/releasing locks carefully; races with a late IRQ are possible. High-speed enable is disabled by `#if 0` due card compatibility problems, so performance expectations should account for that.

### Test Signals
Test PIO and DMA transfer paths, forced `nodma`, unaligned buffers and odd block sizes, exact 32-byte RX tails, small TX tails, multi-block with auto-CMD12, SDIO card interrupts, timeout recovery, MBUS window programming on Marvell platforms, module `maxfreq`, clock off/on transitions, and card-detect/write-protect integration. Fault injection should include command CRC/timeout, data CRC/timeout, auto-CMD12 errors, and late/spurious interrupts after masks are disabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mvsdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mvsdio.h -->
## sources/distributed-fs/ceph-client/drivers/mmc/host/mvsdio.h

### Purpose
`mvsdio.h` defines the private Marvell Orion SDIO/MMC controller register map and bitfields consumed by `mvsdio.c`. It is a hardware contract rather than executable logic, covering clock limits, command/transfer/host-control encoding, interrupt status/error bits, auto-CMD12 status, DMA/window registers, and reset/control offsets.

### Important APIs, Types, And Functions
There are no functions or C types beyond preprocessor constants. Important groups are register offsets such as `MVSD_SYS_ADDR_LOW`, `MVSD_BLK_SIZE`, `MVSD_CMD`, `MVSD_FIFO`, `MVSD_HOST_CTRL`, `MVSD_CLK_DIV`, interrupt enable/status registers, auto-CMD12 registers, and MBUS window registers. Bitfield groups define command response types and CRC/index checks, transfer-mode flags for write start, hardware write data, auto-CMD12, interrupt checking, read direction, stop clock, and PIO, host-control flags for push-pull, card type, endian/bit order, 4-bit width, high-speed, and timeout, normal interrupt bits, error bits, and auto-CMD12 error bits.

### Control Flow
The header has no control flow. `mvsdio.c` composes these constants into request-time command registers, transfer modes, interrupt masks, host-control settings, clock divisors, reset operations, DMA address programming, and error decoding.

### State, Persistence, And Dependencies
The persistent state represented by these constants lives in hardware registers. `mvsdio.c` caches selected values (`xfer_mode`, `intr_en`, `ctrl`) and writes them back using these definitions. The header depends only on inclusion by C code that provides standard integer/register access helpers; it uses no Linux types itself.

### Integration Points
This file is tightly coupled to `mvsdio.c` and the Marvell controller documentation. It also supports MBUS integration through `MVSD_WINDOW_CTRL()` and `MVSD_WINDOW_BASE()` macros, allowing `mvsdio.c` to program DRAM decode windows before DMA.

### Risks
Any incorrect offset or bit definition directly misprograms hardware. Timeout mask/index fields, response reconstruction assumptions, PIO/DMA transfer-mode bits, and normal/error interrupt masks are especially high impact because the driver uses them to decide request completion and error propagation. The header does not enforce field widths; callers must clamp divisors, timeout indices, and command indices correctly.

### Test Signals
Validation comes from exercising every consumer path in `mvsdio.c`: response types, auto-CMD12, PIO and DMA, SDIO interrupts, reset, timeout programming, 4-bit bus, push-pull/open-drain, MBUS windows, and all command/data/auto-CMD12 error statuses. Register dumps during known-good transfers are useful for comparing encoded constants against hardware documentation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/mmc/host/mvsdio.h -->
