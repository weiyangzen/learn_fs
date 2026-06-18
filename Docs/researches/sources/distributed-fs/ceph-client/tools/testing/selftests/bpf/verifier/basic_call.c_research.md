# sources/distributed-fs/ceph-client/tools/testing/selftests/bpf/verifier/basic_call.c

Purpose: validates basic helper-call instruction decoding, helper ID validation, and argument register initialization across consecutive helper calls.

Important APIs/types/functions: uses raw `BPF_JMP | BPF_CALL` encodings, `BPF_FUNC_get_cgroup_classid`, `BPF_PROG_TYPE_SCHED_CLS`, and callee-saved `R6` for preserving context.

Control flow: invalid cases use a call with `BPF_X`, a call with reserved `off`, an unknown helper ID, and repeated helper calls without restoring `R1`. The accepted case saves `R1` in `R6`, calls the helper, restores `R1`, and calls again.

State and persistence behavior: focuses on register liveness after helper calls. The helper clobbers argument registers, so `R1` must be restored before reuse.

Dependencies and integration points: depends on helper availability for scheduler classifier programs. No map fixups.

Risks: call decoder changes can accidentally accept reserved fields; helper ABI changes can invalidate the liveness expectation.

Test signals: expected errors include `unknown opcode 8d`, `BPF_CALL uses reserved`, `invalid func unknown#1234567`, and `R1 !read_ok`; restored-argument case accepts.
