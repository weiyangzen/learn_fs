# sources/distributed-fs/ceph-client/drivers/net/ethernet/intel/fm10k/fm10k_debugfs.c

## Purpose
`fm10k_debugfs.c` creates debugfs views for fm10k descriptor rings. It exposes per-q_vector directories and per-ring files that dump TX or RX descriptor contents through seq_file.

## Important APIs, types, and functions
Important functions include descriptor seq operations (`fm10k_dbg_desc_seq_start`, `next`, `stop`, TX/RX `show`), `fm10k_dbg_desc_open`, q_vector lifecycle (`fm10k_dbg_q_vector_init`, `fm10k_dbg_q_vector_exit`), interface lifecycle (`fm10k_dbg_intfc_init`, `fm10k_dbg_intfc_exit`), and driver root lifecycle (`fm10k_dbg_init`, `fm10k_dbg_exit`). `dbg_root` stores the root dentry.

## Control flow
Driver init creates a root directory named after `fm10k_driver_name`. Interface init creates a PCI-name child directory. Each q_vector init creates `q_vector.NNN` and files for each TX/RX ring. Opening a descriptor file selects TX or RX seq ops based on whether the ring pointer is before the RX ring array in the q_vector allocation, then seq iteration walks descriptor indexes from zero to `ring->count - 1`.

## State and persistence behavior
Persistent debugfs state is held in `dbg_root`, `interface->dbg_intfc`, and `q_vector->dbg_q_vector`. The files read live descriptor memory and ring metadata; they do not snapshot or lock descriptor contents. Entries are removed recursively on q_vector, interface, and driver teardown.

## Dependencies and integration points
The file depends on `CONFIG_DEBUG_FS`, Linux debugfs and seq_file APIs, and ring/q_vector layout from `fm10k.h`. Stubs in `fm10k.h` remove this feature when debugfs is disabled.

## Risks
Descriptor dumps can race with queue teardown or DMA updates unless lifecycle ordering prevents open files from outliving rings. The TX/RX selection relies on q_vector ring memory layout. Output is privileged mode `0600`, but still exposes DMA addresses and descriptor contents.

## Test signals
With debugfs enabled, load/unload the module and open/close interfaces while checking directory creation/removal. Read TX/RX descriptor files before and after ring allocation, under traffic, and during interface teardown with lockdep/KASAN enabled.
