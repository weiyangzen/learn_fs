# sources/distributed-fs/ceph-client/drivers/crypto/intel/qat/qat_dh895xccvf/adf_dh895xccvf_hw_data.c

Purpose: defines hardware-data callbacks for DH895xCC SR-IOV virtual functions.

Important APIs and functions: `adf_init_hw_data_dh895xcciov()` sets one accelerator, one engine, one ETR bank, ring layout, VF IRQ resource handlers, no-op admin/arbiter/error-correction hooks, PF notification hooks (`adf_vf2pf_notify_init()` and shutdown), BAR IDs, SKU `DEV_SKU_VF`, gen2 config, class accounting, PFVF ops, CSR ops, and DC ops. `adf_clean_hw_data_dh895xcciov()` decrements class instances and updates class index.

Control flow: VF probe calls the init function after allocating `hw_data`; common `adf_dev_up(accel_dev, false)` uses the populated callbacks to configure rings and notify the PF instead of loading firmware directly.

State and persistence: class instance count is persistent across VF devices. All other state is stored in `hw_data` owned by the VF `adf_accel_dev`.

Dependencies and integration points: integrates with ADF VF ISR resources, gen2 config/CSR/DC operations, PFVF messaging, and the dev manager class index.

Risks and test signals: VF support relies on PF cooperation; no-op local admin/arbiter methods are intentional but make PF notification failures important. Tests should cover class instance accounting, PFVF init/shutdown messages, ring layout compatibility with PF, and multiple VFs probing/removing.
