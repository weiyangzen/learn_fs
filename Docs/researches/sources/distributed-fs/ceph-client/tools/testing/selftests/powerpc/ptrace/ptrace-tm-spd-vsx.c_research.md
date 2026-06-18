# sources/distributed-fs/ceph-client/tools/testing/selftests/powerpc/ptrace/ptrace-tm-spd-vsx.c

Purpose: validates ptrace access to VMX and VSX state when a traced process is in a suspended transaction, including checkpointed VMX/VSX writes and post-abort restoration.

Important APIs/types/functions: `load_vsx*()` wrappers feed assembly helpers from `ptrace-vsx.h`; `tm_spd_vsx()` drives the tracee transaction; `trace_tm_spd_vsx()` reads and writes live/checkpointed `NT_PPC_TM_CVMX` and `NT_PPC_TM_CVSX` regsets via helpers in `ptrace.h`.

Control flow: random arrays seed live, speculative, checkpoint, and replacement checkpoint data. The child loads checkpoint vectors before `tbegin.`, loads speculative values, suspends, loads suspended live values, and waits. The parent validates live VMX/VSX against `fp_load`, checkpointed state against `fp_load_ckpt`, writes `fp_load_ckpt_new`, detaches, and the child confirms the final restored state after abort.

State and persistence behavior: shared memory coordinates ready/release/abort flags. The vector arrays are process globals copied by fork and used as immutable expectations. No external persistence exists beyond the per-run child exit code.

Dependencies and integration points: requires real HTM, VSX/VMX ptrace regset support, assembly `loadvsx/storevsx`, and endian-aware vector validation helpers.

Risks and test signals: endian packing mistakes are caught by `validate_vmx()` and `compare_vsx_vmx()`. A stuck transaction or ptrace failure causes the parent to kill the child and fail.
