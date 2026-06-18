# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_c62xvf/adf_c62xvf_hw_data.c

## Purpose
This file initializes C62x VF hardware metadata. It describes the VF as one accelerator, one AE, one ETR bank, fixed Gen2 ring layout, VF interrupt resources, no local admin/arbiter/error-correction operations, and PF/VF notification based startup/shutdown.

## Important APIs, Types, And Functions
Public functions are `adf_init_hw_data_c62xiov()` and `adf_clean_hw_data_c62xiov()`. Local fixed-return helpers provide masks, counts, BAR IDs, and `DEV_SKU_VF`. Noop functions are used for PF-only lifecycle callbacks.

## Control Flow
Initialization fills `hw_data` with VF class, bank/ring geometry, fixed service map, VF ISR callbacks, noops for admin/arbiter/error correction/interrupt enabling, PF/VF init and shutdown notifications, fixed resource callbacks, Gen2 device config, class index updates, VF PFVF ops, CSR ops, and DC ops. Cleanup decrements class instances and updates class indexes.

## State And Persistence Behavior
Runtime state is limited to `hw_data` and class instance count. Actual PF-owned state is coordinated over PF/VF messages rather than local admin firmware calls.

## Dependencies And Integration Points
It depends on Gen2 config, CSR/DC helpers, VF ISR code, and PF/VF VF-message helpers. It is used by the C62x VF PCI driver.

## Risks
The common framework must tolerate noops for PF-only operations. Any mismatch in one-bank ring geometry or TX/RX offset breaks VF transport. Class index updates depend on device-manager list consistency.

## Test Signals
Successful VF probe, PF/VF init/shutdown messaging, one-bank transport setup, interrupt delivery, algorithm registration, and class index cleanup on VF removal validate the file.
