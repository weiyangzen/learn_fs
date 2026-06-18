## sources/distributed-fs/ceph-client/fs/smb/smbdirect/pdu.h

Purpose: Defines SMBDirect wire-format constants and packed PDU structures used for protocol negotiation and data transfer.

Important APIs and types: `SMBDIRECT_V1` is the supported protocol version. `SMBDIRECT_MIN_RECEIVE_SIZE` and `SMBDIRECT_MIN_FRAGMENTED_SIZE` encode minimum negotiated values from MS-SMBD. `struct smbdirect_negotiate_req` and `struct smbdirect_negotiate_resp` describe little-endian negotiation PDUs. `struct smbdirect_data_transfer` describes the data PDU header plus flexible payload. `SMBDIRECT_DATA_MIN_HDR_SIZE`, `SMBDIRECT_DATA_OFFSET`, and `SMBDIRECT_FLAG_RESPONSE_REQUESTED` are used by send/receive logic.

Control flow: This header has no runtime control flow. Its fields are populated in `connect.c`/`accept.c` for negotiate exchange and in `connection.c` for data transfer send/receive.

State and persistence: PDU structs represent on-wire state, not stored state. They are packed and use explicit little-endian integer types to preserve protocol layout across architectures.

Dependencies and integration points: Included by `internal.h`, which makes these definitions available across SMBDirect implementation files. Values integrate with MS-SMBD negotiation validation, credit exchange, keepalive response requests, and upper SMB message fragmentation.

Risks and edge cases: Any layout change would break wire compatibility. Callers must use endian conversion on all multi-byte fields. `data_offset` alignment and minimum header sizes are validated in receive code, so constants must remain consistent with struct layout and protocol expectations.

Test signals: Compile-time layout awareness, negotiation interop with SMBDirect peers, endian correctness on non-little-endian builds, malformed PDU validation, and data-transfer offset/length boundary tests.
