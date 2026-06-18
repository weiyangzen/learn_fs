# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_aries.h

## Purpose

`gnilnd_aries.h` supplies Aries-specific compile-time defaults and the shared-MDD hold buffer helpers required by the generic gnilnd code. It is included only after `gnilnd_hss_ops.h` and `gnilnd_api_wrap.h` through `gnilnd.h` when `CONFIG_CRAY_ARIES` is selected.

## Important APIs And Definitions

- Aries timeout defaults: imports `aries/aries_timeouts_gpl.h` on Cray XT builds, otherwise defines `TIMEOUT_SECS()` and a generic `TO_GNILND_timeout` fallback.
- Hardware policy constants: `GNILND_BASE_TIMEOUT`, `GNILND_CHECKSUM_DEFAULT`, `GNILND_REVERSE_RDMA`, `GNILND_RDMA_DLVR_OPTION`, service-node `GNILND_SCHED_THREADS`, `GNILND_KGNI_TS_MINOR_VER`, and `GNILND_TS_ENABLE`.
- `kgnilnd_register_smdd_buf(kgn_device_t *dev)`: allocates one page, selects `GNI_MEM_READWRITE` plus optional `GNI_MEM_RELAXED_PI_ORDERING`, and registers it with GNI into `dev->gnd_smdd_hold_hndl`.
- `kgnilnd_deregister_smdd_buf(kgn_device_t *dev)`: deregisters the shared-MDD hold memory and frees the page.

## Control Flow

At compile time, the header chooses Aries timeout and reverse-RDMA defaults based on build configuration. At device initialization, `kgnilnd_dev_init()` calls `kgnilnd_register_smdd_buf()` after creating CQs; the helper allocates `dev->gnd_smdd_hold_buf` and calls `kgnilnd_mem_register()`. At device finalization, `kgnilnd_dev_fini()` calls `kgnilnd_deregister_smdd_buf()` when the buffer pointer is set, then clears the pointer after a successful return assertion.

## State And Persistence Behavior

This header adds no global state. It mutates per-device in-memory fields `gnd_smdd_hold_buf` and `gnd_smdd_hold_hndl`. The registered page is a runtime resource used to keep a shared MDD allocated for Aries behavior; it is not persisted across module unload or device reinitialization.

## Dependencies And Integration Points

The file depends on LNet headers, `gnilnd_hss_ops.h` include ordering, Aries timeout headers when available, GNI memory flags, `kgnilnd_tunables.kgn_bte_relaxed_ordering`, and the memory wrappers from `gnilnd_api_wrap.h`. Its constants are consumed by generic gnilnd timeout, scheduler, reverse-RDMA, checksum, and thread-safe KGNI-version logic.

## Risks And Edge Cases

- Include order is enforced with `#error`; direct inclusion without `gnilnd_hss_ops.h` breaks the build.
- Generic-kernel builds rely on the fallback `TO_GNILND_timeout` value, so timeout behavior can differ from Cray XT-provided headers.
- `kgnilnd_register_smdd_buf()` returns a memory-registration error without freeing the allocated page immediately. Current cleanup may recover through device finalization if the pointer remains set, but this is a resource-management hotspot.
- `kgnilnd_deregister_smdd_buf()` frees the page regardless of the deregistration return code. Callers assert success in normal finalization, but error paths should be reviewed carefully.
- Reverse-RDMA defaults differ between compute and service builds, so behavior-sensitive tests need both configurations.

## Test Signals

Build coverage should include Aries compute, Aries service, Cray XT timeout-header, and generic-kernel fallback configurations. Runtime signals include successful shared-MDD buffer allocation/registration during `kgnilnd_dev_init()`, successful deregistration/free during `kgnilnd_dev_fini()`, relaxed-ordering flag propagation when the tunable is set, and correct thread-safe KGNI gating at minor version `0x45`.
