<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/interrupt.h -->
# sources/distributed-fs/ceph-client/tools/include/linux/interrupt.h

## Purpose
This is an intentionally empty compatibility include for code that references `<linux/interrupt.h>` while building in the tools tree.

## APIs And Flow
It exports only an include guard and no types, constants, or functions. There is no control flow.

## State, Dependencies, Risks, Tests
There is no state and no dependencies. The key integration point is compile compatibility for sources that include interrupt headers but do not actually use IRQ APIs in user space. The risk is silent inadequacy if code later starts using `IRQF_*`, `irqreturn_t`, or `request_irq()` symbols. Test signal is building all tools consumers and checking that no interrupt-specific symbol is required.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/include/linux/interrupt.h -->
