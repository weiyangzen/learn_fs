# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/bti/assembler.h

Purpose: assembly macro support for the BTI freestanding tests.

Important APIs/types/functions: GNU property constants; `startfn`/`endfn` function macros; `emit_aarch64_feature_1_and` emits `.note.gnu.property` with BTI/PAC bits when `BTI` is true; hint macros for `paciasp`, `autiasp`, `bti` variants.

Control flow: macros expand at assembly time only.

State and persistence: emits ELF note metadata into object files.

Dependencies/integration: included by BTI assembly sources.

Risks and test signals: incorrect note encoding would make kernel/loader treat the binary as non-BTI or malformed. Raw hint encodings preserve compatibility with assemblers lacking mnemonic support.
