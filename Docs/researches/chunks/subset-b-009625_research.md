# `sources/user-network-fs/impacket/impacket/hresult_errors.py` lines 1-2196

## Purpose

This chunk begins Impacket's shared HRESULT lookup table. The module header identifies the data as HRESULT errors from Microsoft `[MS-ERREF]` and notes the intended direction that protocol modules should centralize HRESULT decoding through this file. Lines 1-2196 define the start of one module-level constant, `ERROR_MESSAGES`, mapping integer HRESULT values to `(symbolic_name, human_message)` tuples.

The chunk is data-only. It contains no classes, functions, imports, branching logic, I/O, or runtime initialization beyond constructing the Python dictionary at import time. The covered range starts at the copyright/header block and line 19 dictionary assignment, then includes 2,177 HRESULT entries through `0xC00D11DF` / `NS_E_WMP_MULTIPLE_ERROR_IN_PLAYLIST`. The dictionary continues after this chunk, so this research note covers only the first slice of the table.

## Important APIs, Types, and Data Shape

`ERROR_MESSAGES` is the only API in this chunk. Its contract is:

```python
ERROR_MESSAGES = {
    0xHRESULT: ("ERROR_SYMBOL", "Human-readable explanation"),
}
```

Consumers use integer dictionary lookups and then index tuple element `0` for the short symbolic name and tuple element `1` for the verbose description. The data is keyed by Python integers written as hexadecimal literals, not strings. Messages are plain strings and sometimes preserve Windows placeholder syntax such as `%1`, `%2`, `%s`, `%d`, and formatting details from the source specifications.

The table is broad rather than protocol-specific. This chunk includes success, informational, warning, and failure HRESULT families, including:

- Structured storage, OLE, COM, DCOM, RPC, Dispatch, type library, clipboard, moniker, cache, event, scheduler, transaction, and COM+ results.
- Security and crypto families such as SSPI/Kerberos-adjacent `SEC_*`, CryptoAPI `CRYPT_*`, certificate/trust `CERT_*` and `TRUST_*`, smart card `SCARD_*`, TPM/TBS/TPMAPI, and ASN.1/OSS errors.
- Windows subsystem families for filter manager, graphics/display, Performance Logs and Alerts, BitLocker/FVE, Windows Filtering Platform, NDIS, distributed link tracking, and auditing.
- Windows Media/NetShow `NS_*` and `NS_E_WMP_*` errors, which dominate the end of the chunk and continue past line 2196.

## Control Flow

There is no explicit control flow in the chunk. Importing the module evaluates the dictionary literal once and binds it to `ERROR_MESSAGES`. All later behavior is driven by external consumers checking membership in the dictionary and formatting errors from tuple values.

The main implicit flow is lookup-oriented:

1. A protocol layer receives or constructs a numeric HRESULT/status value.
2. It checks `if code in hresult_errors.ERROR_MESSAGES`.
3. It extracts `ERROR_MESSAGES[code][0]` and `ERROR_MESSAGES[code][1]`.
4. It formats a `SessionError` or logging message with the symbolic and verbose text.

Unknown codes are not handled by this file; callers decide their own fallback text.

## State and Persistence Behavior

The chunk creates process-local immutable-by-convention module state. `ERROR_MESSAGES` is a mutable dictionary, but this file never mutates it after construction and performs no persistence. There is no disk, network, registry, database, environment, or cache interaction. Because the table is built at import time, its runtime cost is proportional to importing and allocating the large dictionary, and its memory footprint is always paid by processes importing `impacket.hresult_errors`.

The data is deterministic and has no dependency on platform state. A consumer can safely use it offline and in tests without a Windows host.

## Dependencies

This chunk has no imports and no third-party dependencies. The only external dependency is semantic: the table mirrors Microsoft HRESULT names and descriptions from `[MS-ERREF]`. Since the module does not generate or validate these entries dynamically, correctness depends on the literal table staying synchronized with the upstream specification and with any protocol modules that expect a given HRESULT to be present.

Sibling modules use the same pattern for other error namespaces, including `nt_errors.py`, `system_errors.py`, and `mapi_constants.py`. Those files are separate dictionaries rather than dependencies of this file.

## Integration Points

Several Impacket DCE/RPC and DCOM modules import this table directly for exception rendering. Local references show direct use in modules such as:

- `impacket/dcerpc/v5/tsch.py`, `atsvc.py`, `sasec.py`, `gkdi.py`, `drsuapi.py`, `iphlp.py`, `nspi.py`, `oxabref.py`, and `icpr.py`.
- DCOM modules including `dcomrt.py`, `dcom/wmi.py`, `dcom/oaut.py`, `dcom/scmp.py`, `dcom/vds.py`, and `dcom/comev.py`.
- `impacket/dcerpc/v5/rpcrt.py`, which checks `hresult_errors.ERROR_MESSAGES` while decoding RPC status/fault values.

The integration contract is narrow but widely shared: entries must remain indexed by exact integer HRESULT and values must remain two-element tuples. If the tuple shape changes, many `SessionError.__str__` implementations that do `ERROR_MESSAGES[key][0]` and `[1]` would break.

## Risks and Edge Cases

- Coverage gaps produce weaker diagnostics. Unknown HRESULTs fall through to caller-specific generic formatting, so missing or incorrect entries reduce operator clarity rather than usually breaking protocol behavior.
- The table includes both success/informational values and failures. Callers should not infer failure solely from presence in this dictionary; the high bits of the HRESULT or protocol semantics must still drive success/error decisions.
- Some messages include Windows formatting placeholders. Callers currently display them literally; adding interpolation would require knowing the original parameter context and could introduce formatting errors.
- The dictionary is mutable and globally shared. Accidental runtime mutation by another module would affect all later error formatting in the process.
- Literal transcription errors are plausible in a file this large. A wrong integer key can silently map an HRESULT to the wrong message, while duplicate keys later in the full dictionary would overwrite earlier entries at import time.
- Chunk boundary risk: line 2196 ends in the middle of the full `ERROR_MESSAGES` literal, immediately before additional Windows Media entries. A final per-file report must reconcile this chunk with later chunks before drawing whole-file conclusions.

## Test Signals

Useful checks for this chunk are mostly structural and integration-focused:

- Import or compile the module to catch malformed dictionary syntax in the full file, since this chunk alone does not include the dictionary close.
- Assert representative lookups from this range, for example `0x80004005 -> E_FAIL`, `0x80070005 -> E_ACCESSDENIED`, `0x8009030C -> SEC_E_LOGON_DENIED`, `0x8010002E -> SCARD_E_NO_READERS_AVAILABLE`, `0x80310000 -> FVE_E_LOCKED_VOLUME`, and `0xC00D11DF -> NS_E_WMP_MULTIPLE_ERROR_IN_PLAYLIST`.
- Exercise a consumer `SessionError` path from modules such as `tsch`, `dcomrt`, or `rpcrt` and verify the formatted string includes the symbolic HRESULT name.
- Add a shape invariant test that all covered entries are `int -> tuple[str, str]` with tuple length two.
- For synchronization work against `[MS-ERREF]`, compare keys and symbols rather than verbose text only, because message wording can be long and placeholder-heavy.
