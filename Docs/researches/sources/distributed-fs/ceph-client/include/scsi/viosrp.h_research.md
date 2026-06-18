# sources/distributed-fs/ceph-client/include/scsi/viosrp.h

Purpose: defines IBM virtual I/O SRP command/response queue formats and management datagrams used by pSeries/iSeries logical partitions to exchange SCSI and SRP management traffic.

Important APIs and types: `union srp_iu` wraps all base SRP IU variants with a 256-byte maximum. `struct viosrp_crq` defines the architected CRQ entry with valid/format/status/timeout/IU length and TCE pointer. Enums describe CRQ headers, init formats, SRP/MAD/OS-specific formats, and CRQ status codes. `struct mad_common` and MAD bodies cover empty IU, error log, adapter info, fast fail, capabilities, reserve, and migration data. `union viosrp_iu` combines SRP and MAD payloads; `struct mad_adapter_info_data` advertises SRP/MAD versions, partition identity, OS type, and per-port transfer limits.

Control flow: virtual SCSI clients place SRP or MAD IUs in DMA buffers, post CRQ entries, process init/complete events, and interpret status for DMA or partner failures. Empty IUs provide a way for the server to respond asynchronously despite the request-oriented flow.

State and persistence: no persistent state is owned here. Hypervisor/driver state includes CRQ rings, DMA mappings, partition capabilities, and outstanding MAD/SRP tags.

Dependencies and integration points: includes `scsi/srp.h` and forms the ABI between Linux and IBM virtual I/O servers, including AIX and OS/400 compatibility.

Risks and test signals: structures are architected and cannot change without cross-OS breakage. Risks include endian errors, CRQ validity/status misinterpretation, MAD length mismatch, capability negotiation regressions, and TCE/IU lifetime bugs. Test virtual SCSI login, init-complete handshake, adapter info, migration/reconnect capabilities, fast-fail enablement, and mixed Linux/AIX/IBM i interoperability.
