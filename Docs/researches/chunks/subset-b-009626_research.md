# sources/user-network-fs/impacket/impacket/hresult_errors.py lines 2197-5001

## Scope

This chunk covers the latter part of Impacket's HRESULT error catalog. It starts inside the `ERROR_MESSAGES` dictionary at the Windows Media Player / Windows Media namespace error range, closes that dictionary at line 2947, and then begins the module-level `# Error Codes` constant aliases from the first HRESULT in the file through `NS_E_WMP_CONVERT_PLUGIN_UNKNOWN_FILE_OWNER`.

The range contains data definitions only: no functions, classes, imports, or executable control-flow branches beyond Python module initialization of a dictionary and integer constants. In this chunk, the source defines 750 `ERROR_MESSAGES` entries and 2,051 integer constant aliases.

## Purpose

`hresult_errors.py` centralizes HRESULT names and human-readable descriptions sourced from Microsoft's MS-ERREF catalog. Impacket uses it to turn numeric RPC/DCOM/HRESULT status values into useful exception messages while also exposing named constants for protocol stubs and callers that need symbolic HRESULT values.

Within this specific chunk, the dictionary entries mainly cover:

- Windows Media Player, media library, DRM, CD/DVD burning, sync, codec, playlist, URL, caching, and namespace failures in the `0xC00D11E0` through `0xC00D2F0B` ranges.
- Media Foundation transform, ASF parsing, streaming, proxy, device, and quality-of-service errors in the `0xC00D36xx` and related ranges.
- Windows graphics/display HRESULTs in the `0xC02620xx` through `0xC02625E0` ranges, including VidPN topology, monitor, OPM/PVP, DDC/CI, and MCA failures.

The constant section then restarts from the beginning of the full file's HRESULT catalog, exposing symbolic names such as `STG_S_CONVERTED`, COM/OLE/Task Scheduler/security success codes, many failure codes, and the early-to-mid Windows Media constants up to `NS_E_WMP_CONVERT_PLUGIN_UNKNOWN_FILE_OWNER`.

## Important APIs, Types, And Data

The primary API is the module-level `ERROR_MESSAGES` mapping:

- keys are integer HRESULT values, written as hexadecimal literals;
- values are two-tuples of `(symbolic_name, descriptive_message)`;
- callers perform direct membership tests and index lookups, for example `if key in hresult_errors.ERROR_MESSAGES`.

The second API surface is the flat set of module constants:

- each constant binds a symbolic HRESULT name to the corresponding integer value;
- the constants duplicate names already present as the first element of `ERROR_MESSAGES` entries;
- the chunk begins this alias table at `STG_S_CONVERTED = 0x00030200` and ends at `NS_E_WMP_CONVERT_PLUGIN_UNKNOWN_FILE_OWNER = 0xC00D115E`;
- later chunks continue the remaining aliases after this line.

There are no custom types. The data shape is deliberately simple so protocol modules can import either the whole `hresult_errors` module for lookup or individual constants by name.

## Control Flow

At import time Python evaluates the full dictionary literal and then evaluates each constant assignment in order. There is no runtime branching, lazy loading, normalization, or generation step in this source file.

Consumer-side control flow is outside this file but follows a common pattern:

1. Receive or decode a numeric HRESULT/status value from an RPC, DCOM, certificate, directory, or protocol response.
2. Check whether that integer is present in `hresult_errors.ERROR_MESSAGES`.
3. If present, use tuple element `0` as the short symbolic name and tuple element `1` as the verbose explanation.
4. If absent, fall back to a generic `unknown error code` message, another catalog such as `system_errors` or `mapi_constants`, or a low-word system-error lookup depending on the protocol module.

Because this chunk is split across a larger file, one boundary detail matters for reconciliation: line 2197 is not the start of `ERROR_MESSAGES`; it is a continuation of a dictionary that began at the top of the file. The dictionary itself closes in this chunk, and the constant alias table starts immediately afterward.

## State And Persistence Behavior

The module has no persistence behavior. Importing it creates process-local immutable-by-convention Python objects:

