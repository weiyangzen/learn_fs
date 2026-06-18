# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath12k/wifi7/mhi.h

## Purpose

`mhi.h` declares the Wi-Fi 7 ath12k MHI controller configuration objects for use by hardware parameter tables.

## Important API/Data

It exports `ath12k_wifi7_mhi_config_qcn9274` and `ath12k_wifi7_mhi_config_wcn7850`, both typed as `const struct mhi_controller_config`. The definitions live in `mhi.c`.

## Control Flow And Integration

`hw.c` includes this header and assigns the exported configs to `ath12k_hw_params.mhi_config` for PCIe-capable Wi-Fi 7 chips. The selected config is later consumed by shared ath12k PCI/MHI setup code during device initialization.

## State And Persistence Behavior

The header owns no state; it only exposes immutable configuration descriptors.

## Dependencies

It depends on `struct mhi_controller_config` being visible to includers through their existing MHI/core includes. The header itself is intentionally small and guarded by `_ATH12K_WIFI7_MHI_H`.

## Risks And Edge Cases

Missing or stale extern declarations would break hardware parameter builds. If a hardware table references `NULL` for non-PCI/remoteproc devices, consumers must tolerate that separately; this header only covers the exported PCIe configs.

## Test Signals

Build tests should ensure both externs resolve and no hardware table points to an undeclared config. Runtime probe verifies the configs indirectly through successful MHI initialization.
