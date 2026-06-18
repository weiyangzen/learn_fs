# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/mhi.h

Purpose: Declares the ath11k MHI-facing API and the PCIe/MHI register offsets used by reset and vector-clear logic. It is the small boundary between PCI/HIF lifecycle code and the MHI implementation.

Important APIs and constants: Register constants define TX/RX vector doorbell/status offsets (`PCIE_TXVECDB`, `PCIE_TXVECSTATUS`, `PCIE_RXVECDB`, `PCIE_RXVECSTATUS`) and MHI control/status offsets (`MHISTATUS`, `MHICTRL`, `MHICTRL_RESET_MASK`). Public functions are `ath11k_mhi_register()`, `ath11k_mhi_unregister()`, `ath11k_mhi_start()`, `ath11k_mhi_stop()`, `ath11k_mhi_suspend()`, `ath11k_mhi_resume()`, `ath11k_mhi_set_mhictrl_reset()`, `ath11k_mhi_clear_vector()`, and `ath11k_mhi_coredump()`.

Control flow: `pci.c` includes this header to register MHI during probe, start MHI during power-up, stop it during power-down/suspend, clear vectors and reset MHI during software reset, and fetch RDDM data during devcoredump. The reset helpers are used before or after SoC global reset to restore the MHI block to a known state.

State and persistence behavior: The header has no own state, but it exposes functions that mutate `struct ath11k_pci` and `struct mhi_controller` lifecycle state. Register constants are stable hardware ABI values and must stay aligned with target PCIe/MHI register maps.

Dependencies and integration points: Includes `pci.h` for `struct ath11k_pci` and implicitly depends on MHI controller declarations through included PCI/core headers. It integrates with Linux MHI, ath11k PCI reset paths, and coredump collection.

Risks and edge cases: Wrong register offsets or reset mask values can leave firmware in SYSERR, miss vector cleanup, or break post-reset MHI boot. Function declarations must remain synchronized with `mhi.c`; signature drift breaks HIF build. The coredump declaration exposes an `mhi_controller` pointer, so callers must ensure the controller remains registered while downloading RDDM.

Test signals: Build with PCI/MHI ath11k enabled. Runtime validation should include warm reset after firmware crash, suspend/resume, vector clear around SoC reset, and coredump invocation before MHI unregister.
