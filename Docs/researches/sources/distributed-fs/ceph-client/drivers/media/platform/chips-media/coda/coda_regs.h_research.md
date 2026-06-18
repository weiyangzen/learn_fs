# sources/distributed-fs/ceph-client/drivers/media/platform/chips-media/coda/coda_regs.h

## Purpose
`coda_regs.h` is the register ABI map for the Chips&Media CODA VPU driver. It has no executable logic; its purpose is to give the CODA driver stable symbolic names for memory-mapped register offsets, command mailbox registers, command ids, codec mode ids, bit masks, and field packing helpers across CODADX6, CODA7, and CODA9 hardware generations.

## Important APIs, Types, and Constants
The header exports preprocessor definitions only. Key groups are the basic BIT processor control registers (`CODA_REG_BIT_CODE_RUN`, `CODA_REG_BIT_BUSY`, `CODA_REG_BIT_RUN_COMMAND`, interrupt and reset registers), static firmware buffer registers (`CODA_REG_BIT_CODE_BUF_ADDR`, `CODA_REG_BIT_WORK_BUF_ADDR`, stream/frame memory control), command values (`CODA_COMMAND_SEQ_INIT`, `CODA_COMMAND_PIC_RUN`, `CODA_COMMAND_SET_FRAME_BUF`, `CODA_COMMAND_FIRMWARE_GET`), codec mode constants for decode and encode, and per-command mailbox offsets for decoder sequence init, decoder picture run, encoder sequence init, encoder parameter change, encoder picture run, frame buffer setup, header generation, firmware version reads, CODA9 GDI, and CODA9 JPEG.

## Control Flow and Integration
Control flow is indirect: other CODA source files write these offsets through MMIO accessors before issuing commands via `CODA_REG_BIT_RUN_COMMAND` and polling or interrupting on busy/status registers. The same mailbox address range has different meanings depending on the active command, so call sites must choose the macro family matching the command they are about to issue.

## State and Persistence
The file defines volatile hardware state, not kernel-persistent state. Register writes program firmware buffers, stream pointers, decoded/encoded frame state, SRAM use, JPEG state, and command arguments in the VPU. Values persist in hardware until reset, overwritten by a later command, or cleared by firmware.

## Dependencies and Risks
The header depends on Linux bit helpers such as `BIT()` being available through including translation units. Risks are primarily ABI drift and macro misuse: many offsets overlap by design, generation-specific fields differ, and incorrect endian, stride, address, or mode constants can silently corrupt DMA or firmware state.

## Test Signals
Useful signals are successful CODA probe and firmware version query, clean decode/encode/JPEG smoke tests on hardware for each supported generation, absence of timeout on `CODA_REG_BIT_BUSY`, correct interrupt reasons, and media compliance tests that exercise sequence init, picture run, frame buffer registration, and JPEG paths.
