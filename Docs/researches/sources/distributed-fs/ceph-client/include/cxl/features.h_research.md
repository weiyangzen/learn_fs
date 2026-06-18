# sources/distributed-fs/ceph-client/include/cxl/features.h

Purpose: declares kernel-known CXL feature UUIDs and device feature-state setup helpers.

Important APIs, types, and flow: UUID macros identify patrol scrub, ECS, soft/hard PPR, cacheline sparing, row sparing, bank sparing, and rank sparing features. `enum cxl_features_capability` distinguishes no feature command support, read-only support, and read-write support. `struct cxl_features_state` links to `cxl_dev_state` and holds a counted array of feature entries plus user-visible feature count. Enabled builds expose `to_cxlfs()`, `devm_cxl_setup_features()`, and `devm_cxl_setup_fwctl()`; disabled builds return NULL or `-EOPNOTSUPP`.

State and persistence: feature discovery state is devm-managed per CXL device. Feature settings may affect device firmware through other code, but this header does not persist them.

Dependencies and integration: depends on UUID support, fwctl, CXL feature UAPI, `cxl_dev_state`, mailbox capability, and memdev setup.

Risks and test signals: UUID typos, counted-array sizing, and Kconfig stubs can hide or mis-expose device controls. Signals include CXL feature discovery tests, fwctl registration, read-only/read-write capability checks, disabled-Kconfig builds, and feature UUID matching against device mailbox responses.
