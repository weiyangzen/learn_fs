# sources/distributed-fs/ceph-client/drivers/infiniband/hw/mthca/mthca_profile.h

Purpose: declares the mthca HCA resource profile request structure and the profile-building entry point.

Important APIs/types/functions: `struct mthca_profile` carries requested counts for QPs, RDBs per QP, SRQs, CQs, multicast groups, MPTs, MTTs, UD address vectors, UARs, UARC size, and reserved FMR MTTs. `mthca_make_profile` maps this request and firmware limits into `struct mthca_init_hca_param`.

Control flow: this header has no executable control flow beyond exposing the single builder prototype; implementation is in `mthca_profile.c`.

State and persistence: profile values are transient bring-up inputs, later copied into `dev->limits`, `dev` table bases, and INIT_HCA parameters. They are not persisted outside the device initialization path.

Dependencies and integration: includes `mthca_dev.h` and `mthca_cmd.h` because the builder needs device state, firmware device limits, and INIT_HCA command structures. Consumers are the main mthca initialization/profile selection code.

Risks: all fields are plain `int`, so callers must bound values before/while building the profile. The ABI between profile fields and firmware resource sizing is implicit and must stay aligned with `mthca_make_profile`.

Test signals: compile coverage, successful driver probe with default and tuned profile values, and failure-path tests for oversized requested resources.
