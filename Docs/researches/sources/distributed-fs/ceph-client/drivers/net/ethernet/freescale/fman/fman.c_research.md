# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman.c

## Purpose

`fman.c` is the platform driver and central hardware bring-up layer for Freescale/NXP DPAA Frame Manager. It maps FMan device-tree resources, initializes the core register blocks (FPM, BMI, QMI, DMA, HW parser, KeyGen), allocates shared MURAM regions for DMA CAM and BMI FIFO, dispatches FMan and MAC interrupts, and exports the service APIs used by port and MAC drivers.

## Important APIs, Types, And Functions

The file defines internal big-endian register layouts for FPM, BMI, QMI, DMA, IRAM, and HWP blocks, plus `struct fman_state_struct` for runtime resource accounting and `struct fman_cfg` for one-shot initialization values. Public exported APIs include `fman_register_intr()`, `fman_unregister_intr()`, `fman_set_port_params()`, `fman_reset_mac()`, `fman_set_mac_max_frame()`, `fman_get_bmi_max_fifo_size()`, `fman_get_revision()`, `fman_get_qman_channel_id()`, `fman_get_mem_region()`, `fman_get_max_frm()`, `fman_get_rx_extra_headroom()`, and `fman_bind()`. With `CONFIG_DPAA_ERRATUM_A050385`, `fman_has_errata_a050385()` exports a global erratum flag read from device tree.

Key internal paths are `read_dts_node()`, `fman_config()`, `fman_init()`, `fman_reset()`, `dma_init()`, `fpm_init()`, `bmi_init()`, `qmi_init()`, `clear_iram()`, `enable_time_stamp()`, and `fill_soc_specific_params()`. Interrupt handling is split between `fman_err_irq()` for error pending bits and `fman_irq()` for normal pending bits.

## Control Flow

Module load registers a platform driver matching `fsl,fman`. Probe calls `read_dts_node()` to allocate `struct fman`, read `cell-index`, IRQs, clock, QMan channel range, and MURAM child resource, request normal/error IRQs, ioremap the FMan register resource, and populate child devices. `fman_config()` then allocates runtime state/config, creates a MURAM allocator, records register block pointers at fixed offsets, reads revision, applies SoC-specific limits, and prepares default thresholds. `fman_init()` saves LIODN state, resets the block, resumes QMI if halted, clears IRAM to avoid ECC noise, initializes DMA/FPM/BMI/QMI/HWP, allocates MURAM FIFO space, initializes KeyGen, enables BMI/QMI, enables timestamps, and frees the temporary config object to mark initialization complete.

Port setup enters through `fman_set_port_params()`. It takes `spinlock`, reserves task/FIFO/open-DMA resources, updates QMI thresholds for TX ports, restores LIODN programming, configures order restoration on pre-v3 hardware, and enforces that port max frame length is at least the MAC max frame length. MAC drivers register callbacks into `intr_mng[]`; the FMan IRQ handlers decode pending bits and fan out to module-specific handlers or registered MAC callbacks.

## State And Persistence Behavior

Persistent runtime state lives in `fman->state`, including revision, clock, exceptions, accumulated tasks/FIFO/open-DMA counts, per-MAC/port max frame lengths, QMan channel range, and SoC resource limits. `fman->cfg` exists only until successful init; `is_init_done()` treats a NULL config as initialized. MURAM allocations for CAM and FIFO are tracked by offsets and sizes. Boot/module parameters `fsl_fm_rx_extra_headroom` and `fsl_fm_max_frm` are lazily range-checked and then cached by static booleans on first getter call.

Hardware state is programmed via big-endian MMIO writes. LIODN values are read before reset and restored per port. Interrupt registration state is in memory and not persistent across driver reload.

## Dependencies And Integration Points

This file depends on Linux platform, OF, clock, IRQ, module, delay, and IO APIs; Freescale GUTS registers for FMan v3 reset erratum handling on PPC; `fman_muram` for MURAM allocation; and `fman_keygen` for KeyGen setup. Downstream integration is with MAC drivers (`fman_dtsec.c`, `fman_memac.c`, and peers), FMan port code via `fman_set_port_params()`, QMan channel consumers via `fman_get_qman_channel_id()`, and net buffer sizing via exported max-frame/headroom getters.

## Risks And Edge Cases

Resource accounting is manual and only grows; failed partial port setup can leave accumulated counters advanced because rollback is not performed after each reservation failure. Hardware polling uses short retry loops, making reset and IRAM failures sensitive to timing. Error IRQ absence disables many exception classes after init. `fman_bind()` increments the device reference through `get_device()` but returns only the driver pointer, so callers must follow the wider driver convention for device lifetime. This snapshot also shows apparent source corruption that a build should catch: doubled opening braces in `fman_bus_error()` and `fman_get_rx_extra_headroom()`, and a duplicate `case FMAN_EX_FPM_DOUBLE_ECC`.

## Test Signals

Build coverage is the first gate because this file has syntax-sensitive register structures and visible malformed tokens in the snapshot. Runtime validation should exercise probe failure paths, reset timeout handling, no-error-IRQ exception disabling, FMan v2/v3 revision branches, port resource exhaustion, LIODN restore with and without `CONFIG_FSL_PAMU`, module parameter range clamping, and MAC interrupt callback registration/unregistration. Hardware or emulation tests should confirm BMI/QMI thresholds, MURAM allocation offsets, KeyGen enablement, and normal/error IRQ fan-out.
