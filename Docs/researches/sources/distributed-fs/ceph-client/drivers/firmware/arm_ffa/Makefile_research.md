# sources/distributed-fs/ceph-client/drivers/firmware/arm_ffa/Makefile

## Purpose
Defines kbuild composition for the Arm FF-A bus/core and transport module.

## APIs, Types, And Functions
`ffa-core.o` is built from `bus.o`. `ffa-module.o` is built from `driver.o` and optional transport objects, currently `smccc.o` when `CONFIG_ARM_FFA_SMCCC` is enabled. Both are tied to `CONFIG_ARM_FFA_TRANSPORT`.

## Control Flow
kbuild expands `ffa-transport-$(CONFIG_ARM_FFA_SMCCC)` and links the resulting object lists into the two FF-A build products.

## State, Persistence, And Dependencies
No runtime state is in the Makefile. Build artifacts depend on `ARM_FFA_TRANSPORT` and `ARM_FFA_SMCCC`.

## Integration Points
The split lets the bus layer register early as `ffa-core`, while the runtime driver and transport calls live in `ffa-module`.

## Risks And Test Signals
Risks are link omissions between bus, driver, and transport symbols. Test signals are module and built-in builds for FF-A with and without `ARM_FFA_SMCCC`.
