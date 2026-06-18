# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/hpre/hpre_main.c

## Purpose
This file is the PCI/QM lifecycle driver for HiSilicon HPRE accelerators. It initializes hardware registers, capabilities, error handling, debugfs, SR-IOV, runtime PM, UACCE registration, and the global HPRE device list used by `hpre_crypto.c` to allocate QPs and register algorithms.

## Important APIs, Types, and Functions
Important public/cross-file functions are `hpre_create_qp()`, `hpre_check_alg_support()`, and `hisi_hpre_get_pf_driver()`. PCI lifecycle functions are `hpre_probe()`, `hpre_remove()`, `hpre_init()`, and `hpre_exit()`. QM/device setup flows through `hpre_qm_init()`, `hpre_pre_store_cap_reg()`, `hpre_probe_init()`, `hpre_pf_probe_init()`, `hpre_set_user_domain_and_cache()`, `hpre_set_cluster()`, `hpre_config_pasid()`, and SVA prefetch open/close helpers.

Diagnostics and debugfs are handled by `hpre_debugfs_init()`, `hpre_ctrl_debug_init()`, `hpre_dfx_debug_init()`, `hpre_cap_regs_show()`, and register dump show functions. Error handling is collected in `hpre_err_ini`, with callbacks such as `hpre_hw_error_enable()`, `hpre_hw_error_disable()`, `hpre_get_err_result()`, `hpre_dev_is_abnormal()`, `hpre_disable_axi_error()`, `hpre_enable_axi_error()`, and last-DFX-register snapshot functions.

## Control Flow
Module initialization initializes the global QM list, creates the top-level `hisi_hpre` debugfs directory, and registers the PCI driver. Probe allocates `struct hpre`, initializes the embedded `hisi_qm`, rejects unsupported hardware revision 1, determines PF/VF type, configures PF queue counts and error callbacks, calls `hisi_qm_init()`, stores capability registers, sets supported algorithm strings, performs PF hardware initialization when needed, starts QM, initializes debugfs, adds the device to the global list, registers algorithms to the crypto subsystem, optionally registers UACCE, optionally enables SR-IOV VFs, and initializes PM.

PF hardware initialization configures user/domain/cache registers, enables RSA/ECC blocks depending on hardware version, initializes read channel and clusters, applies Kunpeng 920 DSM/MSI and FLR workarounds, configures PASID/SVA prefetch, and enables clock gating. Remove reverses the order: PM shutdown, wait for tasks, unregister algorithms, remove from list, disable SR-IOV, remove debugfs, stop QM, clear counters and hardware debug state, close SVA prefetch, uninitialize device error handling, and uninitialize QM.

Error handling reads HPRE interrupt status, logs named hardware error bits, marks multi-bit ECC state, disables repeated reporting for reset-required errors, clears recoverable errors, and re-enables reporting. PCI AER/reset hooks are delegated to shared QM handlers with HPRE-specific callbacks supplied by `hpre_err_ini`.

## State and Persistence Behavior
There is no disk persistence. Module parameters persist for the module lifetime: `uacce_mode`, `pf_q_num`, and `vfs_num`. Global runtime state includes `hpre_debugfs_root` and `hpre_devices`. Per-device state is in `struct hpre`/`struct hisi_qm`, including capability tables, QP counts, function type, error masks, debugfs roots, last-register snapshots, channel names, UACCE state, SR-IOV VF count, and PM state. Hardware state includes cluster enable/init registers, RAS masks, interrupt masks, SVA prefetch state, clock gate state, current debug selector registers, and read-clear counters.

## Dependencies and Integration Points
This file depends on PCI, ACPI DSM, debugfs, runtime PM, UACCE, SR-IOV, topology/NUMA for QP allocation, and the shared HiSilicon QM framework. It exposes algorithms through `hisi_qm_alg_register()` and uses `hpre_algs_register()`/`hpre_algs_unregister()` via `hpre_devices`. It uses common debugfs exports from `debugfs.c` for QM register dumps and diff register support.

## Risks and Edge Cases
Capability table indexes must stay aligned with `hpre.h` and hardware capability layouts; otherwise algorithm registration and cluster counts can be wrong. PF-only operations must not run on VFs, and the code has many PF/VF branches that need coverage. SVA prefetch open/close waits on hardware status and can time out; failed open attempts call close as recovery. Debugfs control files can write hardware selector/read-clear registers and require strict validation. Probe error unwinding crosses QM start, debugfs creation, list insertion, crypto registration, UACCE, and SR-IOV, so ordering bugs can leak registrations. The module-level algorithm registration is shared across devices; concurrency and multi-device remove ordering depend on the QM list and crypto registration reference counting in `hpre_crypto.c`.

## Test Signals
Test PF and VF probe/remove, unsupported revision rejection, capability parsing for v2/v3 hardware, PF queue module parameter validation, UACCE modes, SR-IOV enable/disable, runtime suspend/resume, AER/reset recovery, SVA prefetch timeout handling, debugfs register/control files, algorithm registration based on capability masks, and fault injection at each probe stage to validate unwind paths.
