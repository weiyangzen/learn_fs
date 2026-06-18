<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/v1_test.go -->
## sources/control-plane/ceph-csi/internal/util/reftracker/v1/v1_test.go

Purpose: verifies v1 layout behavior at the object-shape level using fake RADOS.

Coverage: `TestV1Read` exercises successful add through read path, missing object failure, stale generation failure, refcount overflow, and error identity for stale generation. `TestV1Init` confirms exclusive create success and existing-object failure. `TestV1Add` checks adding a new ref increments object version/refcount/omap, existing ref no-ops without version bump, masked refs block re-add, and failure cases. `TestV1Remove` checks removal without deletion, deletion on last normal ref, masking without deletion, masking with deletion, adding a mask for a missing ref, no-op unknown normal removal, and stale generation error identity.

State assertions: tests compare entire `FakeObj` values, including `Ver`, `Omap`, and `Data`, which strongly protects layout and fake-version behavior.

Dependencies: fake RADOS, `reftype`, reftracker errors, and `testify/require`.

Risks and gaps: does not simulate true concurrent interleavings beyond stale generation. Duplicate remove fixture comments/cases are present. No explicit corrupt omap reftype test in v1 read path.

Test signal quality: strong for current v1 persistence contract and idempotent semantics.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/reftracker/v1/v1_test.go -->
