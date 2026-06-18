# sources/distributed-fs/ceph-client/arch/sparc/lib/NGmemcpy.S

Purpose: First-generation Niagara optimized memcpy engine and template for NG user-copy routines.

Important APIs/functions: Emits `NGmemcpy` by default. Defines `__restore_asi` and many `NG_ret_*` residual helpers. Macro hooks include `LOAD`, `LOAD_TWIN`, `STORE`, `STORE_INIT`, `EX_LD`, `EX_ST`, and `FUNC_NAME`.

Control flow: Uses a register window (`save`) and input registers for copy state. It checks lengths, aligns destination, uses paired loads/stores and block-init stores for large aligned spans, then handles medium and tiny copies. User wrappers override access macros for fault handling.

State and persistence: Stateless, but uses register-window state and temporary `%asi`.

Dependencies/integration: Includes `linux/linkage.h`, `asm/asi.h`, and `asm/thread_info.h`; patched by `NGpatch.S`.

Risks/test signals: Register-window conventions and residual helpers are fragile. Test every alignment low bit, length thresholds around 16/64, copy correctness, and user-copy faults at each stage.
