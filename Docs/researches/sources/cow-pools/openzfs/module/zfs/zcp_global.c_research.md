# File Research: sources/cow-pools/openzfs/module/zfs/zcp_global.c

## Summary
Loads global errno constants into the ZCP Lua environment.

## Main Responsibilities
- Defines the errno names available to channel programs.
- Pushes each errno as a Lua global number.
- Provides the public `zcp_load_globals()` entry point.

## Key APIs
- `zcp_load_globals()`

## Important Behavior
The exported globals include common filesystem and syscall errors such as `EPERM`, `ENOENT`, `EIO`, `EACCES`, `EINVAL`, `ENOSPC`, `EROFS`, `ENOTSUP`, `EDQUOT`, and `ENAMETOOLONG`.

## Risks
The list is explicit, not generated from platform headers at runtime. Scripts can depend only on the errno names included here.
