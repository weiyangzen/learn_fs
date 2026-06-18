<!-- BEGIN_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/user/opmask/opmask.go -->
# sources/control-plane/rook/tests/integration/object/user/opmask/opmask.go

Purpose: integration coverage for `CephObjectStoreUser.spec.opMask` reconciliation. It verifies the default RGW operation mask, an explicit read-only mask, nil reset to default, and an explicitly empty mask.

Important APIs and control flow: `TestObjectStoreUserOpMask` creates a namespace and user, waits for `ConditionReady`, initializes a go-ceph admin client, verifies initial `OpMask` is `read, write, delete`, updates `Spec.OpMask` to a one-element slice containing `read`, removes it by setting nil, and then sets an empty slice to remove all operations. Each state is checked by polling `adminClient.GetUser`.

State, persistence, and integration: state lives in the user CR spec and RGW user metadata. It depends on Rook reconciliation and go-ceph admin access. Risks include string-format sensitivity in RGW's `OpMask` display (`<none>` versus empty) and the skipped TLS path. Test signals include exact admin API values for default, restricted, restored, and empty masks plus deletion and namespace cleanup.
<!-- END_FILE_RESEARCH: sources/control-plane/rook/tests/integration/object/user/opmask/opmask.go -->
