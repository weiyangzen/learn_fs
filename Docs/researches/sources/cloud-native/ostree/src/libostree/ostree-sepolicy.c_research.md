# sources/cloud-native/ostree/src/libostree/ostree-sepolicy.c

Purpose: implements `OstreeSePolicy`, a GObject/GInitable that loads SELinux policy from a root filesystem or commit checkout, then provides label lookup, restorecon, fscreatecon, checksum/name reporting, logging suppression, and SELinux xattr filtering.

Important APIs/types/functions: `struct OstreeSePolicy` stores a rootfs fd/path, optional tempdir, and under `HAVE_SELINUX` the policy root, `selabel_handle`, policy name, and checksum. `get_policy_checksum` finds the newest binary policy and returns SHA256. Constructors cover root path, root fd, and commit extraction. `initable_init` parses `etc/selinux/config` or `usr/etc/selinux/config`, sets libselinux policy root, opens the file-label database, validates lookup for `/`, and records metadata. Public APIs include `get_path`, `get_name`, `get_csum`, `get_label`, `restorecon`, `setfscreatecon`, and cleanup.

Control flow: construction stores either a canonical `GFile` or root directory fd and runs `GInitable.init`. With SELinux compiled in, initialization primes host SELinux cache, resolves root, locates config, reads `SELINUX=` and `SELINUXTYPE=`, and only opens policy if target config is enforcing or permissive. Policy checkout from a commit extracts `usr/etc/selinux` into a temp dir and constructs a fd-based policy. Label lookup is a no-op success when no handle exists, special-cases `/proc` as `/mnt`, calls `selabel_lookup_raw`, returns `NULL` for `ENOENT`, and propagates other errors. `restorecon` obtains mode, optionally preserves existing labels, computes the policy label, honors `ALLOW_NOLABEL`, and calls `lsetfilecon`.

State/persistence: the object holds policy handles and metadata until finalize. `restorecon` persists labels on filesystem objects. `setfscreatecon` mutates process SELinux create-label state until cleanup. `new_from_commit` owns temporary extracted policy state.

Dependencies/integration: conditionally depends on libselinux plus GLib/GIO, libglnx, OSTree repo checkout/read APIs, and checksum utilities. Integrated by `OstreeRepoCommitModifier`, checkout paths, archive import, sysroot/deployment labeling, and SELinux-enabled tests.

Risks: libselinux policy root and fscreatecon are process-global, so concurrent policy use and cleanup order deserve care. Fd-relative roots are only partially represented as paths. Target SELinux enabled with host SELinux disabled silently skips `setfscreatecon`, which can produce unlabeled files until later relabeling. `restorecon` can fail deployments if `ALLOW_NOLABEL` is not set. Non-SELinux builds return success/null for most operations.

Test signals: `tests/test-libarchive-import.c` covers archive import with SELinux policy and label checks. `basic-test.sh` has SELinux-relabeled sections and skips when unavailable. Installed/nondestructive tests exercise host-policy commit paths.
