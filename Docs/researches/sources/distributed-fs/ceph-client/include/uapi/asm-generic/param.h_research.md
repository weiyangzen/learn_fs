# sources/distributed-fs/ceph-client/include/uapi/asm-generic/param.h

Purpose: Defines generic user-visible system parameter constants.

Important APIs/types/functions: Provides `__USER_HZ` default 100, `HZ` as `__USER_HZ` unless overridden, `EXEC_PAGESIZE` 4096, `NOGROUP` -1, and `MAXHOSTNAMELEN` 64.

Control flow: Preprocessor guards allow architecture or build headers to override selected values.

State/persistence: No runtime state; constants inform user-space assumptions.

Dependencies/integration: Used by exported asm headers and libc compatibility code.

Risks: `HZ` and page-size assumptions are ABI-visible; careless overrides affect time conversion and executable loading assumptions.

Test signals: Headers compile checks and user-space validation of exported constants for architectures using generic params.
