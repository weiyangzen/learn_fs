<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_base.c -->
# sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_base.c

## Purpose
`vcpu_sbi_base.c` implements the SBI BASE extension for RISC-V KVM guests. It answers specification, implementation, machine identity, and extension probing queries.

## Important APIs, Types, And Functions
`kvm_sbi_ext_base_handler()` handles `GET_SPEC_VERSION`, `GET_IMP_ID`, `GET_IMP_VERSION`, `PROBE_EXT`, `GET_MVENDORID`, `GET_MARCHID`, and `GET_MIMPID`. `vcpu_sbi_ext_base` exports the handler for `SBI_EXT_BASE`.

## Control Flow
The handler switches on guest `a6`. Most calls fill `retdata->out_val` directly. `PROBE_EXT` forwards experimental and vendor probes to userspace; otherwise it calls `kvm_vcpu_sbi_find_ext()` and optional extension probes. Unknown functions set `SBI_ERR_NOT_SUPPORTED`.

## State And Persistence
The file does not own mutable state. It reads per-vCPU architectural id fields and effective extension availability maintained by `vcpu_sbi.c`.

## Dependencies And Integration Points
It depends on Linux version metadata, SBI constants, and the shared KVM SBI dispatcher. Guest firmware and operating systems use this extension to discover the virtual SBI surface.

## Risks
Probe behavior is ABI-visible. Experimental/vendor ranges must remain forwardable so userspace VMMs can implement policy. Reported implementation version is `LINUX_VERSION_CODE`, so guests can infer host kernel lineage.

## Test Signals
Run SBI probe selftests for every enabled/disabled extension, legacy guests expecting BASE, and userspace-forwarding tests for vendor/experimental ids.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/riscv/kvm/vcpu_sbi_base.c -->
