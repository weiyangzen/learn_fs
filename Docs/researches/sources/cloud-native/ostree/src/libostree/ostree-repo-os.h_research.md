# sources/cloud-native/ostree/src/libostree/ostree-repo-os.h

Purpose: declares metadata keys and the helper API for marking OSTree commits as bootable OS commits.

Important APIs/types/functions: defines `OSTREE_METADATA_KEY_BOOTABLE` (`ostree.bootable`, type `b`), `OSTREE_METADATA_KEY_LINUX` (`ostree.linux`, type `s`), and `ostree_commit_metadata_for_bootable`.

Control flow: callers provide a root `GFile` and mutable `GVariantDict`; the implementation inspects the filesystem and inserts the two keys when a kernel is found.

State and persistence: the header defines metadata contract only. Persistence occurs when the caller writes the updated dictionary into commit metadata.

Dependencies/integration: includes GIO, `ostree-types.h`, and `sys/stat.h`. The constants are public API since 2021.1 and should remain stable for consumers inspecting bootable commit metadata.

Risks: changing key names or variant types would break consumers. The API returns errors rather than silently omitting metadata, so callers must decide whether bootable metadata is mandatory.

Test signals: direct tests should assert both keys and types; current coverage is not obvious from nearby test search.
