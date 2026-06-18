# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/sec2/sec_main.c

## Purpose
This file is the PCI and device-management layer for the HiSilicon SEC accelerator. It initializes the QM instance, capabilities, memory, user-domain/SMMU settings, clock gating, RAS/error recovery, debugfs, SR-IOV, runtime PM, and Crypto API registration for PF/VF SEC devices.

## Important APIs, Types, And Functions
Exported helpers include `sec_create_qps()`, `sec_destroy_qps()`, `sec_get_alg_bitmap()`, and `hisi_sec_get_pf_driver()`. Module parameters are `pf_q_num`, `ctx_q_num`, `vfs_num`, and `uacce_mode`; setters validate PF queue count, even context queue count, SR-IOV count, and UACCE mode.

Device initialization is centered on `sec_probe()`, `sec_qm_init()`, `sec_probe_init()`, `sec_pf_probe_init()`, and `sec_set_user_domain_and_cache()`. Hardware bring-up is in `sec_engine_init()`, which disables clock gating before memory init, waits for SEC memory initialization, enables TRNG, configures SVA/prefetch, opens SEC cores from capability bitmaps, enables v2 descriptor checks, sets endian, and re-enables clock gating on newer hardware.

RAS and reset integration are implemented through `sec_err_ini`, with callbacks such as `sec_hw_error_enable()`, `sec_hw_error_disable()`, `sec_get_err_result()`, `sec_dev_is_abnormal()`, `sec_disable_axi_error()`, and `sec_enable_axi_error()`. Debugfs support is created by `sec_debugfs_init()`, `sec_core_debug_init()`, and the `clear_enable`, DFX counter, register dump, diff-reg, and capability-reg files.

## Control Flow
Module init initializes the QM device list, creates the root debugfs directory, and registers a PCI driver. Probe allocates `struct sec_dev`, initializes QM fields based on PF/VF identity, stores capability registers, maps algorithm names, checks whether an IOMMU paging domain is active, performs PF-only hardware init, starts QM, initializes debugfs, adds the device to the QM list, registers algorithms through `sec_crypto.c`, optionally registers UACCE, optionally enables SR-IOV VFs, and initializes PM.

Remove reverses that sequence: PM uninit, wait for tasks, unregister algorithms, remove from list, disable SR-IOV, remove debugfs, stop QM, undo PF resources, and uninit QM. PCI error handlers delegate reset and recovery to common HiSilicon QM handlers with SEC-specific `sec_err_ini` callbacks.

## State And Persistence
Persistent runtime state is device memory only: `struct sec_dev`, embedded `struct hisi_qm`, cached capability tables, debug counters, last DFX register snapshots, `ctx_q_num`, `iommu_used`, and debugfs files. Hardware state includes SEC memory init, SAA/core enable bits, endian mode, SVA prefetch mode, RAS masks, and OOO shutdown settings. No on-disk persistence exists.

## Dependencies And Integration Points
This file depends on PCI, debugfs, IOMMU, PM runtime, UACCE, SR-IOV, and the HiSilicon QM common layer. It integrates with `sec_crypto.c` through `sec_devices.register_to_crypto` and queue allocation. It shares capability and error semantics with other HiSilicon accelerator drivers.

## Risks
Risks include incorrect capability defaults across hardware versions, queue-count module parameters that overcommit hardware, SVA prefetch close/open timeout behavior, RAS masking that suppresses recoverable errors, and cleanup ordering around algorithm unregister versus in-flight queue tasks. PF/VF v1 special casing is fragile because VF queue layout is hard-coded.

## Test Signals
Probe/remove smoke tests should cover PF and VF IDs, v1/v2/v3 capability variants, module parameters, UACCE on/off, SR-IOV enable/disable, runtime suspend/resume, and PCI error injection. Debugfs `cap_regs`, `diff_regs`, and DFX counters should appear for PFs and be cleaned on remove. Crypto API algorithms should register only after QM start and vanish after device removal.
