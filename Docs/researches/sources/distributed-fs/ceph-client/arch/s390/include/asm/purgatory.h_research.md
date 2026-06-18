# sources/distributed-fs/ceph-client/arch/s390/include/asm/purgatory.h

Purpose: This header declares the s390 kexec purgatory digest verification entry point.

Important APIs/types/functions: `verify_sha256_digest()` is declared when not assembling, alongside generic purgatory definitions.

Control flow: Kexec purgatory code calls the verifier before transferring control to the loaded kernel image.

State and persistence: State is the purgatory image and digest data provided by kexec; the header stores none.

Dependencies and integration points: It depends on Linux purgatory infrastructure and integrates with `kexec.h` loader and relocation code.

Risks and test signals: Digest verification failure must stop booting the new kernel. Tests should include kexec_file loads, tampered image/digest failure, purgatory relocation, and crash-kernel boot.
