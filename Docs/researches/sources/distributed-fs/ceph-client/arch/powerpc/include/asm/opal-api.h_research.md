<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal-api.h -->
# sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal-api.h

## Purpose
This header is the Linux copy of the OPAL firmware ABI for PowerNV systems. It defines return codes, call tokens, event masks, message formats, PCI/EEH diagnostics, HMI data, PRD/OCC messages, I2C requests, dump/MPIPL records, and sensor/system policy enums.

## Important APIs, Types, And Functions
It exports OPAL status codes, console/event/interrupt/PCI/flash/sensor/security/MPIPL token numbers, quiesce and power-management flags, many enums for PCI freeze/reset/reinit/slot/LPC/message/system states, and ABI structs including `opal_msg`, `opal_ipmi_msg`, `OpalMemoryErrorData`, `OpalHMIEvent`, PHB error data variants, `oppanel_line_t`, PRD/OCC messages, `opal_sg_entry`, `opal_sg_list`, `opal_i2c_request`, and MPIPL structures.

## Control Flow
No C control flow is implemented. OPAL call wrappers and drivers use these constants to marshal firmware calls, interpret asynchronous messages, decode diagnostic payloads, and expose firmware state to kernel subsystems.

## State And Persistence Behavior
The file describes firmware-owned persistent or asynchronous state: event queues, error logs, PCI freeze state, sensors, flash/dump state, secure variables, and MPIPL/FADump metadata. Struct layouts and big-endian fields are ABI contracts.

## Dependencies And Integration Points
It is included by `opal.h`, PowerNV PCI, console, RTC, NVRAM, IPMI, I2C, dump, HMI, PRD/OCC, sensor, and power-control code.

## Risks And Edge Cases
Changing token values or structure layout breaks firmware ABI. Many fields are endian-specific. Diagnostic structs are versioned and hardware-generation-specific. Async calls require token lifecycle discipline.

## Test Signals
Build PowerNV, boot under OPAL firmware, exercise console, RTC, NVRAM, PCI config/EEH, sensors, flash/dump, IPMI/I2C, HMI handling, PRD/OCC paths, and MPIPL/FADump registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/powerpc/include/asm/opal-api.h -->
