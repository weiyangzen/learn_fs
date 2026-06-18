# sources/distributed-fs/ceph-client/arch/sparc/lib/U1copy_from_user.S

Purpose: UltraSPARC-I/II/IIi/IIe optimized raw copy-from-user wrapper.

Important APIs/functions: Defines `FUNC_NAME raw_copy_from_user`, guarded integer/FP loads, `LOAD`, `LOAD_BLK`, `EX_RETVAL(0)`, and ASI preamble before including `U1memcpy.S`.

Control flow: Checks `%asi` and falls back to `raw_copy_in_user` for non-user ASI. The included U1 engine performs alignment setup, VIS/block copying, and tails while load exceptions return residual counts.

State and persistence: Stateless; uses `%asi`, VIS/FPU state, and exception-table records.

Dependencies/integration: Depends on `U1memcpy.S`, `asm/asi.h`, `asm/visasm.h`, and public raw-copy callers.

Risks/test signals: This is the default raw copy-from-user symbol for U1-class CPUs. Test user faults, small/large lengths, VIS state restoration, and fallback branch behavior.
