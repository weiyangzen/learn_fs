# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/tdx/tdx_global_metadata.c

Purpose: Provides generated helper functions for reading TDX module global metadata fields into `struct tdx_sys_info`. It is intentionally included into another C file because it relies on the including file's `read_sys_metadata_field()` SEAMCALL primitive.

Important APIs/types/functions: `get_tdx_sys_info_version()` reads module major/minor/update versions. `get_tdx_sys_info_features()` reads `tdx_features0`. `get_tdx_sys_info_tdmr()` reads TDMR limits and PAMT entry sizes. `get_tdx_sys_info_td_ctrl()` reads TDR/TDCS/TDVPS base sizes. `get_tdx_sys_info_td_conf()` reads fixed attribute/XFAM masks, CPUID config count, max vCPUs per TD, and CPUID leaf/value arrays. `get_tdx_sys_info()` sequences the full read and logs the module version.

Control flow and state: Each helper short-circuits on first read error. CPUID array reads validate `num_cpuid_config` against destination array sizes before filling leaves and value pairs. The only persisted state is the caller-provided `tdx_sys_info` structure.

Dependencies and integration points: Field IDs are TDX module ABI constants encoded directly in the generated code. The helpers depend on Linux `ARRAY_SIZE`, `pr_info`, and the including translation unit's SEAMCALL read wrapper. `tdx.c` uses the result to check features, size TDMR/PAMT allocations, and expose sysinfo to KVM.

Risks and test signals: Stale generated field IDs or missing bounds checks can corrupt host setup or KVM's advertised TD capabilities. Test signals include module version logging, failure on unsupported metadata, CPUID config count overflows returning `-EINVAL`, and successful KVM TD creation using the exported sysinfo.
