# sources/distributed-fs/ceph-client/drivers/char/ppdev.c

## Purpose
`ppdev.c` implements `/dev/parportN`, allowing userspace drivers to control parallel ports through the kernel parport subsystem. It exposes read/write data transfer in selected IEEE 1284 modes, a broad ioctl surface for port control and negotiation, interrupt notification, and automatic device-node creation for discovered parports.

## Important APIs, Types, and Functions
- `struct pp_struct` is per-open state: registered `pardevice`, IRQ wait queue/count, flags, IRQ response settings, current/saved IEEE1284 state, default timeout, and IDA index.
- `pp_open()` allocates per-open state and defers parport device registration until `PPCLAIM`.
- `register_device()` finds a parport by minor, allocates a per-device index, and calls `parport_register_dev_model()` with `pp_irq()`.
- `pp_do_ioctl()` implements `PPCLAIM`, `PPEXCL`, mode/phase getters and setters, register read/write/frob operations, data direction, negotiation, yield/release, IRQ control/count, timeout get/set, mode capability query, and user-visible flags.
- `pp_read()` and `pp_write()` require `PP_CLAIMED`, allocate a 1 KiB transfer buffer, configure inactivity timeout, and use parport or EPP operations depending on mode and flags.
- `pp_attach()` and `pp_detach()` create/destroy `/dev/parportN` class devices for parport instances.

## Control Flow
Module init registers major `PP_MAJOR`, registers class `ppdev`, and registers a parport driver. Opening a node only allocates state. `PPEXCL` must be requested before claim. `PPCLAIM` registers the parport device if needed, claims or blocks, saves the previous parport IEEE1284 state, installs the user's state, and enables IRQs. Most ioctls require the claimed state. Release restores saved IEEE1284 state, returns to compatibility mode if userspace forgot, releases/unregisters the parport device, frees the IDA index, and frees per-open state.

## State and Persistence
State is per-open plus global device nodes and `ida_index`. Hardware port state is mutated while claimed and restored as much as possible on release. IRQ count is atomic per open and consumed by `PPCLRIRQ`. No persistent storage is used.

## Dependencies and Integration Points
The file integrates with the parport core, `struct parport_operations`, IEEE1284 state machine, device classes, fixed char major registration, compat ioctl handling, poll wait queues, and user ABI constants in `linux/ppdev.h`.

## Risks
- The ioctl surface provides direct low-level hardware control to userspace; correctness depends on claim/release discipline.
- Some FIXME comments note mode and phase validation gaps.
- Global `pp_do_mutex` serializes ioctl operations but read/write paths can still interact with device state and IRQs.
- Release contains complex compatibility-mode cleanup to recover from userspace omissions.
- Timeout ioctl variants include 32/64-bit and sparc64 compatibility adjustments.

## Test Signals
Tests should cover open on valid/invalid minors, deferred registration, `PPEXCL` before/after claim, claim/release restoration, mode/phase get/set, EPP fast flags, IRQ poll and `PPCLRIRQ`, timeout ioctls on native and compat ABIs, parport attach/detach device creation, and cleanup after userspace exits without release.
