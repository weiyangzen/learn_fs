# sources/control-plane/external-snapshotter/pkg/sidecar-controller/snapshot_delete_test.go

Purpose: table-driven deletion reconciliation tests for `syncContent`, focused on whether the sidecar calls CSI delete, clears status, removes finalizers, emits events, and handles secret/class failures correctly.

Important APIs/data: global fixture values for sizes, policies, times, class parameters, deletion-secret annotations, `snapshotClasses`, and `TestDeleteSync`. Each `controllerTest` entry supplies initial contents, expected contents, expected CSI create/list/delete calls, fake secrets, injected reactor errors, expected events, and a test runner.

Control flow: cases exercise dynamic and pre-provisioned contents with `Delete` and `Retain` policies, deletion errors, invalid or missing secret references, missing classes, content disappearing before delete, bound contents that should not be deleted, and group snapshot member contents whose backend snapshot is owned by a group snapshot. The test runner feeds fixtures into a fake controller/reactor and performs one reconciliation pass.

State and persistence: state is simulated through fake `VolumeSnapshotContent` objects, fake secrets, expected API content status/finalizer mutations, and mocked CSI call ledgers. Persistent API effects being asserted include cleared snapshot handles, retained restore size in some branches, finalizer removal, and event emission.

Dependencies and integration: integrates the sidecar controller test harness, snapshot CRD fixtures, core secrets, deletion annotations, CSI mock handlers, and API reactors.

Risks and test signals: this is the main guard against data-loss regressions in deletion behavior. It signals correct non-deletion for `Retain`, finalizer retention on failed deletes, group-member delete suppression, and behavior with absent secrets. Risks remain around concurrent updates and real informer retry timing, which unit tests approximate only indirectly.
