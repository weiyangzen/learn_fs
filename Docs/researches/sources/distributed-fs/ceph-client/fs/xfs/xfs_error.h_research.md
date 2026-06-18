# sources/distributed-fs/ceph-client/fs/xfs/xfs_error.h

Purpose: Declares XFS error/corruption reporting APIs, debug errortag hooks, error-level constants, corruption dump length, and panic tag bitmasks/string mappings.

Important APIs, types, and functions: Declares generic, corruption, buffer verifier, and inode verifier reporting functions. Defines `XFS_ERROR_REPORT()`, `XFS_CORRUPTION_ERROR()`, error levels, `XFS_CORRUPTION_DUMP_LEN`, DEBUG errortag APIs/stubs, `XFS_TEST_ERROR()`, `XFS_ERRORTAG_DELAY()`, panic tags, `XFS_PTAG_MASK`, and `XFS_PTAG_STRINGS`.

Control flow: Macros capture source file, line, and return address; DEBUG stubs compile injection out when disabled.

State and persistence: No state is stored here.

Dependencies and integration points: Included by verifiers, metadata code, sysfs, and sysctl plumbing.

Risks and test signals: Risks are panic tag ABI drift, macro misuse with wrong buffer sizes, and disabled DEBUG callers expecting injection. Test panic tag mappings and DEBUG/non-DEBUG builds.
