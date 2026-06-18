# sources/distributed-fs/ceph-client/fs/smb/server/smb2misc.c

## Purpose
Provides SMB2 request validation utilities. It checks SMB2 headers, fixed structure sizes, variable data area offsets/lengths, compound message boundaries, SMB2 credit charge correctness, and dispatches SMB2 negotiate requests into common negotiation handling.

## Important APIs, Types, and Functions
- `check_smb2_hdr()` rejects inbound messages already marked `SMB2_FLAGS_SERVER_TO_REDIR`.
- `smb2_req_struct_sizes[]` maps SMB2 command numbers to expected request `StructureSize2` values.
- `has_smb2_data_area[]` identifies commands with variable-length data areas.
- `smb2_get_data_area_len()` extracts and validates data offsets/lengths for session setup, tree connect, create, query/set info, read/write channel info or data, query directory, lock arrays, and ioctl buffers.
- `smb2_calc_size()` computes the expected PDU length from header, fixed structure, and variable data region, with special lock-array adjustment.
- Request length helpers compute credit-relevant sizes for query info, set info, read, write, query directory, and ioctl request/response maxima.
- `smb2_validate_credit_charge()` validates client `CreditCharge` against payload/expected response size, maximum dialect credits, granted credits, and outstanding credits under `conn->credits_lock`.
- `ksmbd_smb2_check_message()` is the public validator called before command dispatch.
- `smb2_negotiate_request()` forwards SMB2 negotiate handling to `ksmbd_smb_negotiate_common()`.

## Control Flow
`ksmbd_smb2_check_message()` obtains the current SMB2 PDU from the work item, bounds `NextCommand` against RFC1002 message length for compounds, normalizes the current PDU length, rejects server-to-client headers, checks SMB2 header size and command range, validates command-specific fixed structure size including SMB2.1 oplock/lease break exceptions, ensures fixed request size fits, calculates expected total size, accepts known padding variants, then validates credit charge when Large MTU capability is active.

`smb2_get_data_area_len()` is command-specific: for CREATE it considers both name and create-context regions and chooses a covering variable area; for WRITE it prioritizes data when `DataOffset` or `Length` is present, otherwise checks write-channel info; for LOCK it derives the lock array length from `LockCount`.

## State and Persistence
The file mutates only connection credit accounting: `conn->outstanding_credits` is increased when credit validation succeeds. It otherwise performs stateless validation over the request buffer.

## Dependencies and Integration Points
It depends on SMB2 PDU definitions, status/common constants, session and connection structures, and the common negotiate function. `smb_common.c` calls `ksmbd_smb2_check_message()` through dialect verification; `server.c` calls `ksmbd_verify_smb_message()` before dispatch. Correct validation is a prerequisite for `oplock.c` create-context parsing and all SMB2 command handlers.

## Risks and Edge Cases
- Validation accepts some padding mismatches to interoperate with Windows and Linux clients; the tolerance must not mask malicious overlong variable areas.
- `hdr->Command` is little-endian in the wire struct but many switch statements compare against SMB2 constants; this relies on the constants used here matching the field representation.
- Credit validation increments `outstanding_credits` but the corresponding decrement must happen elsewhere; leaks will throttle clients.
- `*off > 4096` and `MAX_STREAM_PROT_LEN` limits protect offsets/lengths, but command handlers still need their own semantic validation.
- Compound `NextCommand` handling must align with subsequent `ksmbd_req_buf_next()` advancement or a later command can be validated against the wrong slice.

## Test Signals
Fuzz SMB2 headers and all command fixed sizes, variable offsets, zero/nonzero lengths, CREATE name/context overlap, LOCK lock counts, IOCTL input/output/max response sizes, compound `NextCommand` offsets, padded PDUs, Large MTU credit charge under/over-reporting, outstanding credit overflow, CANCEL credit exemption, and NEGOTIATE size exceptions. Handler tests should assert malformed create contexts are rejected before `smb2_find_context_vals()` sees them.
