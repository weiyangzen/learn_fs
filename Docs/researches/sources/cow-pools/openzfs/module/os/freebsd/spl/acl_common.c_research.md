# File Research: sources/cow-pools/openzfs/module/os/freebsd/spl/acl_common.c

Common ACL conversion code used by the FreeBSD SPL/ZFS compatibility layer. It implements sorting, allocation helpers, POSIX draft ACL to NFSv4 ACE conversion, reverse conversion where possible, and trivial ACL creation/detection.

Key areas:
- `ksort()` and `cmp2acls()` sort `aclent_t` entries.
- Userland-only `acl_alloc()`/`acl_free()` wrap ACL container allocation.
- `ln_aent_to_ace()` converts `aclent_t` entries into allow/deny ACE sequences, including ACL mask emulation and default ACL inheritance flags.
- `ln_ace_to_aent()` converts constrained NFSv4 ACE patterns back to POSIX `aclent_t`; unsupported semantic shapes return `ENOTSUP`.
- `acl_translate()` replaces an ACL in-place with the requested flavor, either ACE or ACLENT.
- `acl_trivial_access_masks()` and `acl_trivial_create()` build owner/group/everyone ACEs from mode bits.
- `ace_trivial_common()` detects non-trivial ACEs by checking principal flags, inheritance, delete bits, and privileged write bits.

The reverse conversion is deliberately strict because many NFSv4 ACLs cannot faithfully map to POSIX draft ACL semantics.
