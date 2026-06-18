# File Research: sources/block-storage/util-linux/libmount/src/hook_mkdir.c

This hook implements `X-mount.mkdir` and `x-mount.mkdir`, creating missing target directories before mounting.

Key behavior:

- `is_mkdir_required()` searches userspace options for `X-mount.mkdir` or lowercase `x-mount.mkdir`.
- If the target already exists, no action is taken.
- The option value, when provided, is parsed as an octal mode, allowing optional leading/trailing quotes.
- Default mode is `0755`.
- `hook_prepare_target()` creates the target with `ul_mkdir_p()` only for unrestricted contexts. Restricted contexts get `-EPERM`.
- After successful creation, if a path cache exists and canonicalizes the target differently, the filesystem target is updated.

Dependencies and interactions:

- Runs at `MNT_STAGE_PREP_TARGET`.
- SELinux handling can insert a dependent target hook after this hook for `rootcontext=@target`.

Risk notes:

- Mode parsing accepts octal text only; malformed values produce `MNT_ERR_MOUNTOPT`.
- Directory creation is deliberately unavailable for suid/restricted mount operations.
