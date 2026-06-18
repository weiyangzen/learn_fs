<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/arm_sdei.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/arm_sdei.h

## Purpose
Defines Arm Software Delegated Exception Interface function ids, version decoding helpers, return values, event flags, status bits, and info constants.

## Important APIs, Types, And Functions
Macros derive SDEI 1.0 SMC/HVC function ids from `SDEI_1_0_FN_BASE`. Version helpers extract major/minor/vendor fields. Return constants include success, not supported, invalid parameters, denied, pending, and out of resource. Event constants cover register routing mode, running/enabled/registered status, completion status, event type, priority, and routing info.

## Control Flow
Kernel or low-level users issue SDEI calls by function id to register, enable, disable, complete, unregister, route, bind interrupts, and reset events. Results are decoded with the return constants and version macros.

## State And Persistence
SDEI event registration, enablement, routing, and PE mask state live in firmware/EL3 interface state until reset/unregister. The header only provides numeric ABI constants.

## Dependencies And Integration Points
Integrates with Arm firmware, SMC/HVC calling conventions, interrupt routing, and kernel SDEI support.

## Risks And Edge Cases
Function id width, signed negative returns, event priority/routing semantics, and firmware version differences are the main risks.

## Test Signals
Firmware feature probing, version decode tests, register/enable/complete/unregister cycles, invalid parameter handling, and interrupt bind/release tests on SDEI-capable platforms.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/arm_sdei.h -->
