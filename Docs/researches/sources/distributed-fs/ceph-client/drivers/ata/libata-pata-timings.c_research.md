<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-pata-timings.c -->
# sources/distributed-fs/ceph-client/drivers/ata/libata-pata-timings.c

Purpose: This helper library computes PATA timing register values from ATA transfer modes and device IDENTIFY timing fields. Low-level PATA drivers use it to turn mode choices such as PIO4, MWDMA2, or UDMA6 into bus-clock counts that satisfy ATA timing constraints.

Important APIs, types, and functions: The static `ata_timing[]` table records nanosecond timing requirements for PIO 0-6, single-word DMA 0-2, multi-word DMA 0-4, and UDMA 0-6 in `struct ata_timing` fields. Exported functions are `ata_timing_merge`, `ata_timing_find_mode`, and `ata_timing_compute`. `ata_timing_quantize` converts nanosecond timings to controller clock units using `T` for normal cycles and `UT` for UDMA cycles. The `ENOUGH` and `EZ` macros implement round-up conversion from nanoseconds to clock counts.

Control flow: `ata_timing_compute` finds the base mode row, copies it into the output, merges device-supplied EIDE PIO or MWDMA cycle minima when IDENTIFY word validity allows it, quantizes all fields, recursively merges the selected DMA/UDMA timing with the device's current PIO timing for commands still issued via PIO, and then lengthens active/recovery windows so the combined cycle constraints are met. `ata_timing_merge` is a field-selective maximum merge, allowing callers to enforce the slower of two timing sources. `ata_timing_find_mode` scans the ordered timing table and warns if no row exists.

State and persistence behavior: The file is stateless. It reads `adev->id` and `adev->pio_mode`, writes only the caller-provided `struct ata_timing`, and has no allocation, global mutation, hardware I/O, or persistent storage. Its results become persistent only if a low-level driver programs chipset timing registers from the returned structure.

Dependencies and integration points: It depends on `linux/libata.h` for transfer-mode constants, `struct ata_device`, IDENTIFY word indexes, CFA detection, and timing masks. It is typically integrated with driver `set_piomode`, `set_dmamode`, or `set_mode` callbacks and with libata mode selection performed during EH recovery in `ata_eh_set_mode`.

Risks and edge cases: The timing table must remain ordered by mode because `ata_timing_find_mode` advances while `xfer_mode > t->mode`. Bad or missing device IDENTIFY fields can cause conservative fallback to table timings but not runtime validation against hardware limits. Recursive PIO merging assumes `adev->pio_mode` is valid for DMA/UDMA modes. Rounding via clock periods can produce active plus recovery values larger than cycle, so the final correction expands `cycle`; controller drivers must tolerate these rounded values.

Test signals: Good coverage would compare computed timing structures against ATA/ATAPI and CFA reference values for each mode, including EIDE overrides, DMA merged with PIO fallback timing, non-divisible controller clock periods, invalid mode lookup returning `-EINVAL`, and the final cycle correction when quantization makes active plus recovery exceed cycle.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/ata/libata-pata-timings.c -->
