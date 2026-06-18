<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_regs.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_regs.h

## Purpose
`dcore0_dec0_cmd_regs.h` is the generated address map for DCORE0 decoder 0 command registers, prototype `VSI_CMD`. It defines 31 `mmDCORE0_DEC0_CMD_SWREG*` addresses in the 0x41E0000-0x41E010C range for command submission, status, interrupt, timeout, AXI accounting, and dummy/scratch registers.

## Important APIs, types, and functions
There are no functions or types. The address constants cover contiguous `SWREG0` through `SWREG26` at 4-byte spacing and a second group `SWREG64` through `SWREG67`. Semantics are supplied by `dcore0_dec0_cmd_masks.h`: version/id, build date, interrupt sources, command execution address/length/id, command counters, AXI counters and handshakes, start/reset/abort controls, IRQ causes/enables, timeout, AXI id/burst/swap, and dummy fields.

## Control flow
Runtime code writes command-buffer address and control registers, starts execution through `SWREG16`, then waits by polling work/IRQ state or by handling interrupt status in `SWREG17`. Reset and abort paths also target this register window. The header itself only supplies the physical offsets used by those flows.

## State and persistence behavior
State is in the decoder command hardware. Command setup registers persist between commands, IRQ/status fields reflect latched or live decoder state, and dummy registers may persist as hardware scratch if used. Correct reset/init code should not assume power-on defaults after a soft reset unless the decoder block was actually reset.

## Dependencies and integration points
This file integrates directly with `dcore0_dec0_cmd_masks.h`, decoder command-buffer generation, interrupt handling, reset/recovery code, and any debug tooling that reads decoder command status.

## Risks and edge cases
Address mistakes in this header would redirect decoder control to unrelated DCORE registers. More realistically, callers can pair these addresses with stale or mismatched masks, write start/reset bits in the wrong order, or forget to clear/mask IRQ sources before submitting a new command.

## Test signals
Useful validation includes command-buffer execution, repeated start/reset cycles, interrupt status/clear behavior, timeout programming, AXI counter sanity under load, and register dump comparison against expected DCORE0 decoder address ranges.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_regs.h -->
