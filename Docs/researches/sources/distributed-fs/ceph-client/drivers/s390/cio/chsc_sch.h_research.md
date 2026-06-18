# sources/distributed-fs/ceph-client/drivers/s390/cio/chsc_sch.h

## Purpose
This private header defines the tiny request/private-state structures shared within the CHSC subchannel driver.

## Important APIs, Types, and Functions
`struct chsc_request` contains a completion and the IRB copied by the interrupt handler. `struct chsc_private` stores the currently active request pointer for a CHSC subchannel.

## Control Flow
There is no executable logic. `chsc_sch.c` initializes `chsc_request.completion`, assigns the request pointer before an asynchronous CHSC starts, and the IRQ handler clears the pointer and completes the request.

## State and Persistence
The structures hold only transient in-kernel request state. No persistent storage or exported API is defined.

## Dependencies and Integration Points
The header relies on includers having completion and IRB types available. It is local to the CHSC subchannel module and not a broad subsystem contract.

## Risks and Test Signals
Risk areas are request lifetime and header dependence on include order. Test signals are async CHSC ioctl completion, module remove while a request exists, and compile coverage of `chsc_sch.c`.
