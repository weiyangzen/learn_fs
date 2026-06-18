# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath11k/pci.h

Purpose: Defines PCIe hardware register constants and the per-device PCI private state used by ath11k's PCI HIF implementation. It is consumed by PCI, MHI, and PCIC code.

Important APIs, types, and constants: Register constants cover SoC global reset, WLAON warm/reset cause registers, Q6 cookie, PCIe wake scratch, LTSSM/hot reset, interrupt clear, QSERDES/PCS L1SS fixup registers from `hw_params`, QFPROM power control, and reset mask values. `enum ath11k_pci_flags` currently tracks whether ASPM should be restored. `struct ath11k_pci` stores the `pci_dev`, `ath11k_base`, device ID, AMSS path, MHI controller, MSI config pointer, previous MHI callback, register window cache and lock, flags, saved link control, and DMA mask. `ath11k_pci_priv()` casts `ab->drv_priv`, and `ath11k_pci_get_msi_irq()` exposes PCI vector lookup.

Control flow: `pci.c` initializes `struct ath11k_pci` at probe, fills hardware IDs and MHI/PCI state, and uses the register constants during reset/power sequencing. `mhi.c` uses the MHI controller pointer and AMSS path and calls `ath11k_pci_get_msi_irq()`. `pcic.c` uses common PCI ops installed by the PCI layer to access register windows and MSI vectors.

State and persistence behavior: The header declares runtime state but does not manage it. `register_window` caches the selected register window and must be protected by `window_lock`. `link_ctl` persists the pre-boot ASPM state so it can be restored. `dma_mask` is derived from PCI DMA mask configuration and later used for MHI IOVA range setup.

Dependencies and integration points: Depends on Linux MHI, PCI core through implementation users, and ath11k core structures. It bridges bus-specific private state into the common `ath11k_base` allocation.

Risks and edge cases: Register constants are hardware ABI values; incorrect offsets can wedge reset, wake, or L1SS behavior. `ath11k_pci_priv()` assumes `drv_priv` was allocated with `sizeof(struct ath11k_pci)`. Saved ASPM state must only be restored when it was actually cleared. The AMSS path buffer size must remain large enough for firmware paths built by core helpers.

Test signals: Compile all PCI/MHI users, probe supported PCI IDs, run reset and L1SS fixup paths on hardware with and without static register maps, validate ASPM save/restore, and verify MSI vector lookup with multi-vector and one-vector fallback.
