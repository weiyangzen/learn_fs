# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mem_ops.h

Purpose: Declares LiquidIO Octeon core-memory access routines.

Important APIs, types, and functions: `octeon_read_device_mem64()` and `octeon_read_device_mem32()` read a single big-endian value from a core address and return host-endian data. `octeon_write_device_mem32()` writes a host-endian 32-bit value after conversion. `octeon_pci_read_core_mem()` and `octeon_pci_write_core_mem()` transfer arbitrary byte ranges between host buffers and Octeon memory.

Control flow: Higher-level code uses these APIs when it needs direct access to firmware/device memory rather than queue-based command submission. The C implementation handles BAR1 mapping and alignment details.

State and persistence: Function calls can read or mutate device memory. The header itself defines no state, but its APIs imply side effects on device memory and BAR1 registers.

Dependencies and integration: Requires `struct octeon_device` and the BAR1 mapping machinery from `octeon_device` function hooks. Used by diagnostics, console paths, and other low-level driver setup code.

Risks: These are low-level MMIO memory primitives; callers must pass valid core addresses, lengths, and live device pointers. They bypass command queue ordering, so use during reset or concurrent firmware access needs care.

Test signals: Compile coverage for all declarations, value endian round trips, partial buffer transfers, invalid/reset-device call avoidance, and callers that cross BAR1 entry boundaries.
