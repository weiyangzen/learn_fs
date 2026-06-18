# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/tm/tm-poison.c

Purpose: detects leakage of FP or VMX register state between parent and child across TM context switching on the same CPU.

Important APIs/types/functions: `tm_poison_test()` binds parent and child to one picked online CPU, child writes poison to f31/vr31, and parent repeatedly checks f31 then vr31 inside transactions.

Control flow: after HTM skips and CPU affinity setup, the child loops yielding and writing poison. The parent sets target registers to 1, then uses time-base-limited transactional loops to read back f31 and vr31; any value other than 1 indicates leaked state. The child is killed at the end.

State and persistence behavior: CPU affinity, live child process, FP/VMX registers, and time-base loop variables are the only state. No persistent files.

Dependencies and integration points: requires VSX move instructions, scheduler affinity, and real HTM. Harness timeout is extended to about 250 seconds.

Risks and test signals: long runtime and same-CPU scheduling are deliberate. Failure prints leaked register value and returns nonzero.
