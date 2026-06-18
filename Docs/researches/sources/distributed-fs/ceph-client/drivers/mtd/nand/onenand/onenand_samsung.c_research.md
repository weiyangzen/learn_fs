# sources/distributed-fs/ceph-client/drivers/mtd/nand/onenand/onenand_samsung.c

## Purpose
`onenand_samsung.c` provides Samsung S3C6400/S3C6410/S5PC110 OneNAND controller support. For S3C64xx it emulates the generic OneNAND BufferRAM model using controller command windows and private buffers. For S5PC110 it mostly uses generic OneNAND operations but overrides BufferRAM reads with controller DMA support.

## Important APIs, Types, and Functions
`enum soc_type` selects TYPE_S3C6400, TYPE_S3C6410, or TYPE_S5PC110. `struct s3c_onenand` stores the platform device, MTD pointer, mapped controller/AHB/DMA bases, SoC type, pseudo BufferRAM buffers, mapping callbacks, DMA state, physical base, and completion. Major functions are `s3c_onenand_setup()`, `s3c_onenand_probe()`, `s3c_onenand_remove()`, `s3c_onenand_command()`, `s3c_onenand_wait()`, `s3c_onenand_readw()`, `s3c_onenand_writew()`, `s3c_unlock_all()`, `s3c_onenand_bbt_wait()`, `s5pc110_read_bufferram()`, `s5pc110_dma_poll()`, and `s5pc110_dma_irq()`.

## Control Flow
Probe allocates a combined MTD/chip object and global driver state, derives the SoC type from platform IDs, calls `s3c_onenand_setup()`, maps resources, sets `this->base`, skips unlock-status checks, and then diverges by SoC. S3C64xx maps an AHB command window and allocates pseudo page/OOB BufferRAMs; S5PC110 maps DMA registers and chooses polling or IRQ-driven DMA. It then calls `onenand_scan()`, adjusts S3C subpage settings, logs sync burst mode, and registers MTD partitions from platform data.

S3C command execution builds SoC-specific mapped command addresses from block/page/sector fields. Reads fill private main/OOB buffers, writes drain them to the controller, erase/unlock commands write controller command values, and generic BufferRAM callbacks copy between MTD buffers and those private buffers. Wait handling polls Samsung interrupt/error status bits, acknowledges them, checks ECC and lock/program/erase failures, and updates MTD ECC counters.

## State and Persistence
Persistent state is flash content, block lock state, and erase/program results. Volatile state includes the file-scope `onenand` pointer, pseudo BufferRAM contents, controller interrupt status, DMA configuration, completion state, and platform-data partition registration. Resume calls `unlock_all()`, which may change block protection state after power management transitions.

## Dependencies and Integration Points
The driver depends on Samsung-specific register definitions in `samsung.h`, platform device IDs (`s3c6400-onenand`, `s3c6410-onenand`, `s5pc110-onenand`), MTD OneNAND core callbacks, DMA mapping, IRQs, and optional platform partitions. It does not use OF matching in this file.

## Risks
The global `onenand` pointer makes the implementation effectively single-instance. S3C64xx emulation must match generic BufferRAM expectations exactly; any index mismatch corrupts read/write staging. DMA completion in `s5pc110_dma_irq()` ignores timeout/error return after waiting and always returns 0 from the DMA helper. PM resume unconditionally unlocks all blocks. Illegal generic register accesses are logged but still route to mapped commands in some cases.

## Test Signals
Test on each supported SoC ID path. Signals include successful MTD registration, manufacturer/device probing, sync burst log, read/write/OOB/erase behavior, ECC failure accounting, lock/unlock status checks, DMA polling versus IRQ mode on S5PC110, and suspend/resume ensuring expected lock state.
