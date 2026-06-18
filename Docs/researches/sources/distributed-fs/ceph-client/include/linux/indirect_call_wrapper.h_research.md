<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/indirect_call_wrapper.h -->
# sources/distributed-fs/ceph-client/include/linux/indirect_call_wrapper.h

Purpose: Provides retpoline-aware wrappers that replace indirect calls with likely direct-call comparisons when mitigation is enabled.

Important APIs/types/functions: `INDIRECT_CALL_1` through `_4` compare a function pointer with known target functions under `CONFIG_MITIGATION_RETPOLINE`; otherwise they call directly through the pointer. `INDIRECT_CALLABLE_DECLARE`, `INDIRECT_CALLABLE_SCOPE`, and `EXPORT_INDIRECT_CALLABLE` manage symbol visibility. `INDIRECT_CALL_INET` variants adapt to IPv6/INET Kconfig.

Control flow: Hot networking paths pass a function pointer and likely targets; wrappers dispatch direct calls for matching targets or fall back to the function pointer.

State/persistence: Stateless macro dispatch.

Dependencies/integration: Tied to retpoline mitigation, export symbols, and networking protocol Kconfig.

Risks: Argument order must match target prototypes; missing `INDIRECT_CALLABLE` export can break modules.

Test signals: Builds with/without retpoline, IPv4-only/IPv6 configs, and objdump/perf checks showing direct target branches in hot paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/linux/indirect_call_wrapper.h -->
