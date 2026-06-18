# sources/distributed-fs/ceph-client/fs/xfs/scrub/attr_repair.h

## Purpose
This header exposes the small public interface for extended attribute repair operations that other repair modules need. It avoids publishing the large salvage context and keeps tempfile exchange details mostly private to `attr_repair.c`.

## Important APIs, types, and functions
It forward-declares `struct xrep_tempexch` and declares `xrep_xattr_swap`, `xrep_xattr_reset_fork`, and `xrep_xattr_reset_tempfile_fork`. The swap API commits a rebuilt tempfile attr fork into the target inode. The reset APIs clear attr forks from the target inode or tempfile.

## Control flow and state
There is no implementation state in this header. The functions require callers to hold the locks and transaction context documented by `attr_repair.c`; incorrect call context can corrupt fork state or violate exchange preconditions.

## Persistence and integration
These APIs are used by broader inode repair flows that need to reset or exchange attribute forks after other metadata reconstruction. They integrate with tempfile exchange and attr fork reaping code.

## Risks and test signals
Tests should focus on call-site locking and transaction requirements: resetting a target attr fork with extents, resetting a tempfile attr fork before inactivation, swapping local-local forks by copyout, swapping block-mapped forks through `xrep_tempexch_contents`, and confirming old attr blocks are left attached to the tempfile for reaping.
