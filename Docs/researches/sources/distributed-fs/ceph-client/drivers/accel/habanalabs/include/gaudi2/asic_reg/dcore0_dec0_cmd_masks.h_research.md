<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_masks.h -->
# sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_masks.h

## Purpose
`dcore0_dec0_cmd_masks.h` is the generated bitfield map for the DCORE0 decoder 0 command register bank, prototype `VSI_CMD`. It defines 144 shift/mask macros for software-visible decoder command/status registers `SWREG0` through `SWREG26` plus dummy registers `SWREG64` through `SWREG67`.

## Important APIs, types, and functions
The macro API covers version/id/builddate fields, normal and abnormal external interrupt source/gate fields, command-buffer execution count and address fields, AXI read/write total counters, work-state and AXI handshake status bits, start/reset/abort/clock-gate controls, IRQ cause and IRQ enable bits for end-command, bus error, timeout, command error, abort, and jump, timeout cycle/enable fields, command-buffer executable address/length/id fields, AXI read/write id and max burst controls, command swap bits, ready command-buffer count, and dummy scratch-style full-width fields.

## Control flow
This header has no logic. Decoder command code composes writes to the control and command-buffer registers, triggers execution with `SW_START_TRIGGER`, then polls or handles interrupts signaled through the IRQ and work-state fields. Reset and abort flows use the `SW_RESET_*` and `SW_ABORT_MODE` masks. Debug and performance paths decode AXI counters and handshake bits from the status registers.

## State and persistence behavior
The masks describe hardware registers whose values persist until cleared, overwritten, or reset. IRQ cause bits are latched hardware state, command-buffer address/length/id are active execution state, and AXI counters/handshake bits reflect live decoder traffic. Timeout and IRQ-enable settings persist across commands unless reprogrammed.

## Dependencies and integration points
This file is tied to `dcore0_dec0_cmd_regs.h`, decoder firmware/driver command submission, interrupt handling, and any video/scaler decoder command-buffer ABI used by the Gaudi2 stack. It is generated from the same `VSI_CMD` prototype used for similar decoder command blocks.

## Risks and edge cases
Risks include write-one-to-clear or latched IRQ fields being manipulated with ordinary read-modify-write code, command-buffer high/low address or length mismatch, starting execution before AXI ids/burst/swap fields are valid, and treating dummy/reserved fields as portable configuration.

## Test signals
Test signals include decoder command execution, end-command interrupt delivery, timeout/bus-error/command-error injection, reset and abort behavior, AXI counter movement during command execution, and no stuck work-state after repeated command buffers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/accel/habanalabs/include/gaudi2/asic_reg/dcore0_dec0_cmd_masks.h -->
