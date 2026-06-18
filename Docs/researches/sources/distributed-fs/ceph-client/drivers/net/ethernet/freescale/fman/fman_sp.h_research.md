# sources/distributed-fs/ceph-client/drivers/net/ethernet/freescale/fman/fman_sp.h

## Purpose
Declares shared FMan storage/profile constants, buffer-margin structures, metadata offset structures, and helper prototypes used by FMan port initialization.

## Important APIs, Types, and Functions
Defines `ILLEGAL_BASE`, default 64-byte context alignment, external buffer pool and DMA attribute register bits, and internal-context shift constants. Important types are `fman_sp_int_context_data_copy`, `fman_sp_buf_margins`, and `fman_sp_buffer_offsets`. It declares `fman_sp_build_buffer_struct` and `fman_sp_set_buf_pools_in_asc_order_of_buf_sizes`.

## Control Flow and State
There is no runtime control flow. The header describes how buffer-prefix state is represented before it is converted into BMI register fields: copy offsets/sizes, external buffer start/end margins, and data/parser/timestamp/hash offsets.

## Dependencies and Integration Points
Includes `fman.h` and Linux integer types. It is consumed by `fman_sp.c` and `fman_port.c`, where constants are reused for BMI register shifts and pool flags.

## Risks and Test Signals
Risks are register-contract drift and offset sentinel misuse. Test signals include successful compilation of FMan port code, correct metadata offsets for configured prefix content, and Rx buffer pool programming with valid/backup/counter flags matching hardware expectations.
