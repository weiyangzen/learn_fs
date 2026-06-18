# sources/cloud-native/ostree/src/libostree/ostree-sepolicy.h

Purpose: public header for `OstreeSePolicy`, exposing SELinux policy construction and file-label APIs used by repository commit/checkout code and external libostree consumers.

Important APIs/types/functions: type macros and `ostree_sepolicy_get_type` define the GObject. Constructors are `ostree_sepolicy_new`, `ostree_sepolicy_new_at`, and `ostree_sepolicy_new_from_commit`. Accessors expose root path, policy name, policy checksum, and label lookup. `OstreeSePolicyRestoreconFlags` provides `ALLOW_NOLABEL` and `KEEP_EXISTING`. `restorecon`, `setfscreatecon`, and cleanup provide labeling operations. `ostree_sepolicy_set_null_log` disables libselinux logging.

Control flow: callers construct a policy, query label/name/checksum, pass it to commit modifiers or checkout options, or call restore/create-context APIs directly. The cleanup macro enables C scope-based reset of fscreatecon.

State/persistence: objects own policy handles and optional temp extraction state. `restorecon` persists file xattrs; `setfscreatecon` alters process-global creation context until cleanup.

Dependencies/integration: depends on `ostree-types.h`, GLib/GIO types, and optional libselinux support in the implementation. `ostree-repo.h` includes this header for commit modifier and checkout option APIs.

Risks: `ostree_sepolicy_get_path` is deprecated in practice because fd-based policies may not have a global path. Callers must not assume non-NULL policy name/checksum. Cleanup use is critical after `setfscreatecon`.

Test signals: integration and libarchive tests cover construction and commit labeling under SELinux-capable environments. Header API shape is indirectly covered by C and Rust binding compilation.
