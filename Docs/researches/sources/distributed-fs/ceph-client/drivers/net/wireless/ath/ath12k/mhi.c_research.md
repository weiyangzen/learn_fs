# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mhi.c

## Purpose

`mhi.c` adapts ath12k PCI devices to the Linux MHI bus. It registers an `mhi_controller`, supplies firmware image information, binds MSI vectors, drives the MHI power-state machine, handles firmware crash/RDDM callbacks, and exposes helpers used by PCI reset and coredump code.

## Important APIs And Functions

- `ath12k_mhi_register()` allocates and initializes `struct mhi_controller`, selects dual-MAC or normal AMSS firmware from `firmware-N.bin` or the legacy `mhi.bin` path, assigns MSI IRQs, sets DMA/iova limits and callbacks, then calls `mhi_register_controller()`.
- `ath12k_mhi_unregister()` releases the controller, allocated IRQ array, and ath12k pointer.
- `ath12k_mhi_start()` transitions through `ATH12K_MHI_INIT` and `ATH12K_MHI_POWER_ON`; `ath12k_mhi_stop()` powers down, optionally with `mhi_power_down_keep_dev()` during suspend, then deinitializes.
- `ath12k_mhi_suspend()` and `ath12k_mhi_resume()` call MHI PM suspend/resume through the same guarded state helper.
- `ath12k_mhi_set_mhictrl_reset()` and `ath12k_mhi_clear_vector()` reset MHI/PCI vector registers after global reset or before rebooting firmware.
- `ath12k_mhi_coredump()` delegates RDDM image download to the MHI core.

## Control Flow

PCI probe calls `ath12k_mhi_register()` after MSI allocation and before HAL/CE setup. PCI power-up later calls `ath12k_mhi_start()`, which uses `mhi_prepare_for_power_up()` followed by synchronous MHI power-up so QRTR channels are ready before resume paths continue. Power-down reverses this by calling MHI power down and unprepare. MHI status callbacks translate MHI events into ath12k recovery behavior: `MHI_CB_EE_RDDM` sets crash/recovery flags and queues `reset_work`, while consecutive RDDM callbacks are suppressed by `mhi_pre_cb`.

## State And Persistence

State is stored in `ath12k_pci::mhi_ctrl`, `mhi_state`, `mhi_pre_cb`, and firmware buffer/path fields. `ath12k_mhi_set_state_bit()` records coarse state bits for init, power-on, suspend, trigger-RDDM, and RDDM-done; `ath12k_mhi_check_state_bit()` prevents invalid transitions and logs current bit state. Firmware buffers are owned by ath12k core firmware mappings or by the MHI firmware image path.

## Dependencies And Integration

The file depends on Linux MHI, PCI/MSI, firmware, IRQ, and bit helpers. It integrates tightly with `pci.c` for register access and MSI assignment, `core.h` for firmware blobs and recovery flags, and `debug.h` for diagnostics. It relies on hardware parameters for MHI config, RDDM size, OTP board-id register, and firmware layout.

## Risks And Test Signals

Risks include incorrect MHI state transitions, missing IRQ cleanup on register failure, firmware selection mismatches for dual-MAC board IDs, and recovery storms if RDDM callbacks repeat. Suspend uses a keep-device workaround because normal power-down can break resume. Test signals include PCI probe/tear-down, firmware boot to mission mode, suspend/resume, forced firmware crash with RDDM collection, one-vector and multi-vector MSI configurations, and fallback loading from legacy `mhi.bin`.
