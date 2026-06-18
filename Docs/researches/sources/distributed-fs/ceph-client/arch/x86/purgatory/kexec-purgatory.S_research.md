<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/kexec-purgatory.S -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/kexec-purgatory.S

## Purpose
Includes the linked purgatory binary as data in a kernel object for kexec.

## Important APIs, Types, And Functions
The assembly places purgatory blob contents in a read-only section using symbols consumed by kexec file loading.

## Control Flow
There is no runtime control flow in this wrapper; build rules generate the blob and this object embeds it.

## State And Persistence
The embedded purgatory image becomes kernel data used when preparing a kexec image.

## Dependencies And Integration Points
Depends on the `purgatory.ro` build target and kexec file loader relocation code.

## Risks And Edge Cases
Symbol naming and section placement must match loader expectations. If the blob is stale or missing, kexec file loading fails.

## Test Signals
Successful build of `kexec-purgatory.o` and kexec file load using the embedded blob validate the wrapper.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/kexec-purgatory.S -->
