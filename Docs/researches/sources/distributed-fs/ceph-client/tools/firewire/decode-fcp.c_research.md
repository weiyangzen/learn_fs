<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/decode-fcp.c -->
# sources/distributed-fs/ceph-client/tools/firewire/decode-fcp.c

Purpose: Adds FCP/AV-C protocol decoding to `nosy-dump` transactions so FireWire control frames are printed as human-readable command summaries.

Important APIs/types/functions: Data tables map AV/C `ctype`, subunit types, opcodes, and selected fields. `struct avc_frame` overlays the FCP payload. `decode_avc()` prints AV/C command type, subunit, opcode name, and field names. `decode_fcp()` is the exported decoder called with `struct link_transaction *`.

Control flow: `decode_fcp()` accepts only write-block requests to CSR FCP command/response offsets. It switches on `frame->cts`; CTS 0 routes to `decode_avc()`, other known CTS values print protocol names, and unknown/reserved values print a fallback. It returns `1` only when it handled an FCP frame.

State and persistence: No persistent state. It reads the current transaction request packet and prints to stdout.

Dependencies/integration: Depends on `linux/firewire-constants.h`, `nosy-dump.h`, and transaction assembly in `nosy-dump.c`. Integrated through the `protocol_decoders` table.

Risks/tests: Risks include unchecked payload size before casting to `avc_frame`, compiler-dependent bitfield layout, incomplete field value decoding, and assuming FCP offset constants. Test signals are captured FCP command/response logs, unknown opcode coverage, non-FCP write-block rejection, and big/little-endian smoke testing.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/firewire/decode-fcp.c -->
