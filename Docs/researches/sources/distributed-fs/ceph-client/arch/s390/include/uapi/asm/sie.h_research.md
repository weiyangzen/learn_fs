## sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sie.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm/sie.h` is a SIE intercept decode ABI
in the s390 ceph-client Linux source snapshot. It has 252 lines and 9469 bytes; exported UAPI
contract: yes.

### Important APIs, Types, And Functions
diagnose, SIGP, program-interrupt, and instruction-intercept macro tables plus decoding helpers used
by KVM trace tooling
Important macros/constants: `_UAPI_ASM_S390_SIE_H`, `diagnose_codes`, `sigp_order_codes`, `icpt_prog_codes`, `exit_code_ipa0(ipa0, opcode, mnemonic)`, `exit_code(opcode, mnemonic)`, `icpt_insn_codes`, `sie_intercept_code`, `INSN_DECODE_IPA0(ipa0, insn, rshift, mask)`, `INSN_DECODE(insn)`, `icpt_insn_decoder(insn)`.
Important types/layouts: none detected.
Important declarations or inline helpers: none detected.

### Control Flow
There is no executable control flow in this header; it defines constants and structure layouts that
are consumed by syscall, ioctl, signal, ptrace, or library paths elsewhere.

### State And Persistence
The persistent contract is the exported ABI: numeric constants, ioctl numbers, bit positions, and
packed structure layouts must remain stable across kernel releases. Runtime state lives in the
kernel drivers or userspace buffers that instantiate these declarations.

### Dependencies
KVM, perf trace decoding, QEMU diagnostics, and SIE intercept reporting. Direct include dependencies
detected here: none detected.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/uapi/asm`
source-tree area and feeds the s390 architecture boundary for KVM, perf trace decoding, QEMU
diagnostics, and SIE intercept reporting. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
decode macro drift makes userspace misclassify guest exits

### Test Signals
KVM tracepoint decode tests and intercepted instruction coverage
