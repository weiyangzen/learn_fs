<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-util.h -->
# sources/distributed-fs/orangefs/src/common/security/security-util.h

## Purpose
Declares shared security utility functions and the unsigned-credential test macro.

## Important APIs, Types, And Functions
Defines `IS_UNSIGNED_CRED(cred)` as `sig_size == 0` and declares capability formatting/null/copy/debug/cleanup helpers, credential copy/debug/cleanup helpers, and Windows path substitution.

## Control Flow
Security code uses these declarations for object lifetime management around signing, verification, caching, and debug logging.

## State And Persistence
No state is declared. The functions operate on caller-owned PVFS security structures.

## Dependencies And Integration Points
Relies on PVFS security types being visible before inclusion. It is included broadly by security modules and client capability caching.

## Risks And Test Signals
Risks are implicit include-order requirements for `uint32_t`, `PVFS_*` types, and Windows-only declarations. Compile coverage in all security feature modes is the primary signal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/orangefs/src/common/security/security-util.h -->
