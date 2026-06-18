<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx_global_metadata.h -->
# sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx_global_metadata.h

Purpose: auto-generated header describing TDX global system-info metadata returned by the TDX module. Important types include `tdx_sys_info_version`, `tdx_sys_info_features`, `tdx_sys_info_tdmr`, `tdx_sys_info_td_ctrl`, `tdx_sys_info_td_conf`, and aggregate `tdx_sys_info`.

Control flow: TDX host initialization reads module metadata into these structures to size TDMRs, validate supported features, and configure TD controls. State is module-provided capability data cached by host code.

Dependencies include TDX module ABI and host KVM TDX setup. Risks include generated layout drift versus module metadata fields, causing invalid TD configuration. Test signals include TDX module initialization, metadata parsing tests, feature gating, and build checks when regenerating the header.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/include/asm/tdx_global_metadata.h -->
