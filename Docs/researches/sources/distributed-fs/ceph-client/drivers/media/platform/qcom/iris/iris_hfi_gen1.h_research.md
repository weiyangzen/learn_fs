# sources/distributed-fs/ceph-client/drivers/media/platform/qcom/iris/iris_hfi_gen1.h

## Purpose
`iris_hfi_gen1.h` declares the setup interface for the Gen1 HFI implementation and its instance allocator.

## Important APIs, Types, And Functions
The header declares `iris_hfi_gen1_command_ops_init()`, `iris_hfi_gen1_response_ops_init()`, and `iris_hfi_gen1_get_instance()`. It forward-declares `struct iris_core` and `struct iris_inst`.

## Control Flow
Platform initialization calls the command and response ops init functions to install Gen1 function tables into `struct iris_core`. Instance creation uses `iris_hfi_gen1_get_instance()` to allocate a plain `struct iris_inst`.

## State And Persistence Behavior
The header owns no state. The Gen1 implementation persists only the generic instance fields and uses Gen1 packet structs transiently on stack or heap.

## Dependencies And Integration Points
This is the generation selection hook used by platform data or probe code. It pairs `iris_hfi_gen1_command.c` with `iris_hfi_gen1_response.c`.

## Risks And Test Signals
If the wrong generation init is selected for hardware, command and response wire formats will mismatch. Probe tests should ensure platform data selects Gen1 only for compatible firmware/hardware.
