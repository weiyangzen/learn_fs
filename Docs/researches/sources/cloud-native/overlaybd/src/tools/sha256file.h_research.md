# sources/cloud-native/overlaybd/src/tools/sha256file.h

Purpose: declares the checksum wrapper abstraction for Photon read-only files.

Important APIs/types/functions: abstract class `SHA256File : VirtualReadOnlyFile` adds pure virtual `sha256_checksum()`. Factory `new_sha256_file(IFile*, bool ownership)` wraps a Photon file; `sha256sum(const char*)` hashes a filesystem path.

Control flow: consumers read through `SHA256File` as an `IFile`, then call `sha256_checksum` to obtain the final `sha256:<hex>` string.

State and persistence: header defines no concrete state; implementations own digest state and optionally own the wrapped file.

Dependencies/integration: included by apply/merge-related tools that need layer checksum handling; depends on Photon filesystem interfaces.

Risks: the digest contract implies sequential reads; random seeks or multiple consumers can produce unintuitive digests. Ownership semantics must be passed correctly.

Test signals: compile and runtime coverage through `overlaybd-apply --checksum` plus unit tests around factory ownership.
