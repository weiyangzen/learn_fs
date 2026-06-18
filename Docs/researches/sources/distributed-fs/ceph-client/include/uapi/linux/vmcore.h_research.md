<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vmcore.h -->
# sources/distributed-fs/ceph-client/include/uapi/linux/vmcore.h

Purpose: defines UAPI structures and constants for device dump notes embedded in vmcore crash dumps and hardware error type classification.

Important APIs and types: `VMCOREDD_NOTE_NAME` and `VMCOREDD_MAX_NAME_BYTES` describe device dump note naming. `struct vmcoredd_header` carries ELF note name size, descriptor size, type, fixed `LINUX` name, and a device dump name. `enum hwerr_error_type` categorizes recoverable CPU, memory, PCI, CXL, and other errors.

Control flow, state, and persistence: crash dump producers write device dump headers into vmcore notes; crash analysis tooling reads them later. Persistence is the vmcore file, not kernel runtime state.

Dependencies and integration points: integrates with kdump/vmcore, device crash dump providers, ELF note parsing, and hardware error reporting.

Risks and test signals: risks include note size mismatches, non-terminated dump names, and enum drift in user tools. Test kdump generation with device dumps, vmcore parser compatibility, maximum name length, and hardware error note consumers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/linux/vmcore.h -->
