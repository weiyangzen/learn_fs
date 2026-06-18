# sources/distributed-fs/ceph-client/include/cxl/event.h

Purpose: defines CXL event, CPER event, protocol-error section, RAS capability, and work-queue handoff structures for CXL error handling.

Important APIs, types, and flow: packed record structs mirror CXL 3.x event formats: common headers, media headers, generic events, general media, DRAM, health info, memory module, and memory sparing records. `union cxl_event` and `cxl_event_record_raw` carry typed event payloads with UUIDs. CPER structures capture event record headers, device IDs, serial numbers, and protocol-error sections matching UEFI layouts, including agent type, RCRB/SBDF addressing, device ID, serial, capability, DVSEC length, error length, and RAS registers. Work APIs register/unregister GHES work items and retrieve queued CPER event/protocol-error data, with disabled stubs returning zero or `-EOPNOTSUPP`; protocol errors can be validated, converted to work data, and handled.

State and persistence: structures represent firmware-reported records and queued work data. Actual queues are implementation-owned; no persistence is declared here.

Dependencies and integration: depends on UUIDs, workqueues, ACPI APEI GHES/PCIEAER, CPER, CXL RAS, and CXL mem/event consumers.

Risks and test signals: packed ABI layout must match CXL/UEFI specs exactly; validation bits and endianness are critical. Signals include `sizeof`/offset checks, GHES CPER injection, protocol-error validation tests, disabled-Kconfig builds, event-type decoding, and RAS header-log propagation.
