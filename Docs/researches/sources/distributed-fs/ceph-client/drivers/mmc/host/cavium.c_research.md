# sources/distributed-fs/ceph-client/drivers/mmc/host/cavium.c

## Purpose
`cavium.c` is the shared MMC/eMMC host implementation used by OCTEON and ThunderX front ends. It translates MMC core requests into Cavium MIO_EMM command, switch, buffer, and external DMA register operations, manages per-slot state on a shared controller, handles common interrupts, and probes/removes logical slot hosts from OF children.

## Important APIs, Types, and Functions
External symbols are `cvm_mmc_irq_names`, `cvm_mmc_interrupt`, `cvm_mmc_of_slot_probe`, and `cvm_mmc_of_slot_remove`. Key internals include `cvm_mmc_get_cr_mods`, `do_switch`, `cvm_mmc_switch_to`, `set_wdog`, `do_read`, `do_write_request`, `set_cmd_response`, `check_status`, `finish_dma`, `prepare_dma_single`, `prepare_dma_sg`, `prepare_ext_dma`, `cvm_mmc_dma_request`, `cvm_mmc_request`, `cvm_mmc_set_ios`, `cvm_mmc_init_lowlevel`, and `cvm_mmc_of_parse`.

## Control Flow and State
Every request acquires the bus through a front-end callback and releases it only on completion interrupt. Multiblock read/write requests are forced down the external DMA path and require a stop command. Single-block or non-data commands use the command path: switch to the target slot, prepare inline buffer data for ADTC writes or start SG iteration for reads, set watchdog, enable command interrupts, compute command/response XOR overrides, wait for stale hardware busy bits to clear, and write `MIO_EMM_CMD`.

The interrupt handler clears interrupt bits, checks switch errors, skips completion while DMA is still active, copies buffer data for non-DMA transfers on `BUF_DONE`, checks command/DMA done/error bits, maps response status into `cmd->error`, finishes DMA and unmaps SG, decodes responses, cleans pending DMA on error, clears `current_req`, calls `req->done`, invokes any DMA erratum completion hook, and releases the shared bus.

## State and Persistence Behavior
State is maintained in `struct cvm_mmc_host` and `struct cvm_mmc_slot`: current request, active DMA flag, SG iterator, cached per-slot switch/RCA values, slot clock, bus id, sample delay counts, feature flags, and callback pointers. No durable persistence exists. Slot switching saves the old slot’s switch/RCA registers and restores the new slot’s cached registers/sample delays. IOS updates control power through either a global GPIO callback or regulator, reset bus on power-off, and program clock, width, timing, and power class fields.

## Dependencies and Integration Points
The shared core depends on Linux MMC, OF properties, regulators, MMC GPIO helpers, DMA mapping, scatterlist iteration, bitfield macros, and front-end callbacks for bus locking, interrupt enabling, DMA fixups, and shared power. It consumes common properties via `mmc_of_parse`, legacy `cavium,bus-max-width`, `spi-max-frequency`, and Cavium skew properties. It advertises high-speed MMC/SD, CMD23, power-off-card, 3.3 V DDR, max block/count limits, and max SG count based on front-end SG capability.

## Risks and Test Signals
Risks include strict DMA requirements for multiblock requests, maximum SG FIFO count of 16, 8-byte DMA alignment/size assumptions, shared-controller slot switching, front-end bus-release correctness, response type XOR table correctness for SD vs MMC commands, and cleanup when DMA errors leave `DMA_PEND` set. Test signals include command-only requests, inline data requests, multiblock DMA reads/writes, SD and MMC response types, slot switching across multiple bus ids, regulator/global GPIO power transitions, skew property parsing, DMA error cleanup, and host removal with active slots.
