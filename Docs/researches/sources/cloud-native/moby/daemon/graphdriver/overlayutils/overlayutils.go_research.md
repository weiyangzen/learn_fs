# sources/cloud-native/moby/daemon/graphdriver/overlayutils/overlayutils.go

Purpose: shared overlay filesystem support checks and xattr naming helpers.

Important APIs and control flow: `ErrDTypeNotSupported` creates a `NotSupportedError` with driver/backing filesystem-specific remediation text for XFS and ext filesystems. `SupportsOverlay` rejects rootless SELinux via `_DOCKERD_ROOTLESS_SELINUX`, creates temporary lower/upper/work/merged dirs, attempts an actual overlay mount with one or two lowerdirs depending on `checkMultipleLowers`, unmounts, and returns mount errors wrapped. `GetOverlayXattr` chooses `trusted.overlay.<name>` in the initial user namespace and `user.overlay.<name>` in user namespaces.

State, dependencies, and risks: state is temporary mount test directories. Dependencies include Linux overlayfs, xattr namespace rules, user namespace detection, and graphdriver unsupported errors. Risks include probe false negatives in restricted environments, cleanup warnings leaving temporary dirs, and env-based SELinux rootless detection. These helpers gate overlay2 and native diff behavior.
