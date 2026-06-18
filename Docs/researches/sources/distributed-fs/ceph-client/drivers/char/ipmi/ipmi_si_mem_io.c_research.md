<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_mem_io.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_mem_io.c

## Purpose
Implements memory-mapped register access setup for IPMI system-interface drivers. It binds `struct si_sm_io` to `readb/readw/readl/readq` and matching write helpers, reserves the register windows, maps them with `ioremap()`, and installs cleanup for the generic IPMI SI core.

## Important APIs, Types, and Functions
- `ipmi_si_mem_setup(struct si_sm_io *io)` is the exported setup entry point used when an IPMI SI resource is memory space.
- `intf_mem_inb/outb`, `intf_mem_inw/outw`, `intf_mem_inl/outl`, and optionally `mem_inq/outq` implement byte extraction/insertion across register widths using `regspacing` and `regshift`.
- `mem_region_cleanup()` releases each individually requested register region; `mem_cleanup()` unmaps and releases all regions if setup reached `ioremap()`.
- Depends on `struct si_sm_io` fields from `ipmi_si.h`: `addr_data`, `addr`, `regsize`, `regspacing`, `regshift`, `io_size`, `inputb`, `outputb`, `io_cleanup`, and `dev`.

## Control Flow
`ipmi_si_mem_setup()` rejects a zero physical address, selects accessors based on `regsize`, requests each register-sized memory region separately, computes a minimal contiguous mapping size, maps with `ioremap()`, and records `mem_cleanup()` as `io_cleanup`. On partial region reservation or mapping failure it unwinds all regions already claimed.

## State and Persistence
The persistent state is stored in the caller-owned `si_sm_io`: assigned function pointers, `io->addr` mapping, and cleanup callback. Resource ownership persists until the SI core calls `io_cleanup`.

## Dependencies and Integration Points
This is used by PCI, ACPI, OF, and platform SI discovery paths when the resource is `IPMI_MEM_ADDR_SPACE`. It depends on Linux MMIO APIs and `SI_DEVICE_NAME` for resource ownership.

## Risks
Register sizing is strict; unsupported `regsize` fails. `intf_mem_outw()` uses `writeb()` with shifted data while the read side uses `readw()`, which is intentional-looking legacy behavior but worth regression testing on 16-bit windows. Mapping spans from first register through the last full register while individual reservations may be disjoint, so any future change to `io_size` or `regspacing` arithmetic can over-map more than intended.

## Test Signals
Useful tests are probe/unprobe on KCS/SMIC/BT memory resources with 1, 2, 4, and 8 byte registers, failure injection for `request_mem_region()` and `ioremap()`, and ACPI systems with disjoint reserved register regions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_mem_io.c -->
