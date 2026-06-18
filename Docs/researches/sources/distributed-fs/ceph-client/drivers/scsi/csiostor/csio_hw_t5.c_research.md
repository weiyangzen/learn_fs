# sources/distributed-fs/ceph-client/drivers/scsi/csiostor/csio_hw_t5.c

## Purpose
`csio_hw_t5.c` implements the chip-operation table for Chelsio T5-class hardware. It handles PCIe memory-window programming, PCIe slow-path interrupt decoding, flash configuration address lookup, backdoor MC/EDC memory reads, generic adapter memory read/write through PCIe windows, and debugfs exposure of external memory regions.

## Important APIs and Functions
- `csio_t5_set_mem_win()` programs a T5 PCIe memory access window at `MEMWIN_BASE` with `MEMWIN_APERTURE` and reads it back to flush propagation.
- `csio_t5_pcie_intr_handler()` checks `PCIE_INT_CAUSE_A` against a static `intr_info` table of PCIe parity/queue/DMA errors; fatal bits call `csio_hw_fatal_err()`.
- `csio_t5_flash_cfg_addr()` returns `FLASH_CFG_START` for firmware configuration lookup.
- `csio_t5_mc_read()` uses MC BIST command/status registers to read a 64-byte aligned memory-controller block and optional ECC word.
- `csio_t5_edc_read()` performs the equivalent BIST read for EDC memory, with local T5 EDC register stride macros.
- `csio_t5_memory_rw()` maps EDC/MC memory type and offset into the PCIe memory window and loops over aperture-sized windows to read/write 32-bit words.
- `csio_t5_dfs_create_ext_mem()` adds debugfs files for `mc0` and `mc1` when the corresponding external-memory enable bits are set.
- `t5_ops` exports these functions through `struct csio_hw_chip_ops`.

## Control Flow and State
This file operates on `struct csio_hw` but does not own long-lived state. Its memory-window functions mutate adapter registers via MMIO. MC/EDC reads first verify no BIST is active, program aligned address/length/pattern fields, start BIST, wait for completion through `csio_hw_wait_op_done_val()`, then copy status registers into caller-provided buffers in network byte order. `csio_t5_memory_rw()` computes memory offsets from MA BAR size registers, moves a PCIe memory window over the requested region, and transfers words until `len` is exhausted.

## Dependencies and Integration Points
The file includes `csio_hw.h` and `csio_init.h`. It relies on register macros from `t4_regs.h` and bitfield macros from the T4/T5 hardware headers. Debugfs integration calls `csio_add_debugfs_mem()`. Fatal PCIe error reporting flows into `csio_hw_fatal_err()`. The exported `t5_ops` is selected by the generic hardware initialization path.

## Risks and Edge Cases
- `csio_t5_memory_rw()` rejects unaligned `addr` or `len`, but assumes `buf` points to enough 32-bit storage.
- Memory-type offset calculation depends on EDC/MC size registers; incorrect hardware values can map to the wrong adapter region.
- MC/EDC BIST reads return `-EBUSY` if a BIST is already running and rely on a fixed wait loop of ten one-unit polls.
- `csio_t5_edc_read()` uses `EDC_DATA(i) + idx`, which is compact but easy to misread; register layout changes would need careful review.
- PCIe interrupt handling treats most parity errors as fatal, so false positives can force adapter reset.

## Test Signals
Debugfs memory files should appear for enabled EDC/MC regions and return data without kernel faults. Tests should cover unaligned memory read/write rejection, busy BIST handling, PCIe fatal interrupt injection, and memory-window programming readback. Hardware bring-up logs should show `t5_ops` functions succeeding before queue and FCoE initialization.
