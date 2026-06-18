# sources/distributed-fs/ceph-client/drivers/infiniband/hw/bng_re/bng_sp.h

Purpose: declares the BNG RoCE slow-path device-attribute data model and the query entry point used to populate it. It is the public header for `bng_sp.c`.

Important APIs and types: `struct bng_re_dev_attr` stores firmware version, GID count, QP/CQ/MR/MW/PD/AH/SRQ limits, max inline data, TQM allocation requests, atomic capability, firmware capability flags, and maximum DPI count. Constants include `FW_VER_ARR_LEN`, `BNG_RE_NUM_GIDS_SUPPORTED`, `BNG_RE_MAX_OUT_RD_ATOM`, `BNG_VAR_MAX_WQE`, and `BNG_VAR_MAX_SGE`. `bng_re_get_dev_attr(struct bng_re_rcfw *rcfw)` is the exported query function.

Control flow and integration: the header has no executable control flow, but it defines the shape that firmware query results are normalized into. Resource initialization and verbs/device-query code are expected to read this struct after `bng_re_get_dev_attr()` succeeds.

State and persistence: `struct bng_re_dev_attr` is an in-memory cache of hardware and firmware limits. It is not self-synchronized, reference-counted, or persisted; lifecycle is owned by the enclosing resource object.

Dependencies: includes `bng_fw.h` for firmware constants such as `BNG_MAX_TQM_ALLOC_REQ`. It relies on Linux integer and bool types being available through included driver headers.

Risks: because this header centralizes advertised limits, any mismatch with firmware response decoding can cascade into bad queue sizes, invalid MR limits, or unsupported capability exposure. The `max_mrw` field is declared but not populated in the associated implementation in this subset.

Test signals: compile checks for all consumers of the struct, device-query tests that compare populated attributes with firmware limits, and ABI/feature tests around max GID, max SRQ, atomic enablement, variable WQE, and max DPI behavior.
