# sources/distributed-fs/lustre-release/lnet/klnds/gnilnd/gnilnd_gemini.h

## Purpose

`gnilnd_gemini.h` provides Gemini-platform defaults and small platform hooks for the gnilnd driver. It is a hardware-profile header selected by the broader driver build to define timeout, checksum, RDMA delivery, scheduler thread, and thread-safe KGNI defaults for Gemini systems.

## Important APIs, Types, And Functions

- `GNILND_BASE_TIMEOUT` is 60 seconds.
- `GNILND_CHECKSUM_DEFAULT` is 3, enabling SMSG plus BTE/RDMA checksumming by default.
- `GNILND_REVERSE_RDMA` is `GNILND_REVERSE_NONE`.
- `GNILND_RDMA_DLVR_OPTION` is `GNI_DLVMODE_PERFORMANCE`.
- `GNILND_SCHED_THREADS` is 3 when not building for `CONFIG_CRAY_COMPUTE`.
- `GNILND_KGNI_TS_MINOR_VER` is `0x44`, documenting the KGNI minor version where thread-safe support appeared.
- `GNILND_TS_ENABLE` is 0, disabling thread-safe KGNI use by default.
- `kgnilnd_register_smdd_buf(kgn_device_t *dev)` and `kgnilnd_deregister_smdd_buf(kgn_device_t *dev)` are no-op inline hooks returning `GNI_RC_SUCCESS`.

## Control Flow

The header has no runtime control flow beyond two no-op inline functions. Compile-time flow enforces that `gnilnd_hss_ops.h` must be included first and conditionally defines scheduler thread count for non-compute builds.

## State And Persistence Behavior

No mutable state or persistence exists. The macros seed module parameter defaults in `gnilnd_modparams.c` and platform behavior in the rest of the driver.

## Dependencies And Integration Points

The header depends on `gnilnd_hss_ops.h` being included first, likely so hardware service and NIC/NID translation hooks are available before platform defaults are processed. It uses GNI return constants and `kgn_device_t` from the surrounding gnilnd include context.

The defaults feed directly into module parameters such as `timeout`, `checksum`, `bte_put_dlvr_mode`, `bte_get_dlvr_mode`, `sched_threads`, `reverse_rdma`, and `thread_safe`.

## Risks And Edge Cases

- The enforced include order can break refactors that include this header directly. The preprocessor error is intentional and should be preserved unless the include hierarchy changes.
- Gemini defaults favor full checksumming and performance delivery mode. Changing them affects wire validation cost, RDMA routing behavior, and compatibility expectations.
- The SMDD registration hooks are no-ops here. Code shared with other GNI platforms must not assume these functions actually register resources on Gemini.
- `GNILND_TS_ENABLE` remains disabled even though the header documents KGNI thread-safe support. Enabling thread-safe mode should be validated against runtime KGNI version and lock assumptions.

## Test Signals

- Compile Gemini builds with and without `CONFIG_CRAY_COMPUTE` to verify scheduler-thread defaults and include ordering.
- Module-parameter tests should confirm Gemini defaults surface through `gnilnd_modparams.c`.
- Runtime smoke tests should verify no SMDD register/deregister side effects are expected on Gemini.
