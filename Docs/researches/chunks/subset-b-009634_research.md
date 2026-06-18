# sources/user-network-fs/impacket/impacket/nt_errors.py lines 1989-3611

## Purpose

This chunk is the second half of Impacket's NTSTATUS constant catalog. It exports 1,623 module-level integer symbols for Windows NT status values from the warning range beginning at `STATUS_ALREADY_DISCONNECTED = 0x80000025` through the error range ending at `STATUS_VHD_DIFFERENCING_CHAIN_ERROR_IN_PARENT = 0xC03A0019`.

The constants mirror the numeric NTSTATUS values documented by Microsoft's MS-ERREF reference and are meant to be imported by SMB, SMB2/SMB3, DCE/RPC, Kerberos, examples, relays, and tests instead of hard-coding raw status numbers. The first chunk of the same file defines `ERROR_MESSAGES`, a numeric-code-to-name/message lookup table; this chunk provides the named Python constants that callers compare, return, and raise.

## High-Level Structure

- Lines 1989-2015 finish the warning-status block (`0x80000025` through `0x80210002`), including disconnection, plug-and-play, transaction log, filter manager, and BitLocker/FVE transient metadata statuses.
- Lines 2016-2351 cover core `0xC0000001` NTSTATUS errors: generic failure, invalid parameters, access denial, object and path errors, file/device/media errors, security identifiers, logon/account/password failures, pipe/network/share errors, and early filesystem/transaction errors.
- Lines 2352-2620 continue mainstream kernel, IO, authentication, certificate, cryptography, cluster, volume, EFS, smartcard, debugger, and callback status values.
- Lines 2621-2898 define RPC NT, endpoint mapper, PnP, MUI, cluster, ACPI, side-by-side activation, transaction manager, common log file system, filter manager, monitor, and graphics codes.
- Lines 2899-3441 are dominated by `STATUS_GRAPHICS_*` constants for VidPN topology, monitor descriptors, output protection manager, DDC/CI, physical monitor, session, and display-device failures.
- Lines 3442-3482 define BitLocker/FVE error statuses.
- Lines 3483-3545 define Windows Filtering Platform statuses, including provider/layer/filter/callout lookup, transaction, layer compatibility, validation, TCP/IP readiness, and injection-handle errors.
- Lines 3546-3587 define NDIS and Wi-Fi power/offload statuses.
- Lines 3588-3603 define IPsec and DoS-protection statuses.
- Lines 3604-3611 close the file with volume manager, virtual disk, and VHD differencing-chain status constants.

## Important APIs And Types

- The public API surface is the exported module constants themselves. There are no functions or classes in this chunk.
- Frequently consumed constants from this span include `STATUS_ACCESS_DENIED`, `STATUS_LOGON_FAILURE`, `STATUS_MORE_PROCESSING_REQUIRED`, `STATUS_NO_SUCH_FILE`, `STATUS_OBJECT_NAME_NOT_FOUND`, `STATUS_OBJECT_PATH_NOT_FOUND`, `STATUS_END_OF_FILE`, `STATUS_NOT_SUPPORTED`, `STATUS_PENDING`, `STATUS_DIRECTORY_NOT_EMPTY`, `STATUS_USER_SESSION_DELETED`, `STATUS_NETWORK_NAME_DELETED`, `STATUS_BAD_NETWORK_NAME`, and `STATUS_ACCOUNT_DISABLED`.
- `ERROR_MESSAGES`, defined earlier in the same module, is the companion lookup table used by exception `__str__` implementations to turn the integer values exported here into symbolic names and verbose messages.
- These constants use Python `int` values and are evaluated at import time. They do not wrap values in enums or classes, so comparisons are direct integer equality checks.

## Control Flow

This chunk has no runtime branching beyond Python module import evaluation. When `impacket.nt_errors` is imported, Python binds each uppercase name to the corresponding integer literal in file order.

Runtime behavior appears in consumers:

1. Protocol code imports selected constants or imports the `nt_errors` module.
2. Packet parsers, SMB server handlers, relays, examples, and tests compare wire status values against these constants or assign these constants into outgoing response fields.
3. Exception classes in `smb.py`, `smb3.py`, `smbconnection.py`, and several DCE/RPC modules look up the numeric code in `nt_errors.ERROR_MESSAGES` to render a symbolic error string.
4. If a consumer references a constant that exists here but the earlier `ERROR_MESSAGES` table lacks the same numeric code, symbolic comparisons still work, but string rendering may fall back to "unknown error code" in callers that guard dictionary membership.

## State And Persistence Behavior

- There is no mutable state in this chunk. Each binding is an immutable integer constant at module scope.
- There is no persistence, caching, IO, network activity, locking, or lifecycle management.
- The only state effect is namespace population when the module is imported. Subsequent imports reuse Python's module cache.
- Values are intentionally stable protocol constants. Changing a number would alter on-the-wire behavior for any caller that returns or compares that status.

