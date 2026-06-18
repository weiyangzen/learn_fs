# sources/distributed-fs/ceph-client/drivers/net/ethernet/altera/altera_utils.c

Purpose: this file provides four tiny read-modify-write helpers for manipulating bit masks in Altera TSE MMIO registers through the CSR accessors from `altera_tse.h`.

Important APIs, types, and functions: `tse_set_bit()` reads a 32-bit register, ORs a mask, and writes it back. `tse_clear_bit()` reads, clears a mask, and writes back. `tse_bit_is_set()` and `tse_bit_is_clear()` return integer truth values after reading the register. All functions accept a base `void __iomem *`, byte offset, and `u32` mask.

Control flow: callers in the main driver use these helpers around MAC command/config and TX/RX command-status registers. Each helper performs exactly one read and, for setters, one write; there is no locking inside the utility file.

State and persistence: the helpers mutate hardware register state only. They do not hold software state, cache values, or persist information beyond the device register write.

Dependencies and integration points: the file includes `altera_tse.h` for `csrrd32()` and `csrwr32()` and `altera_utils.h` for declarations. It is shared by the MAC reset/configuration and multicast/link code in `altera_tse_main.c`.

Risks: these are non-atomic read-modify-write operations against MMIO. Callers must hold the appropriate driver lock, such as `mac_cfg_lock`, when concurrent updates are possible. Any register with write-one-to-clear or side-effect bits would be unsafe with these generic helpers; current callers use command-style registers where read-modify-write is expected.

Test signals: compile/link checks should verify exported declarations match. Runtime signals are correct setting and clearing of MAC enable, reset, RX shift, TX shift, CRC, and promiscuous bits without losing unrelated command-config fields under concurrent link/multicast changes.
