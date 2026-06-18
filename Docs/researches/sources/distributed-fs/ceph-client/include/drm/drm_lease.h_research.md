# sources/distributed-fs/ceph-client/include/drm/drm_lease.h

Purpose: declares the DRM KMS leasing interface that lets a DRM master delegate selected mode objects to a lessee file descriptor while retaining ownership hierarchy and revocation support.

Important APIs and types: `drm_lease_owner()` finds the owner master for a lessee, `drm_lease_destroy()` releases lease state for a lessee master, `drm_lease_held()` and `_drm_lease_held()` test access to a KMS object id, `drm_lease_revoke()` revokes a master's leases, and `drm_lease_filter_crtcs()` masks CRTC bits through lease visibility. UAPI ioctl handlers are declared for create lease, list lessees, get current lease objects, and revoke lease.

Control flow: a master creates a lease through `drm_mode_create_lease_ioctl()`, passing a set of object IDs. Later KMS object lookup and ioctl paths use lease checks to restrict object visibility. Lessees can be listed, queried, and revoked through the other ioctl handlers; destruction runs when a lessee master is torn down.

State and persistence behavior: lease state is tied to `struct drm_master` and `struct drm_file` lifetimes, not persistent storage. Revocation changes in-kernel master/lease relationships and immediately affects object access.

Dependencies and integration points: integrates with DRM master handling, mode object lookup, CRTC masks, KMS ioctls, and access control in mode-setting paths.

Risks: lease filtering must be applied consistently or lessees can access objects outside their lease. Revocation must handle active lessee file descriptors without use-after-free. CRTC bit filtering can silently affect legacy APIs that use bitmasks instead of object IDs.

Test signals: create/list/get/revoke lease ioctls, lessee object lookup denial, CRTC mask filtering, lease owner traversal, master destruction with active leases, and revocation during modeset attempts.
