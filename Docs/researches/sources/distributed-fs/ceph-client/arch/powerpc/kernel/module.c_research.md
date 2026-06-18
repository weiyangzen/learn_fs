
# sources/distributed-fs/ceph-client/arch/powerpc/kernel/module.c

Purpose: common PowerPC module finalization after architecture-specific relocation, applying CPU/MMU/firmware/speculation fixups and recording ABI v1 OPD bounds.

Important APIs/types/functions: `find_section`; `module_finalize`; `module_finalize_ftrace`; `do_feature_fixups`; `do_barrier_nospec_fixups_range`; `do_lwsync_fixups`; module architecture fields `start_opd` and `end_opd`.

Control flow: `module_finalize` first delegates ftrace finalization. It then locates optional special sections by name: `__ftr_fixup`, `__mmu_ftr_fixup`, PPC64 `__fw_ftr_fixup`, ABI v1 `.opd`, `__spec_barrier_fixup`, and `__lwsync_fixup`. Existing sections are patched in-place according to current CPU features, MMU features, firmware features, speculation barrier enablement, and lwsync capability.

State and persistence: mutates loaded module text/data before use and stores OPD address bounds in `me->arch` for later function-descriptor dereferencing. Effects persist for the lifetime of the module.

Dependencies and integration: sits between generic module loader and PowerPC-specific 32/64 relocation files; depends on section names emitted by build tooling and runtime feature masks in `cur_cpu_spec` and `powerpc_firmware_features`.

Risks: missing or malformed fixup sections leave code unpatched for the active CPU; ftrace finalization failure aborts module load; ABI v1 OPD bounds are required to distinguish descriptors from code pointers.

Test signals: load modules with feature-fixup sections on CPUs with differing features, test ftrace-enabled modules, ABI v1 function descriptors, speculation barrier toggles, and lwsync fixups.
