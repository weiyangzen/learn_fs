<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_asm.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_asm.S

Purpose: Assembly support for VSX register preservation under preemption. It is the VSX analogue of the VMX helpers but targets wider VSR state.

Important APIs and types: Exports `check_vsx` and `preempt_vsx`. Uses `basic_asm.h` and `vsx_asm.h` macros to load/check VSX registers and return mismatch status.

Control flow: `check_vsx` compares active VSX register contents with a caller-provided memory image. `preempt_vsx` waits for C-side thread coordination, repeatedly validates VSR contents while `running` is set, and reports the first mismatch.

State and persistence: Architectural VSX registers are transiently modified. Coordination state is supplied via pointers to C globals.

Dependencies and integration points: Used by `vsx_preempt.c`; depends on VSX hardware support, the powerpc ABI, and kernel VSR save/restore.

Risks: The code is sensitive to register numbering and compiler/linker ABI mode. Because it tests low-level state, ordinary sanitizers or instrumentation may interfere.

Test signals: Passing the VSX preempt test shows stable VSR content across scheduler preemption.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/math/vsx_asm.S -->
