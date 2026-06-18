# sources/user-network-fs/impacket/impacket/nt_errors.py lines 1-1988

## Scope

This chunk covers the header, the full `ERROR_MESSAGES` table, and the first 171 module-level numeric error-code aliases from `STATUS_SUCCESS` through `STATUS_SERVER_HAS_OPEN_HANDLES`. The source file continues past this chunk with many more aliases, but this range contains the complete descriptive lookup dictionary and the opening part of the constants block.

The module is data-only in this range. It has no imports, classes, functions, dynamic initialization, I/O, or branching control flow beyond Python evaluating literals at import time.

## Purpose

`nt_errors.py` centralizes Windows NTSTATUS values for Impacket. The opening comment identifies the data as NT STATUS errors from `[MS-ERREF]` and notes that other files should ideally use this table. The table lets protocol and application code translate integer NTSTATUS values into a symbolic name and verbose description, while the constants block lets callers compare or emit well-known numeric statuses without repeating magic numbers.

This exact chunk supplies:

- success, wait, pending, reparse, enumeration, and informational statuses;
- debugger, RPC, terminal-services, side-by-side, transaction, filter-manager, graphics, BitLocker/FVE, firewall-platform, NDIS, IPsec, virtual-disk, and other NTSTATUS families in `ERROR_MESSAGES`;
- the start of the public alias surface, including common SMB/RPC statuses such as `STATUS_SUCCESS`, `STATUS_PENDING`, `STATUS_MORE_ENTRIES`, `STATUS_NO_MORE_FILES`, `STATUS_ACCESS_DENIED` in the dictionary, and warning/informational aliases through `STATUS_SERVER_HAS_OPEN_HANDLES`.

## Important APIs And Data Shapes

- `ERROR_MESSAGES`: a module-level dictionary keyed by integer NTSTATUS values. Each value is a two-element tuple: `(symbolic_name, verbose_message)`. Consumers typically use `ERROR_MESSAGES[status][0]` for the status name and `[1]` for human-readable detail.
- Module-level constants such as `STATUS_SUCCESS = 0x00000000` and `STATUS_MORE_ENTRIES = 0x00000105`: integer aliases for direct comparisons, return values, packet status fields, and exception construction.
- `DBG_*`, `RPC_NT_*`, and `STATUS_*` names are all plain integers in the same module namespace; there is no enum type or class wrapper.

The `ERROR_MESSAGES` table contains 1,794 literal entries in this chunk. Python dictionary semantics mean duplicate keys are resolved at import time by the last occurrence. Two duplicate numeric keys are visible here:

- `0x00000080` appears as both `STATUS_ABANDONED` and `STATUS_ABANDONED_WAIT_0`; the effective dictionary entry is `STATUS_ABANDONED_WAIT_0`.
- `0xC0220018` appears as both `STATUS_FWP_TOO_MANY_BOOTTIME_FILTERS` and `STATUS_FWP_TOO_MANY_CALLOUTS`; the effective dictionary entry is `STATUS_FWP_TOO_MANY_CALLOUTS`.

The constants block keeps aliases for duplicate values separately, for example both `STATUS_ABANDONED` and `STATUS_ABANDONED_WAIT_0` are available as names bound to `0x00000080`.

## Control Flow

Import-time evaluation is the only control flow in this chunk:

1. Python executes the module comments as no-ops.
2. Python builds the `ERROR_MESSAGES` dictionary from literal integer keys and tuple values.
3. Python binds integer names in the `# Error Codes` section, starting at line 1818.

There are no lookups, validation helpers, reverse indexes, generated aliases, or exception classes in this range. All downstream behavior is driven by other modules importing these names and indexing the dictionary.

## State And Persistence Behavior

The data is process-local module state. Once imported, `ERROR_MESSAGES` and the constants remain in memory for the lifetime of the Python interpreter unless a consumer mutates the module namespace. The module itself does not persist anything to disk, open sockets, cache remote state, or write logs.

