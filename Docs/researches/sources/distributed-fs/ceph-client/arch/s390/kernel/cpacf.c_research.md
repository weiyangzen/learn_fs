# sources/distributed-fs/ceph-client/arch/s390/kernel/cpacf.c

## Purpose
Exposes raw s390 CP Assist for Cryptographic Function query masks and query-authentication-information blocks through CPU sysfs binary attributes.

## Important APIs, Types, And Functions
Macros `CPACF_QUERY()` and `CPACF_QAI()` generate read handlers and `BIN_ATTR_RO` objects for KM, KMC, KIMD, KLMD, KMAC, PCKMO, KMF, KMCTR, KMO, PCC, PRNO, KMA, and KDSA. `cpacf_init()` creates the `cpacf` binary attribute group under the CPU subsystem root.

## Control Flow
At device init, the CPU root kobject is looked up and a sysfs group is created. Each binary read executes the corresponding CPACF query or QAI instruction helper; unsupported instructions return `-EOPNOTSUPP`, supported ones copy the raw fixed-size result through `memory_read_from_buffer`.

## State And Persistence
No persistent state is owned. Data is queried on read, so sysfs output tracks current hardware/firmware capabilities.

## Dependencies And Integration Points
Depends on Linux sysfs, CPU subsystem devices, and `asm/cpacf.h`. It integrates hardware crypto capability discovery with userspace tools.

## Risks And Edge Cases
The raw binary ABI exposes instruction-specific masks, so size and naming are ABI-like. Unsupported facilities must fail cleanly. CPU root lookup failure silently skips group creation.

## Test Signals
Signals include sysfs presence under `/sys/devices/system/cpu/cpacf`, binary read length checks, unsupported instruction behavior, and comparison with CPACF facility bits on real hardware.
