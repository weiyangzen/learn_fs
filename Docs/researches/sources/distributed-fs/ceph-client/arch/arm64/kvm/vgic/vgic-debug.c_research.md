<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-debug.c -->
# sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-debug.c

## Purpose
This file implements VGIC debugfs views. It exposes distributor/vCPU IRQ state through `vgic-state` and ITS device/event translation table state through `vgic-its-state@<base>`.

## Important APIs, Types, And Functions
- `vgic_debug_init()` creates the VM-level `vgic-state` debugfs file.
- `vgic_debug_destroy()` is currently a no-op.
- `vgic_its_debug_init()` creates an ITS-specific debugfs file.
- `vgic_its_debug_destroy()` is currently a no-op.
- `struct vgic_state_iter` tracks distributor, vCPU, and INTID iteration for the VGIC state seq file.
- `struct vgic_its_iter` tracks current ITS device and interrupt translation entry.
- Seq operations are implemented by `vgic_debug_start/next/stop/show` and `vgic_its_debug_start/next/stop/show`.

## Control Flow
For `vgic-state`, seq iteration starts with distributor metadata, then walks private IRQs for each vCPU, SPIs, and LPIs in the distributor xarray. `vgic_debug_show()` prints distributor state first, skips IRQ details until VGIC initialization, obtains the current IRQ object, locks `irq_lock`, prints stable fields, unlocks, and drops the IRQ reference.

For ITS debugfs, `vgic_its_debug_start()` locks `its_lock`, finds the first device and ITE, advances to the requested seq offset, and returns an iterator. `next` advances within a device or to the next device. `show` prints a device header at the first ITE and then event ID to INTID/HWINTID/target/collection mapping.

## State And Persistence Behavior
The file does not own VGIC state; it snapshots existing distributor, IRQ, LPI xarray, and ITS tables. It allocates short-lived iterators per seq read. IRQ fields are protected by `irq_lock`; LPI xarray enumeration uses RCU; ITS table traversal holds `its_lock` for the seq session.

## Dependencies And Integration Points
It depends on debugfs, seq_file, interrupt APIs, KVM host structures, VGIC internals, RCU/xarray for LPIs, and ITS data structures. It is initialized from `vgic_init()` and ITS device creation paths.

## Risks And Edge Cases
- Iteration over LPIs switches from sequential INTIDs to xarray-driven lookup after SPIs; off-by-one errors can skip or repeat high INTIDs.
- Debug output must handle uninitialized VGICs and missing IRQ objects.
- Hardware SGI pending state may need `irq_get_irqchip_state()` rather than the cached latch.
- `vgic_its_debug_start()` returns `NULL` without unlocking `its_lock` if no device exists, which is a subtle path to review against seq_file expectations.
- Debugfs lifetime relies on KVM/debugfs teardown to remove files; explicit destroy hooks are no-ops.

## Test Signals
Read debugfs `vgic-state` before and after VGIC init, with multiple vCPUs, SPIs, LPIs, and hardware-backed interrupts. Read ITS debugfs with empty and populated device tables. Lockdep and RCU debug builds are useful for iterator/locking mistakes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm64/kvm/vgic/vgic-debug.c -->
