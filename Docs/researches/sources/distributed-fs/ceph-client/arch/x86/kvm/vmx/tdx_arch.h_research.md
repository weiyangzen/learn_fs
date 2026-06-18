# sources/distributed-fs/ceph-client/arch/x86/kvm/vmx/tdx_arch.h

## Purpose
Defines architectural TDX field encodings, TD parameter layout, CPUID value layout, TSC conversion helpers, Secure EPT state decoding, and metadata IDs used by KVM's TDX implementation.

## Important APIs, Types, And Functions
Field encoding macros include `BUILD_TDX_FIELD()`, `BUILD_TDX_FIELD_NON_ARCH()`, `TDCS_EXEC()`, `TDVPS_VMCS()`, `TDVPS_STATE()`, `TDVPS_STATE_NON_ARCH()`, and `TDVPS_MANAGEMENT()`. Key structs are `struct tdx_cpuid_value` and the 1024-byte aligned/packed `struct td_params`. Helpers include `tdx_vcpu_state_details_intr_pending()`, `tdx_get_sept_level()`, and `tdx_get_sept_state()`.

## Control Flow
`tdx.c` uses these constants to build TDH_MNG_INIT input, read TDCS execution controls, read/write TDVPS fields, inject pending NMI, detect pending interrupt state, extend measurement in fixed chunks, interpret extended exit qualification, and construct metadata reads for TD CPUID values.

## State And Persistence
The file defines persistent ABI layout for `struct td_params`, including attributes, XFAM, max vCPUs, EPTP controls, config flags, TSC frequency, measurement IDs, owner fields, and CPUID values. It does not allocate state itself.

## Dependencies And Integration Points
Depends only on Linux types and bit helpers. It integrates with SEAMCALL wrappers, TDX module metadata, KVM userspace ABI conversion, and Secure EPT handling.

## Risks
Packed layout and field IDs must match the TDX module ABI exactly. TSC frequency conversion truncates to 25 MHz units, so callers must ensure the default TSC kHz is valid. Secure EPT state decoding must match module-provided level/state bit positions.

## Test Signals
Static size/build assertions in `tdx.c`, TD init success/failure against the TDX module, CPUID metadata reads, measurement extension, and Secure EPT fault handling validate these definitions.
