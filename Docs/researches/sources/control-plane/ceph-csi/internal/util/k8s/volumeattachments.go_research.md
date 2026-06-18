<!-- BEGIN_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/volumeattachments.go -->
## sources/control-plane/ceph-csi/internal/util/k8s/volumeattachments.go

**Purpose:** Provides helpers to list all Kubernetes VolumeAttachments or fetch one by name.

**Important APIs and functions:** `GetVolumeAttachmentList` calls `StorageV1().VolumeAttachments().List`. `GetVolumeAttachment` calls `StorageV1().VolumeAttachments().Get`. Both wrap client and API errors.

**Control flow, state, and persistence:** Read-only Kubernetes API calls using `context.TODO`; no local caching or persistence.

**Dependencies and integration points:** Depends on Kubernetes storage/v1, metav1, and the shared client. It integrates with attach/detach reconciliation and diagnostics.

**Risks and test signals:** Listing all volume attachments can be expensive in large clusters without selectors/pagination. No caller context is available. No direct tests are present.
<!-- END_FILE_RESEARCH: sources/control-plane/ceph-csi/internal/util/k8s/volumeattachments.go -->
