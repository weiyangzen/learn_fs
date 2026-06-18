<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/eeh.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/eeh.h

Purpose: Defines user-visible PowerPC EEH PCI error state and error injection classifications.

Important APIs/types/functions: PE state constants `EEH_PE_STATE_*`, error type constants, and error function constants for load/store/config/DMA address/data/master/target events.

Control flow: EEH user interfaces and tooling pass these numeric constants to query or inject PCI error conditions.

State and persistence: No state owned; values describe PCI PE state maintained by EEH core/firmware.

Dependencies and integration points: Integrated with EEH kernel code, debugfs/sysfs/ioctl-like users, and platform firmware error handling.

Risks: Numeric ABI changes break diagnostic tooling. Function ranges must match kernel validation.

Test signals: EEH recovery and error injection tests on pSeries/PowerNV PCI, plus userspace tooling compile checks.

Source read size: 44 lines, 1580 bytes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/uapi/asm/eeh.h -->
