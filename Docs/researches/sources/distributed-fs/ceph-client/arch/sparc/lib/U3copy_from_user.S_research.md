# sources/distributed-fs/ceph-client/arch/sparc/lib/U3copy_from_user.S

Purpose: UltraSPARC-III/Cheetah optimized copy-from-user wrapper.

Important APIs/functions: Defines guarded loads, `FUNC_NAME U3copy_from_user`, ASI-based `LOAD`, and `EX_RETVAL(0)` before including `U3memcpy.S`.

Control flow: Uses the U3 copy engine with user-space loads and exception fixups. Unlike U1 wrappers, this file does not define an explicit ASI preamble in the wrapper, so behavior follows `U3memcpy.S` defaults plus user load macros.

State and persistence: Stateless; uses `%asi`, VIS/FPU state, and exception-table entries.

Dependencies/integration: Depends on `U3memcpy.S` and `cheetah_patch_copyops`.

Risks/test signals: Verify expected ASI setup by callers/patching and correct residuals on load faults. Test U3 patched copy-from-user, page faults, and alignment variants.
