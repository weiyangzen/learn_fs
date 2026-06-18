# File Research: sources/cow-pools/nilfs-utils/sbin/mount/mount.nilfs2.h

## Scope

Defines shared constants for NILFS mount helpers.

## API Surface

- `NILFS2_FS_NAME` is `"nilfs2"`.
- `PPOPT_NAME` is `"pp"` for cleaner protection period mount attribute.
- `NOGCOPT_NAME` is `"nogc"` for suppressing cleaner daemon startup.

## Dependencies And Risks

The constants are shared between legacy and libmount helpers and must stay synchronized with cleaner-control option parsing.