- `ERROR_MESSAGES`, a mutable dictionary that callers treat as a read-only catalog;
- many integer globals representing HRESULT constants.

No files, sockets, registry entries, caches, environment variables, or network resources are read or written by this chunk. The only durable state is the source text itself. If a consumer mutates `ERROR_MESSAGES` at runtime, that mutation is process-local and affects later lookups in the same interpreter, but the module does not intentionally provide mutation APIs.

## Dependencies And Integration Points

This file has no imports and no external runtime dependencies. Its integration points are the Impacket modules that import `hresult_errors` to format exceptions or protocol errors. Relevant examples in this source tree include:

- `impacket/dcerpc/v5/dcomrt.py`, where `DCERPCSessionError` uses `hresult_errors.ERROR_MESSAGES` for DCOM HRESULT messages.
- `impacket/dcerpc/v5/rpcrt.py`, where RPC fault/status formatting consults the HRESULT catalog when the status code matches.
- `impacket/dcerpc/v5/iphlp.py`, `gkdi.py`, `atsvc.py`, `sasec.py`, `drsuapi.py`, `tsch.py`, and `icpr.py`, which use the catalog in protocol-specific `DCERPCSessionError` implementations.
- DCOM helper modules under `impacket/dcerpc/v5/dcom/`, including `scmp.py`, `wmi.py`, `comev.py`, `vds.py`, and `oaut.py`, which use this table for COM-style error reporting.
- Exchange/MAPI-adjacent modules such as `nspi.py` and `oxabref.py`, which first try MAPI-specific messages and then fall back to HRESULT messages.

The constants are integration glue for code that needs to compare against named HRESULTs instead of magic numbers. This chunk's alias table covers storage, COM, scheduler, security, cryptography, TPM, UI, network, Windows Update, media, and early Windows Media namespaces up to the `0xC00D115E` range.

## Risks And Edge Cases

- The catalog is duplicated: each code appears once in `ERROR_MESSAGES` and again as a module constant. A manual update can accidentally change one representation without the other.
- Import cost and memory usage are proportional to the full catalog size. This is acceptable for exception formatting but should be considered if imported on hot startup paths.
- `ERROR_MESSAGES` is mutable. There is no defensive wrapper preventing accidental caller-side modification.
- The lookup contract assumes callers pass unsigned HRESULT integers matching the literal values. Signed 32-bit interpretations, low-word Win32 codes, or NTSTATUS values will not match unless the consumer normalizes them or falls back to another catalog.
- Several protocol modules use different fallback orders. For example, some check HRESULTs before system errors, while others check MAPI or low-word system errors first. A shared numeric value can therefore format differently depending on the caller.
- The chunk boundary splits the file's generated-style data: this range starts mid-dictionary and ends mid-constant table. Any final per-file report should merge this chunk with adjacent chunks before making whole-file completeness claims.
- Messages are copied from an external specification and can become stale if MS-ERREF adds, renames, or revises HRESULT descriptions.

## Test Signals

Useful validation for this chunk is mostly structural and integration-oriented:

- `python3 -m py_compile sources/user-network-fs/impacket/impacket/hresult_errors.py` should succeed, proving the large literal and constant assignments are syntactically valid.
- Importing `impacket.hresult_errors` should expose `ERROR_MESSAGES[0xC00D11E0] == ("NS_E_WMP_IMAPI2_ERASE_FAIL", ...)` and constant `NS_E_WMP_CONVERT_PLUGIN_UNKNOWN_FILE_OWNER == 0xC00D115E`.
- A consistency check can verify that each dictionary entry's symbolic name has a matching module global with the same integer value once the full file is loaded.
- Exception-formatting tests for DCOM/RPC protocol modules should assert that known HRESULTs render the symbolic short name and verbose message instead of generic unknown-error text.
- Fallback-path tests should cover an unknown HRESULT, a low-word Win32 error, and a MAPI-specific value to ensure this catalog integrates correctly with `system_errors`, `nt_errors`, and `mapi_constants`.
