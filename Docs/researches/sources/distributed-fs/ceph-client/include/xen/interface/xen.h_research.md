# sources/distributed-fs/ceph-client/include/xen/interface/xen.h

## Purpose
`interface/xen.h` is the central public Xen guest ABI header. It assigns hypercall numbers, virtual IRQ numbers, MMU update and extended MMU operation formats, console/vm-assist commands, domain IDs, multicall layout, shared VCPU/time/event-channel structures, boot `start_info`, dom0 console info, and transient memory op layout.

## Important APIs, Types, and Functions
Major definitions include `__HYPERVISOR_*` IDs, `VIRQ_*`, `MMU_*`, `MMUEXT_*`, `UVMF_*`, `CONSOLEIO_*`, `VMASST_*`, `domid_t` and reserved `DOMID_*` values, `struct mmu_update`, `struct mmuext_op`, `struct multicall_entry`, `struct vcpu_time_info`, `struct vcpu_info`, `struct shared_info`, `struct start_info`, `struct xen_multiboot_mod_list`, `struct dom0_vga_console_info`, and `struct tmem_op`.

## Control Flow
Guests use hypercall numbers and command payloads to enter Xen. PV guests use MMU update and mmuext sequences to construct, pin, switch, flush, and update page tables. Event-channel delivery is mediated by `shared_info` bitmaps and per-VCPU pending/mask fields. Boot code consumes `start_info` to find shared info, Xenstore, console, modules/initrd, page tables, command line, and p2m data.

## State and Persistence Behavior
This header defines shared memory state (`shared_info`, `vcpu_info`, wallclock, event-channel bitmaps), boot-time immutable/resume-updated `start_info`, and hypervisor-managed MMU/domain state changed through hypercalls. Shared state persists while the domain runs and is refreshed on resume.

## Dependencies and Integration Points
It includes architecture-specific Xen interface definitions and is included by most Xen guest, event-channel, memory, time, boot, and driver code. Linux Xen setup, pvclock, event channels, PV MMU, console, Xenstore, and dom0 display paths all depend on this ABI.

## Risks and Test Signals
Risks include breaking struct sizes/offsets, page-table writable/pinning rule violations, event-channel lost-edge handling mistakes, seqlock-style time reads done incorrectly, boot `start_info` interpretation drift, and PAT/cache attribute translation bugs. Test signals include PV boot/resume, event-channel storm/mask tests, pvclock consistency, MMU update negative tests, console I/O, multicall batching, and dom0 console discovery.
