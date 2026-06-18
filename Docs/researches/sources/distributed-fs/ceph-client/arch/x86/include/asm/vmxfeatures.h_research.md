# sources/distributed-fs/ceph-client/arch/x86/include/asm/vmxfeatures.h

Purpose: Defines Linux-internal VMX feature bit numbers used to represent Intel VMX controls and capabilities.

Important APIs/types/functions: `NVMXINTS` says the feature bitmap uses five 32-bit words. `VMX_FEATURE_*` macros assign bit numbers for pin-based controls, EPT/VPID, aggregated APIC features, VMFUNC, primary/secondary/tertiary processor controls, and named features displayed in `/proc/cpuinfo` when comments provide quoted strings.

Control flow: No executable code. VMX capability parsing populates these bits; `vmx.h` converts them to control masks with `VMCS_CONTROL_BIT()`.

State and persistence: Feature bits are stored in CPU capability data elsewhere. This header is the numbering contract.

Dependencies and integration points: Included by `vmx.h` and VMX CPU feature reporting code. Tied to `/proc/cpuinfo` feature-name generation conventions.

Risks: Bit renumbering breaks control-mask mapping and user-visible feature reporting. Aggregated features such as `FLEXPRIORITY` and `APICV` must match the implementation's combined control requirements.

Test signals: VMX feature enumeration tests, `/proc/cpuinfo` checks on Intel hosts, KVM capability tests, and build checks for `NVMXINTS` coverage.
