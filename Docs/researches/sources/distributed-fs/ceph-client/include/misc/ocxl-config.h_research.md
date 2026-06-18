# sources/distributed-fs/ceph-client/include/misc/ocxl-config.h

Purpose: This header lists OpenCAPI 3.0 PCI DVSEC capability IDs and register offsets used by the OCXL configuration parser and setup code.

Important APIs, types, and functions: It defines `OCXL_EXT_CAP_ID_DVSEC`, common DVSEC vendor and ID offsets, TL DVSEC offsets for backoff timers and receive/send capabilities/rates, Function DVSEC offsets for AFU index and actag configuration, AFU information offsets, AFU control offsets for termination, enable, PASID, and actag fields, and vendor DVSEC offsets for version and reset/reload fields.

Control flow: OCXL config code scans PCI extended capabilities for DVSEC entries, compares IDs, and uses these offsets to read and write OpenCAPI function, TL, AFU info, AFU control, and vendor-specific configuration.

State and persistence behavior: The header has no runtime state. The constants address persistent PCI config-space registers whose values configure AFU and link behavior.

Dependencies and integration points: It is consumed by `ocxl.h` implementation functions and lower-level PCI config access. It integrates with OpenCAPI device discovery, PASID and actag assignment, TL negotiation, AFU enable/disable, and vendor reset handling.

Risks: Constants must match the OpenCAPI 3.0 specification. Wrong offsets can write unrelated PCI config fields and break devices. Endianness and field width are handled by implementation, not this header.

Test signals: PCI config parser tests should cover DVSEC discovery, multiple AFUs, absent optional DVSECs, TL negotiation, PASID/actag programming, AFU enable state transitions, and vendor reset/reload register access.
