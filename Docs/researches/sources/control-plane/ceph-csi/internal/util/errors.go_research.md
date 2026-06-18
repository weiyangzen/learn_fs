<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/errors.go -->
## sources/control-plane/ceph-csi/internal/util/errors.go

**Purpose:** Defines shared sentinel errors used across Ceph-CSI utilities and storage backends.

**Important APIs and types:** Package variables include `ErrKeyNotFound`, `ErrObjectExists`, `ErrObjectNotFound`, `ErrSnapNameConflict`, `ErrPoolNotFound`, `ErrClusterIDNotSet`, `ErrMissingConfigForMonitor`, and `ErrConfigNotFound`.

**Control flow, state, and persistence:** This file has no control flow or state. The errors are intended to be wrapped with `%w` so callers can use `errors.Is`.

**Dependencies and integration points:** Depends only on `errors`. These sentinels are used by RADOS object helpers, pool lookup, config lookup, snapshot conflict handling, and option validation.

**Risks and test signals:** Renaming or replacing these values breaks `errors.Is` checks. There are no direct tests here; usage tests in helpers validate wrapping behavior indirectly.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/errors.go -->
