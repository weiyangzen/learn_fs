<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel/iosf_mbi.c -->
# sources/distributed-fs/ceph-client/arch/x86/platform/intel/iosf_mbi.c

## Purpose
Implements PCI-enumerated Intel IOSF sideband mailbox access and PMIC I2C bus arbitration between the kernel and P-Unit.

## Important APIs, Types, And Functions
Exports `iosf_mbi_read()`, `iosf_mbi_write()`, `iosf_mbi_modify()`, `iosf_mbi_available()`, `iosf_mbi_punit_acquire/release()`, `iosf_mbi_block_punit_i2c_access()`, notifier registration helpers, and `iosf_mbi_assert_punit_acquired()`. The PCI probe stores the singleton `mbi_pdev` and SoC semaphore address.

## Control Flow
Mailbox calls form MCR/MCRX values, serialize PCI config transactions with a spinlock, and reject GFX port access. PMIC arbitration waits for P-Unit users, notifies atomic-context users, blocks deep CPU idle via latency QoS, requests the P-Unit semaphore, polls for acknowledgement, and resets state on error. Unblock releases the semaphore and wakes waiters.

## State And Persistence
Global state includes `mbi_pdev`, the spinlock, PMIC access counts, semaphore address/acquired timestamp, notifier chain, waitqueue, and PM QoS request. Debugfs state exists only under `CONFIG_IOSF_MBI_DEBUG`.

## Dependencies And Integration Points
Uses PCI config-space offsets from `asm/iosf_mbi.h`, PCI IDs for Bay Trail/Braswell/Quark/Tangier, CPU latency QoS, blocking notifiers, debugfs, and CAP_SYS_RAWIO for raw debug transactions.

## Risks And Edge Cases
Misbalanced P-Unit/I2C acquire counts can deadlock PMIC access. Semaphore timeout resets the hardware semaphore and may leave callers surprised. MBI is not hot-pluggable and has no PCI remove path. Debugfs raw access can alter sideband registers and is permission-sensitive.

## Test Signals
Successful PCI probe, IOSF consumers returning non-`-ENODEV`, PMIC I2C transactions without SoC hangs under idle load, and debugfs access under debug builds validate behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/x86/platform/intel/iosf_mbi.c -->
