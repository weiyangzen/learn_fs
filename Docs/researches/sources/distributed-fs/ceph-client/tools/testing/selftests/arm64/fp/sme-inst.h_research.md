<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sme-inst.h -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sme-inst.h

Purpose: assembler macro header for SME, SME2, and FPMR instructions not always understood by all toolchains.

Important definitions: `REG_FPMR`, `rdsvl`, `smstop`, `smstart_za`, `smstart_sm`, `_ldr_za`, `_str_za`, `_ldr_zt`, and `_str_zt`.

Control flow and state: no runtime state; macros expand into `msr`, `.inst`, or `sys/sysl`-style encodings.

Dependencies and integration: included by FP ptrace, RDVL, SVE/ZA/ZT tests, and fork helpers. It centralizes architecture encodings used throughout this test subset.

Risks: incorrect instruction encodings create broad false failures. Macro operands are simple textual parameters, so callers must pass valid register numbers.

Test signals: indirect; successful ZA/ZT/SM/VL tests validate these encodings.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/arm64/fp/sme-inst.h -->
