# sources/distributed-fs/ceph-client/drivers/soc/qcom/kryo-l2-accessors.c

## Purpose
Provides serialized indirect read/write helpers for Qualcomm Kryo L2 system registers on ARM64.

## Important APIs, Types, And Functions
Exports `kryo_l2_set_indirect_reg()` and `kryo_l2_get_indirect_reg()`. Uses raw spinlock `l2_access_lock` and system register definitions `L2CPUSRSELR_EL1` and `L2CPUSRDR_EL1`.

## Control Flow
Both helpers take the raw spinlock with IRQ save, write the target indirect register selector, execute `isb()`, then write or read the data register. Writes execute a second `isb()` before unlocking.

## State And Persistence
No heap state. Hardware state is the selected L2 indirect register and its value. The lock serializes selector/data register pairs across CPUs.

## Dependencies And Integration Points
Depends on ARM64 system-register accessors and is gated by `QCOM_KRYO_L2_ACCESSORS`. Other Qualcomm CPU/cache drivers use these exported symbols to configure Kryo-specific L2 registers.

## Risks
Incorrect register selectors or values can affect CPU/cache behavior. Serialization is mandatory because selector and data registers form a shared indirect access pair. Callers must know whether they are allowed to access these implementation-defined registers on the running CPU.

## Test Signals
Unit-level validation is limited; practical signals are successful callers on supported Kryo systems, no concurrent indirect access corruption under multi-CPU stress, and no undefined-instruction faults on configured platforms.
