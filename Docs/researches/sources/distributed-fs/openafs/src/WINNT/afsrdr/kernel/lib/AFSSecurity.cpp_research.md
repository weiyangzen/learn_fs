# sources/distributed-fs/openafs/src/WINNT/afsrdr/kernel/lib/AFSSecurity.cpp

## Purpose
`AFSSecurity.cpp` handles security query/set dispatch. Set-security is a no-op success stub. Query-security returns the redirector's global default security descriptor, rejecting SACL requests and copying `AFSDefaultSD` into the caller's buffer.

## Important APIs, Types, And Functions
The exported handlers are `AFSSetSecurity` and `AFSQuerySecurity`. `AFSQuerySecurity` reads `SecurityInformation`, decodes `FILE_OBJECT`, `AFSFcb`, and `AFSCcb`, validates the FCB, rejects `SACL_SECURITY_INFORMATION`, checks `AFSDefaultSD`, computes descriptor length with `RtlLengthSecurityDescriptor`, reports required size on overflow, locks the user buffer with `AFSLockUserBuffer`, copies the descriptor, unlocks/frees the MDL, completes the IRP, and returns.

## Control Flow
Query flow is linear: validate FCB, reject SACL, validate descriptor, validate output length, lock buffer, copy, set `IoStatus.Information`, cleanup MDL, complete. The CCB is decoded but not used. Requested owner/group/DACL bits do not tailor the copied descriptor; the whole default descriptor is returned.

## State And Persistence Behavior
The only security state used here is the process-global `AFSDefaultSD`, initialized elsewhere. No per-file ACLs, owners, or groups are read or persisted. `AFSSetSecurity` does not relay changes to AFS or store them locally.

## Dependencies And Integration Points
The file depends on Windows security descriptors, MDLs, `AFSDefaultSD`, `AFSLockUserBuffer`, tracing, exception filtering, and completion helpers. AFS authorization semantics are enforced elsewhere through AFS credentials/access checks rather than NTFS-like security descriptors here.

## Risks And Edge Cases
All objects expose the same descriptor, so user-mode security tools do not see AFS ACL semantics. Set-security silently succeeds with no effect. SACL denial is unconditional, including combined SACL/DACL requests.

## Test Signals
Test descriptor queries for owner/group/DACL masks, SACL denial, too-small buffers and required length, null user buffers, missing `AFSDefaultSD`, invalid FCBs, MDL cleanup, and set-security no-effect behavior.
