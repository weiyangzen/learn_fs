# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c3xxxvf/adf_c3xxxvf_hw_data.h

## Purpose
This header defines the fixed hardware geometry for C3xxx VFs: BAR IDs, one accelerator/AE, ring offsets, TX ring mask, one ETR bank, and hardware-data init/clean declarations.

## Important APIs, Types, And Functions
It declares `adf_init_hw_data_c3xxxiov()` and `adf_clean_hw_data_c3xxxiov()`. Important constants include `ADF_C3XXXIOV_PMISC_BAR`, `ADF_C3XXXIOV_ETR_BAR`, `ADF_C3XXXIOV_ACCELERATORS_MASK`, `ADF_C3XXXIOV_ACCELENGINES_MASK`, `ADF_C3XXXIOV_RX_RINGS_OFFSET`, `ADF_C3XXXIOV_TX_RINGS_MASK`, and `ADF_C3XXXIOV_ETR_MAX_BANKS`.

## Control Flow
There is no executable flow. The constants drive VF metadata initialization and PCI BAR indexing in the C3xxx VF driver.

## State And Persistence Behavior
No mutable state exists. Values compile into the VF module and establish the common framework's view of the VF.

## Dependencies And Integration Points
It is consumed by `adf_c3xxxvf_hw_data.c` and the C3xxx VF PCI driver. It integrates with Gen2 VF CSR and transport setup.

## Risks
Because VFs expose a constrained resource subset, wrong geometry values can corrupt ring setup or interrupt handling. The TX/RX offset and mask must stay synchronized with firmware/PF resource assignment.

## Test Signals
Successful VF probe, one-bank transport setup, TX/RX ring operation, PF/VF init/shutdown messages, and clean VF removal validate this header indirectly.
