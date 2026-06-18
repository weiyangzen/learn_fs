<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_handler.S -->
# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_handler.S

Purpose: Low-level Event Based Branching handler. It saves user context, calls the C hook, restores context, and returns with `rfebb`.

Important APIs and types: Defines save-area layout for GPRs, selected SPRs, and VSRs; helper macros for saving/restoring/trashing registers; entry handling for ELFv1/ELFv2; and exports `ebb_handler`.

Control flow: On EBB entry the handler creates an ABI-compliant stack frame, saves registers and vector/scalar state, restores TOC as needed, calls `ebb_hook`, restores all saved state, and executes the raw `RFEBB` instruction.

State and persistence: It uses only the current thread stack for save state but modifies hardware EBB return state. No persistent memory is written outside the stack.

Dependencies and integration points: Linked with all EBB tests and installed into EBBHR by `setup_ebb_handler` in `ebb.c`.

Risks: This is the most ABI-sensitive EBB component. Stack layout, TOC restore, VSR save/restore, and `rfebb` encoding must be correct or tests can corrupt user state.

Test signals: Passing EBB tests, especially register access and repeated EBB tests, validates the handler save/restore path.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/pmu/ebb/ebb_handler.S -->
