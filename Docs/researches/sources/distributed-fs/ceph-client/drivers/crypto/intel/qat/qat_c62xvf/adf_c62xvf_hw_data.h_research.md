# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_c62xvf_hw_data.h

## Purpose
This header defines fixed C62x VF geometry: PMISC and ETR BAR IDs, one accelerator/AE masks and counts, TX/RX ring placement, one ETR bank, and hardware-data init/clean declarations.

## Important APIs, Types, And Functions
It declares `adf_init_hw_data_c62xiov()` and `adf_clean_hw_data_c62xiov()`. Important constants include `ADF_C62XIOV_PMISC_BAR`, `ADF_C62XIOV_ETR_BAR`, `ADF_C62XIOV_ACCELERATORS_MASK`, `ADF_C62XIOV_ACCELENGINES_MASK`, `ADF_C62XIOV_RX_RINGS_OFFSET`, `ADF_C62XIOV_TX_RINGS_MASK`, and `ADF_C62XIOV_ETR_MAX_BANKS`.

## Control Flow
There is no executable flow. The constants are read by C62x VF metadata initialization and PCI BAR setup.

## State And Persistence Behavior
No mutable state exists. Values compile into the VF module.

## Dependencies And Integration Points
The header integrates with Gen2 VF CSR/transport setup and the C62x VF PCI driver.

## Risks
Wrong fixed geometry can corrupt ring programming or prevent interrupts. Since VFs have no firmware names here, the common framework relies on PF/VF coordination rather than local firmware state.

## Test Signals
VF bind/start, one-bank ring traffic, PF/VF notifications, and clean removal are indirect validation.
