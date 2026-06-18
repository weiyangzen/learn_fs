# sources/distributed-fs/ceph-client/drivers/scsi/pm8001/pm8001_chips.h

Purpose: low-level register access helper header for PMC-Sierra SPC 8001/PM8001 SAS/SATA HBAs.

Important APIs: `pm8001_read_32()`/`pm8001_write_32()` directly dereference memory/register windows. `pm8001_cr32()`/`pm8001_cw32()` use BAR-indexed `readl`/`writel` via `pm8001_hba_info::io_mem`. `pm8001_mr32()`/`pm8001_mw32()` operate on arbitrary `void __iomem *` plus offset. `get_pci_bar_index()` maps PCI BAR addresses to internal indices.

Control flow/state: stateless inline helpers used by other PM8001 driver units. Correctness depends on valid ioremapped BARs and 32-bit register offsets.

Dependencies/integration: Linux MMIO primitives and PM8001 host structure definitions from surrounding driver headers.

Risks/test signals: direct `void *` arithmetic and `__le32 *` stores in `pm8001_write_32()` are suitable only for CPU-addressable memory, not arbitrary MMIO; endian behavior differs from `readl`/`writel`. Test register smoke during init, BAR index cases, sparse/endian checks, and adapter bring-up.