## Dependencies And Integration Points

- The constants depend only on Python literal assignment. This chunk imports nothing and calls nothing.
- The file-level dependency is the MS-ERREF NTSTATUS catalog documented in the module header.
- SMB1 integration: `impacket/smb.py` uses `nt_errors.ERROR_MESSAGES` for NT status string rendering and imports `nt_errors` for code-to-message conversion in `SessionError`.
- SMB2/SMB3 integration: `impacket/smb3.py` imports constants such as `STATUS_SUCCESS`, `STATUS_MORE_PROCESSING_REQUIRED`, `STATUS_INVALID_PARAMETER`, `STATUS_NO_MORE_FILES`, `STATUS_PENDING`, `STATUS_NOT_IMPLEMENTED`, and `ERROR_MESSAGES`; the constants in this chunk are part of that same import surface.
- SMB server integration: `impacket/smbserver.py` imports many NTSTATUS names directly, including codes from this span, and returns them from command handlers to shape SMB error responses.
- High-level SMB connection integration: `impacket/smbconnection.py` raises `SessionError` values backed by this module and compares errors such as `STATUS_END_OF_FILE`.
- DCE/RPC integration: modules such as `samr.py`, `nrpc.py`, `mgmt.py`, `rpch.py`, and `even.py` consult `nt_errors.ERROR_MESSAGES` when formatting RPC exceptions that carry NTSTATUS values.
- Kerberos integration: `impacket/krb5/kerberosv5.py` decodes NTSTATUS values embedded in Kerberos error data and maps them through `nt_errors.ERROR_MESSAGES`.
- Examples and relay tools import common constants directly, especially access, authentication, success, and continuation statuses.

## Risks And Edge Cases

- Numeric accuracy is critical. A typo in any assignment can silently make protocol logic compare or emit the wrong NTSTATUS value.
- The constants are plain integers, so there is no type boundary between NTSTATUS, HRESULT, Win32, SMB legacy error codes, and arbitrary integers. Callers must choose the correct error namespace.
- `ERROR_MESSAGES` is keyed by integer, while this chunk is keyed by symbol name. If the two halves drift, code comparisons can still succeed while human-readable messages become wrong or unavailable.
- Duplicate numeric aliases exist. In this chunk `STATUS_FWP_TOO_MANY_BOOTTIME_FILTERS` and `STATUS_FWP_TOO_MANY_CALLOUTS` both equal `0xC0220018`. Python allows both constants, but the earlier `ERROR_MESSAGES` dictionary can preserve only one message for that numeric key because later duplicate keys overwrite earlier ones.
- Dictionary duplicate behavior also affects other aliases in the full file, such as success or abandoned-wait aliases from the first chunk. Tests should treat aliases as expected only when they match MS-ERREF, not as accidental duplicate data.
- `smb3.SessionError.__str__` indexes `ERROR_MESSAGES[self.error]` directly. If an SMB3 path raises a status constant not present in `ERROR_MESSAGES`, string conversion can raise `KeyError`; other callers guard membership and print an unknown-code fallback.
- The file is large and manually structured. Adding, removing, or regenerating constants should preserve ordering by numeric family because downstream maintainers use locality to audit related codes.
- Many constants in this span are rarely exercised by Impacket's normal SMB paths, especially graphics, FVE, WFP, NDIS, IPsec, and VHD statuses. They may be present for completeness rather than active local control flow.

## Test Signals

- Import smoke test: `from impacket import nt_errors` should import without syntax errors and expose representative constants from the beginning, middle, and end of this span.
- Value pinning tests should assert selected high-use constants: `STATUS_ACCESS_DENIED == 0xC0000022`, `STATUS_LOGON_FAILURE == 0xC000006D`, `STATUS_MORE_PROCESSING_REQUIRED == 0xC0000016`, `STATUS_OBJECT_NAME_NOT_FOUND == 0xC0000034`, `STATUS_NOT_SUPPORTED == 0xC00000BB`, and `STATUS_VHD_DIFFERENCING_CHAIN_ERROR_IN_PARENT == 0xC03A0019`.
- Message-table consistency tests should verify that high-use constants from this chunk exist in `ERROR_MESSAGES` and map to the expected symbolic names used in exception strings.
- Alias tests should explicitly document known duplicate numeric values such as `STATUS_FWP_TOO_MANY_BOOTTIME_FILTERS == STATUS_FWP_TOO_MANY_CALLOUTS == 0xC0220018`, so a future cleanup does not mistake a protocol alias for a regression without checking the source reference.
- SMB exception tests should raise or stringify representative `SessionError` instances with statuses from this chunk to confirm formatting paths remain stable.
- Protocol/server tests should cover returned values for common SMB failures: access denied, no such file, object/path not found, sharing violation, directory not empty, bad network name, and user session deleted.
- Static checks can parse every assignment in this span and compare against a generated MS-ERREF snapshot to detect accidental value drift, missing constants, or unexpected duplicate values.
