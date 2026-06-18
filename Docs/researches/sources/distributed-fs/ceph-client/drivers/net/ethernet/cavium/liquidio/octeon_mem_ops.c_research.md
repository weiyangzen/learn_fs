# sources/distributed-fs/ceph-client/drivers/net/ethernet/cavium/liquidio/octeon_mem_ops.c

Purpose: Implements host access to Octeon core memory through PCI BAR1 mappings, including byte-range reads/writes and 32/64-bit accessors.

Important APIs, types, and functions: `octeon_pci_fastread()` and `octeon_pci_fastwrite()` copy unaligned leading/trailing bytes with byte I/O and aligned bodies with 64-bit I/O, toggling BAR1 swap mode on big-endian hosts. `__octeon_pci_rw_core_mem()` selects an existing console static mapping when possible, otherwise locks `mem_access_lock`, programs the dynamic BAR1 index, splits transfers at 4 MB BAR1 entry boundaries, copies data, restores the original index register, and unlocks. Public exports are `octeon_pci_read_core_mem()`, `octeon_pci_write_core_mem()`, `octeon_read_device_mem64()`, `octeon_read_device_mem32()`, and `octeon_write_device_mem32()`.

Control flow: Callers pass a core address and host buffer. The helper maps the address through BAR1 index `BAR1_INDEX_DYNAMIC_MAP`, performs the transfer, and advances address/buffer pointers until complete.

State and persistence: It temporarily modifies BAR1 index registers and possibly swap mode. The only persistent effect is the requested device-memory write; software state is restored after dynamic access.

Dependencies and integration: Depends on chip-specific `fn_list.bar1_idx_read/write/setup`, `oct->mmio[1]`, `console_nb_info`, and `mem_access_lock`. Exported symbols are used by console, diagnostics, and firmware interaction code.

Risks: The boundary calculation is delicate; incorrect copy length can overrun BAR1 windows. Locking protects the shared dynamic mapping, so bypassing it elsewhere can corrupt accesses. Endianness handling must match hardware expectations.

Test signals: Read/write across unaligned addresses, BAR1 4 MB boundaries, static console mapping hit, dynamic mapping restore, big-endian swap-mode behavior, and concurrent memory operations.
