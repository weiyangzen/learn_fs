# sources/distributed-fs/ceph-client/drivers/crypto/hisilicon/zip/zip_main.c

## Purpose
This file is the PCI/QM lifecycle, capability, debugfs, RAS, UACCE, SR-IOV, and PM layer for the HiSilicon ZIP accelerator. It initializes compression/decompression hardware cores, exposes capabilities to QM/UACCE, registers Crypto API algorithms through `zip_crypto.c`, and incorporates DAE support from `dae_main.c`.

## Important APIs, Types, And Functions
Public functions are `zip_create_qps()`, `hisi_zip_alg_support()`, and `hisi_zip_get_pf_driver()`. Module parameters include `perf_mode`, `uacce_mode`, `pf_q_num`, and `vfs_num`. Major lifecycle functions are `hisi_zip_probe()`, `hisi_zip_qm_init()`, `hisi_zip_probe_init()`, `hisi_zip_pf_probe_init()`, `hisi_zip_set_user_domain_and_cache()`, and `hisi_zip_remove()`.

Capabilities are described by `zip_basic_cap_info[]` and `zip_cap_query_info[]`; algorithm strings are mapped by `zip_dev_algs[]`. Error handling is supplied through `hisi_zip_err_ini`, including ZIP and DAE error enable/disable, abnormality checks, reset decisions, SVA prefetch open/close, AXI error gating, and last DFX register dumps. Debugfs setup creates control files, per-core register directories, DFX counters, diff-reg dumps, and capability dumps.

## Control Flow
Module init initializes the ZIP QM list, creates a root debugfs directory, and registers a PCI driver. Probe allocates `struct hisi_zip`, initializes QM identity and PF/VF queue fields, caches capability tables, sets supported algorithm strings, appends DAE algorithms when supported, performs PF-only user-domain/cache/core/SVA/DAE init, starts QM, initializes debugfs, adds the device to the QM list, registers Crypto API algorithms with two queue contexts, optionally registers UACCE, optionally enables SR-IOV, and initializes PM.

Hardware setup configures QM user/cache attributes, ZIP port cache/user attributes, optional SVA SSV user bits, prefetch, core enable bitmaps, SQ/CQ writeback, compression performance mode, literal-length behavior, clock gating, and DAE memory. Remove reverses registration and hardware state.

## State And Persistence
State is per-device and in memory: embedded `struct hisi_qm`, PF control object, DFX counters, capability records, debugfs entries, last register snapshots, and module parameter values. Hardware state includes ZIP core enables, cache/user-domain registers, SVA prefetch, RAS masks, OOO shutdown, clock gating, and DAE registers. No durable persistence exists.

## Dependencies And Integration Points
The file depends on PCI, debugfs, PM runtime, UACCE, HiSilicon QM common code, SR-IOV helpers, and DAE/ZIP crypto module-local APIs. It is the integration hub for `zip_crypto.c`, `zip.h`, and `dae_main.c`.

## Risks
Hardware-version capability handling is the main risk. Core counts drive debugfs register bases and last-register snapshot sizing, so bad capability values can misaddress MMIO. ZIP RAS mask registers use inverted interrupt-mask semantics in some paths, which is error-prone. DAE reset results can force ZIP recovery. Initialization logs debugfs failure but continues, so observability may be absent on otherwise working devices.

## Test Signals
Test PF/VF probe/remove, v1 VF queue special casing, v2 SVA user-domain settings, v3+ clock gating and shaper rates, `perf_mode` validation, UACCE on/off, SR-IOV, DAE-supported and DAE-absent hardware, debugfs per-core layout, PCI error injection, runtime PM, and Crypto API algorithm presence filtered by capability bitmap.
