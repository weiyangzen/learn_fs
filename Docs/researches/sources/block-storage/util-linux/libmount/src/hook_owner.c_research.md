# File Research: sources/block-storage/util-linux/libmount/src/hook_owner.c

This hook implements post-mount ownership and mode changes requested by `X-mount.owner=`, `X-mount.group=`, and `X-mount.mode=`.

Key behavior:

- `hook_prepare_options()` parses requested owner, group, and mode from userspace options.
- UID/GID/mode parsing uses libmount parsers, so names and numeric values are handled consistently with other mount options.
- If any setting is present, it registers a `MNT_STAGE_POST` hook.
- `hook_post()` runs after mount finalization work and applies `lchown()` for owner/group and `chmod()` for mode on the target.
- Failures are reported as `MNT_ERR_CHOWN` or `MNT_ERR_CHMOD`.

Dependencies and interactions:

- Runs at `MNT_STAGE_PREP_OPTIONS` for parsing and at `MNT_STAGE_POST` for filesystem mutation.
- Uses target from `cxt->fs`.

Risk notes:

- These operations happen after a successful mount; failure means the filesystem may already be mounted but requested metadata changes failed.
- `lchown()` avoids following a symlink for ownership, while `chmod()` follows normal chmod behavior.
