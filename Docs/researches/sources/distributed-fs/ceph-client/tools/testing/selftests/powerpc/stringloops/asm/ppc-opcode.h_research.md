# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/stringloops/asm/ppc-opcode.h

Purpose: local opcode macro shim for vector compare instructions that older assemblers may not know by mnemonic.

Important APIs/types/functions: defines `PPC_INST_VCMPEQUD_RC`, `PPC_INST_VCMPEQUB_RC`, field encoders `___PPC_RA/RB/RS/RT`, and macro emitters `VCMPEQUD_RC()` and `VCMPEQUB_RC()`.

Control flow: no runtime flow; macros emit `.long` instruction words in assembly.

State and persistence behavior: no state.

Dependencies and integration points: used by `memcmp_64.S` VMX loops to generate record-form vector compares.

Risks and test signals: incorrect opcode encodings would silently make the assembly test invalid or crash at runtime. Build success alone is not enough; `memcmp.c` comparisons validate behavior.
