## sources/distributed-fs/ceph-client/arch/s390/include/asm/uprobes.h

### Purpose
`sources/distributed-fs/ceph-client/arch/s390/include/asm/uprobes.h` is a uprobes breakpoint ABI in
the s390 ceph-client Linux source snapshot. It has 33 lines and 588 bytes; exported UAPI contract:
no.

### Important APIs, Types, And Functions
architecture uprobe slot sizing and s390 breakpoint instruction encoding for execute-out-of-line
probes
Important macros/constants: `_ASM_UPROBES_H`, `UPROBE_XOL_SLOT_BYTES`, `UPROBE_SWBP_INSN`, `UPROBE_SWBP_INSN_SIZE`.
Important types/layouts: `arch_uprobe`, `arch_uprobe_task`.
Important declarations or inline helpers: none detected.

### Control Flow
The header itself has no standalone runtime loop; control flow is owned by the implementation files
that include it and call the declared entry points.

### State And Persistence
Most state is external to the header: CPU registers, lowcore fields, page tables, control blocks, or
caller-owned structures. Inline helpers may update hardware-visible state or caller buffers, but the
header does not allocate durable storage.

### Dependencies
generic uprobes, instruction decoding, notifier handling, and ptrace/debug paths. Direct include
dependencies detected here: `linux/notifier.h`.

### Integration Points
This header is included from the `sources/distributed-fs/ceph-client/arch/s390/include/asm` source-
tree area and feeds the s390 architecture boundary for generic uprobes, instruction decoding,
notifier handling, and ptrace/debug paths. For UAPI files, the integration point also includes
headers_install and userspace programs compiled against the exported layout.

### Risks
wrong breakpoint bytes or XOL size corrupt user instructions

### Test Signals
uprobes selftests, single-step emulation, and mixed 31/64-bit probe targets
