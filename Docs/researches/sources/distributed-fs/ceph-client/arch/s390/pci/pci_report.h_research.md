<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.h -->
# sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.h

Purpose: This private header declares the zPCI status-reporting helper used by event/recovery code.

Important APIs/types/functions: It forward-declares `struct zpci_dev` and declares `zpci_report_status`.

Control flow: There is no local control flow; callers include this header to report recovery/status strings against a zPCI device.

State and persistence: The header owns no state. Its function contract snapshots device status into the s390 debug log in the implementation.

Dependencies and integration points: It integrates `pci_event.c` with `pci_report.c` without exposing debug internals.

Risks and test signals: Build failures would catch signature drift. Runtime signal is debug-log entries from zPCI recovery paths.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/s390/pci/pci_report.h -->
