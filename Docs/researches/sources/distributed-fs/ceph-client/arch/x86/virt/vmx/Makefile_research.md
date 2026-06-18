<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/Makefile -->
# sources/distributed-fs/ceph-client/arch/x86/virt/vmx/Makefile

## Purpose
`virt/vmx/Makefile` selects Intel VMX-side virtualization support directories.

## Important APIs, types, and functions
It descends into `tdx/` when `CONFIG_INTEL_TDX_HOST` is enabled.

## Control flow
Kbuild includes host TDX support only for TDX host configurations.

## State and persistence behavior
No runtime state is stored here.

## Dependencies and integration points
It depends on Intel TDX host configuration.

## Risks and edge cases
Incorrect selection can omit SEAMCALL/TDX module support on TDX-capable hosts.

## Test signals
Signals are TDX host configured builds.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/virt/vmx/Makefile -->
