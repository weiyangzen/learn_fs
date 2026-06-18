<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/purgatory/Makefile

## Purpose
Builds the standalone x86 kexec purgatory object and checks it for unresolved symbols.

## Important APIs, Types, And Functions
`purgatory-y` includes `purgatory.o`, stack/setup/entry assembly, `sha256.o`, and `string.o`. It builds `purgatory.ro`, `purgatory.chk`, and embeds them through `kexec-purgatory.o`.

## Control Flow
Kbuild compiles freestanding objects with flags that remove profiling, LTO, stack protector, CFI, retpoline, and other kernel instrumentation. It links a relocatable purgatory object and a non-relocatable check binary to catch unresolved symbols.

## State And Persistence
No runtime state here; it defines the embedded purgatory payload used during kexec.

## Dependencies And Integration Points
Pulls SHA-256 from `lib/crypto/sha256.c` and string routines from compressed boot code. Integrates with kexec file loading.

## Risks And Edge Cases
Purgatory cannot tolerate normal kernel instrumentation, extra sections, unresolved symbols, or unsupported relocation patterns. Build flags are security/correctness-critical for a freestanding blob.

## Test Signals
Successful `purgatory.chk` link, kexec file load, and digest verification in purgatory validate the build rules.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/purgatory/Makefile -->
