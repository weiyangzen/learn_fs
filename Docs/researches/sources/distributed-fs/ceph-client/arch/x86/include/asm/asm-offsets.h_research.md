
# sources/distributed-fs/ceph-client/arch/x86/include/asm/asm-offsets.h

Purpose: architecture include shim that exposes generated C-structure offsets to assembly.

Important APIs and control flow: the file directly includes `<generated/asm-offsets.h>`. There are no local declarations or branches; build tooling generates the target header from offset extraction code before assembly files consume it.

State, dependencies, and risks: state is build-generated, not runtime. Dependencies are the kernel build order and generated header path. Risks are stale or missing generated offsets causing assembly/C ABI mismatches, especially for entry code and low-level context structures. Test signals are compile failures, objtool validation, and boot-time failures in code using generated offsets.
