# sources/distributed-fs/ceph-client/drivers/hv/mshv_root.h

## Purpose

`mshv_root.h` is the private root-partition interface for `/dev/mshv`. It defines partition, VP, memory-region, IRQ routing, SynIC, doorbell, and root global state plus the internal APIs shared by root implementation files.

## Important APIs, Types, and Functions

- `struct mshv_vp` stores VP index, partition backpointer, mapped state pages, run flags, signal count, wait queue, and debugfs state.
- `struct mshv_partition` stores partition ID, refcount, mutexes, memory regions, VPs, IRQ/SRCU state, eventfd lists, routing table, async hypercall state, isolation type, init state, and debugfs dentries.
- `struct mshv_mem_region` tracks guest/user ranges, Hyper-V flags, type, page array, refcount, notifier, and mutex.
- IRQ structs model ack notifiers, LAPIC interrupt data, and routing table entries.
- `struct mshv_root` holds the partition hash table and VMM capabilities.
- Function declarations cover routing, port IDs, SynIC, partition refs/lookups, stats mapping, region operations, hypercall wrappers, and debugfs hooks.

## Control Flow

The header connects the module's implementation units. `mshv_root_main.c` owns lifecycle and ioctls; `mshv_root_hv_call.c` owns Hyper-V calls; `mshv_regions.c` owns memory; `mshv_irq.c` owns routing; `mshv_eventfd.c` owns eventfd bridges; `mshv_synic.c` owns interrupts and doorbells; `mshv_debugfs.c` owns stats exposure.

## State and Persistence Behavior

Partition objects are refcounted and RCU-hashed. VP objects live inside partitions and are exposed through anon inode fds. Memory regions are kref-managed. IRQ routing uses RCU/SRCU. Async hypercall state is one-per-partition because the implementation permits only one in-flight async hypercall per partition.

## Dependencies and Integration Points

The header depends on kernel locking, SRCU, hash tables, mmu notifiers, UAPI `linux/mshv.h`, Hyper-V HVDK types, and trace declarations. It defines the internal contract for all MSHV root files.

## Risks and Edge Cases

The structures expose many lock-protected fields; misuse can race with ISR, fd release, or RCU teardown. `MSHV_MAX_VPS` is fixed at 256. Version constants define the validated Hyper-V build range but module init logs rather than hard-fails on mismatch. `mshv_partition_encrypted()` currently recognizes SNP isolation only.

## Test Signals

Compile all MSHV configurations, validate lockdep annotations and partition reference behavior, stress create/destroy with live VP fds, verify RCU lookup safety from ISR paths, and test stats/debugfs fields under `CONFIG_DEBUG_FS` enabled and disabled.
