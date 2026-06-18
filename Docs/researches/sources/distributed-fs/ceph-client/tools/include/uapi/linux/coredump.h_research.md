# sources/distributed-fs/ceph-client/tools/include/uapi/linux/coredump.h

Purpose: defines a userspace coredump-server negotiation ABI. It lets the kernel request a coredump handling decision, lets userspace acknowledge selected behavior, and defines marker bytes for request/ack validation results.

Important APIs/types: feature flags include `COREDUMP_KERNEL`, `COREDUMP_USERSPACE`, `COREDUMP_REJECT`, and `COREDUMP_WAIT`. `struct coredump_req` carries request size, maximum known ack size, and supported feature mask. `struct coredump_ack` returns ack size and selected mask. `enum coredump_mark` reports success or failures such as min size, max size, unsupported mask, or conflicting options.

Control flow, state, and persistence: runtime flow is kernel sends `coredump_req` on a coredump socket, userspace reads/peeks the versioned size, sends a bounded `coredump_ack`, and kernel emits one marker byte. State is transient per crash; persistence is in the generated core or userspace coredump service policy, not in this header.

Dependencies and integration points: depends on `<linux/types.h>`. It integrates kernel coredump generation with external coredump daemons and versioned UAPI negotiation.

Risks and test signals: risks are size negotiation bugs, accepting unsupported mask bits, conflicting kernel/userspace decisions, and old userspace reading only v0 structure sizes. Tests should cover short/long ack sizes, invalid masks, conflicting flags, successful kernel/userspace/reject flows, and forward-compatible larger request structs.
