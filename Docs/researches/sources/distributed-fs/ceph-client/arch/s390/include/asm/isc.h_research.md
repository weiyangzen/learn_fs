# sources/distributed-fs/ceph-client/arch/s390/include/asm/isc.h

Purpose: This header centralizes s390 I/O interruption subclass assignments so channel, PCI, crypto, and guest drivers avoid collisions.

Important APIs/types/functions: `MAX_ISC`, driver-specific ISC constants (`IO_SCH_ISC`, `CONSOLE_ISC`, `PCI_ISC`, `AP_ISC`, `GAL_ISC`, etc.), and `isc_register()`/`isc_unregister()` are exposed.

Control flow: Drivers register the subclass they use before enabling devices and unregister when the last user goes away. Hardware priorities follow the architecture rule that ISC 0 is highest and 7 is lowest.

State and persistence: Subclass reference counts or masks live in implementation code; constants here define persistent driver policy.

Dependencies and integration points: It integrates CIO, console, EADM, CHSC, VFIO-CCW, QDIO, PCI, GIB alert, and adjunct-processor interrupt routing.

Risks and test signals: Two drivers sharing a subclass unintentionally can affect interrupt priority and masking. Tests should check balanced register/unregister, boot with all driver classes, and interrupt delivery under subclass masking.
