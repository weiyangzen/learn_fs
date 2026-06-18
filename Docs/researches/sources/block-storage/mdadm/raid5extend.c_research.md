# File Research: sources/block-storage/mdadm/raid5extend.c

Purpose: old RAID5 reshape helper logic for translating physical disk/chunk positions from an `n` disk layout to an `m` disk layout.

Key behavior:
- `phys2log(phys, stripe, n, layout)` maps a physical disk in a RAID5 stripe to a logical data block number, returning `-1` for parity and `-2` for unsupported layout.
- `raid5_extend(...)` reads 4 KiB blocks from old member fds, skips parity, computes the destination stripe/disk in the new geometry using `log2phys()`, seeks, and writes the block to the new fd.

Important source-shape note:
- As read, this file is not standalone buildable C: it lacks includes, return types on `raid5_extend`, declarations for variables such as `pd` and `dstripe`, and definitions for helpers like `log2phys()`, `error()`, and layout constants.
- It appears to be historical or draft code rather than a normal mdadm compilation unit.

Risks:
- No short-read/short-write retry handling.
- Fixed static `4096` byte buffer assumes block granularity and uses `chunksize / 4096`.
- No parity generation; it relocates data blocks only.
