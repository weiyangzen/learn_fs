# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/guest-state-buffer.h

Purpose: Defines the PowerPC KVM/PAPR nested-virtualization guest-state buffer ABI: guest-state IDs, serialized element format, buffers, bitmaps, parsers, and message helpers for H_GUEST state hypercalls.

Important APIs, types, and functions: Defines `KVMPPC_GSID_*` IDs for guestwide, hostwide, meta, register, vector, and interrupt state; element class/type/flag enums; serialized `struct kvmppc_gs_header` and `struct kvmppc_gs_elem`; buffer, bitmap, parser, message, partition-table, process-table, and buffer-info structures. Key APIs include `kvmppc_gsid_size()`, `kvmppc_gsid_flags()`, `kvmppc_gsid_mask()`, `kvmppc_gsb_new/free/put/send/recv()`, `__kvmppc_gse_put()`, `kvmppc_gse_parse()`, typed put/get helpers, bitmap operations, parser lookup, and message send/receive wrappers.

Control flow: Callers create a buffer, include GSIDs in a message bitmap, serialize requested state into big-endian elements, invoke send or receive hypercalls, parse returned elements into a lookup table, and refresh caller-owned data through message ops.

State and persistence: `struct kvmppc_gs_buff` tracks capacity, used length, guest ID, VCPU ID, and header pointer. Bitmap/parser/message state is transient kernel memory. Hypervisor-owned guest state changes persist outside the buffer.

Dependencies and integration points: Depends on `hvcall.h`, `plpar_wrappers`, bitmap APIs, GFP allocation, PowerPC vector layout offsets, and KVM Book3S HV nested guest management.

Risks: Serialized sizes and endianness are ABI-sensitive. `kvmppc_gse_get_vector128()` warns on bad length but still continues after assigning zero, so malformed buffers need careful parser validation. GSID masks silently clear unsupported bits. Iteration trusts element counts and remaining length checks; off-by-one errors can drop or overrun elements.

Test signals: Round-trip every GSID class, malformed element lengths, full and empty bitmaps, vector layouts with and without VSX, buffer capacity exhaustion, H_GUEST send/receive failures, and parser duplicate/unknown GSID behavior.
