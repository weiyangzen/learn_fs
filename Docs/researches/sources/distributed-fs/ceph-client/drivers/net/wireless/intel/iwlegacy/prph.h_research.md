# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlegacy/prph.h

## Purpose
`prph.h` defines iwlegacy internal peripheral register addresses and bit fields accessed indirectly through HBUS PRPH registers. It documents power management, bootstrap/uCode loading, data save/restore, and 4965 transmit scheduler register layout.

## Important APIs, Types, and Constants
- APMG power management registers and bits: `APMG_CLK_*`, `APMG_PS_CTRL_*`, `APMG_RFKILL_REG`, voltage and PCI L1 control masks.
- Bootstrap State Machine registers: `BSM_WR_CTRL_REG`, `BSM_DRAM_*`, `BSM_SRAM_LOWER_BOUND`, `BSM_SRAM_SIZE`, `BSM_DRAM_INST_LOAD`.
- 3945 scheduler registers under `ALM_SCD_*`.
- 4965 scheduler constants: `SCD_WIN_SIZE`, `SCD_FRAME_LIMIT`, `IL49_SCD_*` register offsets, queue write/read pointers, queue chain selection, interrupt mask, queue status bits, SRAM context offsets, translate table offsets.
- Queue and aggregation mapping helpers: `IL49_SCD_QUEUE_STATUS_BITS(x)`, `IL49_SCD_CONTEXT_QUEUE_OFFSET(x)`, `IL49_SCD_TRANSLATE_TBL_OFFSET_QUEUE(x)`.

## Control Flow and Integration
The long comments specify the firmware load sequence: write bootstrap instructions into BSM SRAM, program host DRAM pointers for init uCode, configure and start the BSM copy into instruction SRAM, enable future boot loads, release reset, wait for init alive, repoint DRAM registers to runtime images, then wait for runtime alive. During power-save, firmware can save data SRAM to host DRAM and BSM reloads runtime code/data on wake. Scheduler setup occurs after alive, when the driver can initialize queue context, byte count tables, queue modes, FIFO mapping, and RA/TID translation.

## State and Persistence Behavior
The header is declarative, but the described registers persist hardware state: clocks, power source, bootstrap memory, DMA image pointers, scheduler queue contexts, TX status bitmap, and RA/TID mappings. BSM SRAM can remain powered across certain low-power sleeps, while regular runtime data SRAM may be saved to host DRAM.

## Dependencies and Integration Points
`common.h` includes this file for PRPH helper users. Firmware loading, APM, scheduler initialization, aggregation setup, and internal SRAM access depend on these definitions. HBUS target PRPH and memory access offsets come from `csr.h`.

## Risks and Edge Cases
- Firmware load ordering is strict; programming instruction byte count is the trigger for runtime load.
- Saved runtime data in host DRAM can be modified firmware state, not a clean image; full reinitialization must use the original firmware data image.
- Scheduler ACK mode requires byte count tables and matching RA/TID queue mapping; wrong mode/fifo bits can break commands or aggregation.
- Internal register access requires NIC access and must not run while the MAC is asleep without wake sequencing.

## Test Signals
Use firmware boot/restart tests, suspend/resume power-save cycles, RF kill recovery, command queue bring-up after alive, aggregation start/stop, scheduler context dumps, and error injection around BSM load/poll timeouts.
