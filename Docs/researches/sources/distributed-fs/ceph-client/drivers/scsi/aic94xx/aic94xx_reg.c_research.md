# sources/distributed-fs/ceph-client/drivers/scsi/aic94xx/aic94xx_reg.c

Purpose: implements serialized register and internal-memory access for AIC94xx MMIO or legacy PIO mappings, including sliding-window management.

Important APIs/types/functions: public accessors are `asd_read_reg_byte/word/dword()`, `asd_write_reg_byte/word/dword()`, `asd_read_reg_string()`, and `asd_write_reg_string()`. Internal helpers perform raw byte/word/dword IO, compute SWA/SWB/SWC offsets, generate window-specific accessors, and `asd_move_swb()` pages sliding window B through PCI config space.

Control flow: reads/writes validate the internal address range, take `iolock`, choose SWA/SWB/SWC when the requested register is already mapped, or move SWB to cover the target register before accessing it. String reads/writes keep the lock while iterating byte accesses through private unlocked helpers.

State and persistence: updates `io_handle[0].swb_base` whenever SWB moves. Register writes mutate hardware state; no software persistence beyond current window base.

Dependencies and integration: depends on PCI config access, Linux IO primitives, memory barriers, `aic94xx_reg.h` constants, and `asd_ha_struct` IO mappings initialized in `aic94xx_init.c`/`aic94xx_hwi.c`.

Risks and test signals: all callers share one sliding window, so locking is essential. `BUG_ON()` range checks can crash the kernel on bad register constants. PIO mode masks offsets with `0xFF`, so it only works for the intended access window. Test signals include register access under concurrent interrupts/task paths, SWB movement across boundaries, string access crossing windows, MMIO versus IO-port mapping, and memory-barrier-sensitive hardware operations.
