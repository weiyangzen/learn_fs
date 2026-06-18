# sources/distributed-fs/ceph-client/tools/testing/selftests/kvm/lib/arm64/gic.c

## Purpose
This is the architecture-neutral guest-facing ARM GIC wrapper used by arm64 selftests. It hides the concrete GIC implementation behind `struct gic_common_ops` and currently selects the GICv3 implementation.

## Important APIs, Types, and Functions
`gic_init()` initializes distributor state once and CPU interface state per vCPU. Public helpers include interrupt enable/disable, acknowledge/EOI/DIR, priority and priority mask operations, pending/active state manipulation, configuration, and group selection. `gic_dist_init()` serializes global initialization with `spin_lock()`.

## Control Flow
On first `gic_init()`, the calling vCPU acquires `gic_lock`, chooses `gicv3_ops` for `GIC_V3`, runs distributor initialization, publishes `gic_common_ops`, executes `dsb(sy)`, and releases the lock. Every caller then initializes its CPU interface.

## State, Dependencies, and Integration
Persistent guest state is the static `gic_common_ops` pointer and `gic_lock`. The code depends on `gic_private.h`, `gic_v3.c`, processor barriers, and the arm64 spinlock implementation. It integrates with guest interrupt tests that use generic `gic_*` APIs.

## Risks and Test Signals
Only GICv3 is implemented, so unsupported types assert. Correctness depends on one-time distributor initialization and memory ordering before other vCPUs call through the ops table. Tests signal issues through `GUEST_ASSERT()` or unexpected interrupt behavior.
