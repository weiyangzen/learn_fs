# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/mhi.h

## Purpose

`mhi.h` is the shared MHI interface for the PCI-backed ath12k bus. It defines the register offsets used by reset/vector cleanup, the driver-local MHI state enum, and the exported lifecycle helpers implemented in `mhi.c`.

## Important APIs And Types

- Register constants `PCIE_TXVECDB`, `PCIE_TXVECSTATUS`, `PCIE_RXVECDB`, and `PCIE_RXVECSTATUS` identify vector doorbell/status registers cleared during PCI reset.
- `MHISTATUS`, `MHICTRL`, and `MHICTRL_RESET_MASK` support clearing SYSERR-like MHI controller state after SoC global reset.
- `enum ath12k_mhi_state` enumerates driver-requested transitions: init/deinit, power on/off, keep-device power off, forced power off, suspend/resume, trigger RDDM, RDDM, and RDDM done.
- Public functions include register/unregister, start/stop, suspend/resume, vector clearing, reset-bit setting, and coredump download.

## Control Flow And Integration

`pci.c` includes this header to call `ath12k_mhi_register()` during probe, `ath12k_mhi_start()` during power-up, `ath12k_mhi_stop()` during power-down, and suspend/resume wrappers in HIF PM callbacks. Reset paths call `ath12k_mhi_clear_vector()` and `ath12k_mhi_set_mhictrl_reset()` around PCI global reset. Coredump code calls `ath12k_mhi_coredump()` to enter/download RDDM.

## State And Persistence

The header does not allocate state, but its enum values are used as bit positions in `ath12k_pci::mhi_state`. That means enum ordering is semantically important. The declared functions mutate PCI registers, MHI core state, and ath12k recovery state through `struct ath12k_pci` and `struct ath12k_base`.

## Dependencies, Risks, And Test Signals

It includes `pci.h`, so users get `struct ath12k_pci` and `struct ath12k_base` definitions. Risks are mostly ABI-like: changing enum order can corrupt bit-state checks, and changing register constants can break reset recovery. Test signals are successful build across PCI and MHI units plus runtime boot, suspend/resume, reset, and crash-dump tests.