Persistence effects are indirect: Impacket protocol code uses these constants when constructing SMB, SMB relay, DCE/RPC, Kerberos, and service-specific responses or exceptions. A wrong value here can therefore change on-wire status codes or exception strings emitted by higher-level modules.

## Dependencies And Integration Points

This chunk has no direct imports. Its integration surface is the names it exports to the rest of Impacket.

Observed local consumers include:

- `impacket/smb.py` and `impacket/smbconnection.py`, which import `nt_errors` for `SessionError` formatting and status comparisons such as `STATUS_END_OF_FILE` and `STATUS_NOT_SUPPORTED`.
- DCE/RPC modules such as `dcerpc/v5/samr.py`, `mgmt.py`, `mimilib.py`, and `rpch.py`, which consult `nt_errors.ERROR_MESSAGES` when building `DCERPCSessionError` strings.
- Kerberos code in `krb5/kerberosv5.py`, which decodes NTSTATUS data embedded in Kerberos errors through `ERROR_MESSAGES`.
- Relay clients and servers under `impacket/examples/ntlmrelayx`, which import constants such as `STATUS_SUCCESS`, `STATUS_ACCESS_DENIED`, `STATUS_MORE_PROCESSING_REQUIRED`, `STATUS_NETWORK_SESSION_EXPIRED`, and `STATUS_BAD_NETWORK_NAME` for authentication and protocol response paths.
- Tests under `tests/SMB_RPC` and `tests/dcerpc`, which assert symbolic names such as `STATUS_ACCESS_DENIED` in exception text and compare numeric constants for enumeration loops.

The file is parallel in purpose to `system_errors.py`, `hresult_errors.py`, `mapi_constants.py`, and Kerberos `constants.ERROR_MESSAGES`: each gives protocol-specific numeric errors a stable lookup table for exception formatting and diagnostics.

## Risks And Maintenance Notes

- Duplicate dictionary keys are silent in Python. The two duplicates in this chunk intentionally or accidentally collapse to the later symbolic name in `ERROR_MESSAGES`, which can affect formatted exception text even though both constants may exist later as numeric aliases.
- The data is manually maintained or generated as literals. Any stale value, typo in a symbol, or mismatched description propagates to many protocol errors and tests because consumers trust this module as authoritative.
- Descriptions contain Windows format placeholders such as `%hs`, `%p`, `%08lx`, and `%1`. They are stored as display text, not interpolated by this module. Consumers should not apply Python string formatting to these descriptions with untrusted or mismatched arguments.
- The module exposes mutable globals. A consumer could modify `ERROR_MESSAGES` at runtime, changing error formatting process-wide.
- The top comment says all files should ideally use this table, but some modules still define or use local status constants. That creates drift risk when local constants disagree with `nt_errors.py`.
- Since constants are plain integers, accidental comparison between unrelated error domains is possible. Integration code that handles HRESULT, Win32 system errors, MAPI errors, and NTSTATUS values must choose the correct lookup table.

## Test Signals

Useful tests for this chunk should verify:

- importing `impacket.nt_errors` succeeds without side effects or required dependencies;
- `ERROR_MESSAGES[0x00000000]` returns `("STATUS_SUCCESS", "The operation completed successfully.")`;
- common exception-formatting paths render known names such as `STATUS_ACCESS_DENIED`, `STATUS_LOGON_FAILURE`, `STATUS_MORE_ENTRIES`, and `STATUS_NO_MORE_FILES`;
- duplicate-key behavior remains understood, especially `0x00000080` resolving to `STATUS_ABANDONED_WAIT_0` in `ERROR_MESSAGES`;
- constants used by relay/server code, including `STATUS_SUCCESS`, `STATUS_ACCESS_DENIED`, and `STATUS_PENDING`, match their NTSTATUS numeric values;
- SMB, SMB connection, DCE/RPC, Kerberos, and ntlmrelayx tests continue to pass when asserting status names or comparing imported constants.

Because this chunk is data-only, high-value regression coverage is mostly import checks, dictionary lookups, numeric equality checks, and downstream tests that exercise exception string formatting.
