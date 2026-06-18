<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftracker.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/reftracker.go

Purpose: public key-based reference tracker API. It tracks unique reference keys, preserving idempotent increments/decrements in a persistent RADOS object and supporting concurrent writers through object-version assertions.

APIs: `Add(ioctx, rtName, refs)` creates or updates a tracker and returns whether a new object was created. `Remove(ioctx, rtName, refs)` removes or masks references and returns whether the tracker object was deleted. Internal validators reject empty tracker names and empty/nil refs.

Control flow: both operations read the reftracker object version from xattr. `Add` initializes v1 state if the object is missing; otherwise it reads the last RADOS generation and dispatches to `v1.Add`. `Remove` treats a missing object as already deleted; otherwise it dispatches to `v1.Remove`. Unknown layout versions fail through `errors.UnknownObjectVersion`.

State and persistence: persistent state is in a RADOS object named `rtName`: a version xattr plus v1 body/omap layout. `GetLastVersion` immediately after version xattr read provides the generation used by subsequent v1 read/write assertions.

Dependencies and integration: uses `radoswrapper`, version dispatch, v1 implementation, `reftype`, and go-ceph `rados.ErrNotFound`.

Risks: callers must retry on `ErrObjectOutOfDate`; this package surfaces but does not loop. Version-read and last-version assumptions are central to concurrency safety. Empty refs are errors, not no-ops.

Test signals: `reftracker_test.go` covers input validation, new object creation, overlapping idempotent adds, missing-object remove semantics, bulk/single deletes, repeated add/remove cycles, and mask behavior.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/reftracker.go -->
