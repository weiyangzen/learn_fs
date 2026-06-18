<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/uv.c -->
# sources/distributed-fs/ceph-client/arch/s390/boot/uv.c

Purpose: Queries ultravisor capabilities during early boot and sanitizes protected virtualization host/guest flags before the kernel proper starts.

Important APIs/types/functions: Exports bootdata-preserved `prot_virt_guest`, `prot_virt_host`, and `struct uv_info uv_info`. Public functions are `uv_query_info()`, `adjust_to_uv_max()`, and `sanitize_prot_virt_host()`. Internal helper `is_prot_virt_host_capable()` enforces host eligibility.

Control flow: `uv_query_info()` requires facility 158, issues `UVC_CMD_QUI`, tolerates `UVC_RC_MORE_DATA`, copies supported ultravisor limits and feature indications into `uv_info` when KVM is enabled, and marks protected-virtualization guest support if set/remove shared-access calls are present. `adjust_to_uv_max()` constrains virtual layout limits for protected-virtualization hosts. `sanitize_prot_virt_host()` clears host mode unless command line, hardware, non-guest, non-kdump, and non-stand-alone-dump conditions are all satisfied.

State and persistence: `uv_info` and protected-virtualization flags are preserved boot data consumed by later s390 kernel and KVM code. The file also reads `oldmem_data` and IPL dump state.

Dependencies and integration points: Called early from `startup_kernel()` before layout decisions and again indirectly through `setup_kernel_memory_layout()` via `adjust_to_uv_max()`. Depends on facility bits, UVC calling ABI, KVM config, IPL dump detection, and crash dump state.

Risks: Incorrect ultravisor limits can place vmalloc/modules above secure storage addressability. Protected-virtualization mode must be disabled for kdump and stand-alone dump. The query intentionally ignores some extra data, so future UV fields require explicit copy support.

Test signals: Protected guest and protected host boots, KVM-enabled builds, facility-158 absent machines, kdump/stand-alone dump boots, and secure storage limit layout checks.

Source read size: 88 lines, complete file reviewed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/boot/uv.c -->
