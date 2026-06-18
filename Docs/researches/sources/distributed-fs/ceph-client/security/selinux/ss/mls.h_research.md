<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls.h -->
# sources/distributed-fs/ceph-client/security/selinux/ss/mls.h

## Purpose
Declares the MLS operation surface for SELinux security-server code. It connects contexts, policydb, SID table, transition computation, and NetLabel category/level conversion.

## Important APIs, Types, and Functions
Declarations cover context length/rendering, context/range/level validation, string-to-context parsing, range assignment, policy conversion, transition SID MLS computation, user range setup, and optional NetLabel import/export. Inline `mls_range_hash()` hashes low/high sensitivities and category ebitmaps.

## Control Flow
Consumers call validation during context lookup/load, rendering during SID-to-context conversion, parsing during context-to-SID conversion, compute during transition/member/change SID calculation, and conversion during policy reload. NetLabel callers use the optional helpers when translating packet labels.

## State and Persistence
The header owns no state, but all functions operate on policy-owned MLS definitions and context-owned ranges. The hash function contributes to persistent SID/context table lookup behavior.

## Dependencies and Integration Points
Depends on jhash, context, ebitmap, policydb, and optional NetLabel declarations. Integrated by services, SID table, NetLabel glue, and policy conversion.

## Risks
Callers must honor allocation and locking requirements, especially policy read locks for default SID lookup during parsing. Hash changes can affect table distribution. Disabled NetLabel stubs return `-ENOMEM` for category conversion, so callers must treat them as unavailable.

## Test Signals
Compile with and without NetLabel, validate MLS enabled/disabled paths, hash equal ranges consistently, and cover callers in context conversion, transition computation, and policy reload.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/security/selinux/ss/mls.h -->
