
# sources/distributed-fs/ceph-client/drivers/hwtracing/intel_th/sth.h

Purpose: Intel TH STH register offsets and channel MMIO structure.

Important APIs/types/functions: defines STH capability/global packet register offsets and `struct intel_th_channel`, whose fields represent data, marked data, timestamped data, user, flag, and master-error write locations.

Control flow: no runtime logic. `sth.c` indexes this channel array by master/channel and writes appropriate fields for STP packets.

State and persistence: describes hardware MMIO layout; no persistent state.

Dependencies and integration: included by `sth.c`.

Risks: header guard collides with `pti.h` (`__INTEL_TH_STH_H__`), so combined inclusion can suppress one header. Channel struct packing and field sizes must match hardware exactly.

Test signals: build with independent include ordering, packet-write tests for each field, and mmap address validation against `sizeof(struct intel_th_channel)`.
