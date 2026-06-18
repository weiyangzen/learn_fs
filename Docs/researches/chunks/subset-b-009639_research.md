# sources/user-network-fs/impacket/impacket/system_errors.py lines 1-2124

## Scope

This chunk covers the first 2,124 lines of `impacket/system_errors.py`. It starts the module header and the top-level `ERROR_MESSAGES` mapping, then continues through the first 2,105 entries of that mapping. The full source file continues beyond this chunk: the dictionary closes later at line 2771, and the module then exports one numeric constant per Windows system error code from line 2776 onward.

The assigned range ends inside the `ERROR_MESSAGES` literal at `0x000021c0` (`ERROR_DS_DISALLOWED_NC_REDIRECT`). The next line begins additional directory service and later DNS errors, so this chunk must be merged with later chunks before any final per-file conclusion about complete coverage.

## Purpose

`system_errors.py` is Impacket's central catalog for Win32/System error codes from Microsoft MS-ERREF. The header explicitly describes it as the shared source that other files should use for system error names and messages.

Within this chunk, the module provides integer error code lookup data for common Windows API, filesystem, network, service control, RPC, printer, WINS, PeerDist, WMI, cluster, transaction, Terminal Services, File Replication Service, and Active Directory/Directory Service conditions. Each entry maps a numeric error code to a tuple containing:

- the symbolic Windows error name, such as `ERROR_ACCESS_DENIED` or `RPC_S_SERVER_UNAVAILABLE`
- the human-readable message string used in exception formatting and diagnostics

The chunk starts at `ERROR_SUCCESS` (`0x00000000`) and reaches `ERROR_DS_DISALLOWED_NC_REDIRECT` (`0x000021c0`). The entries are ordered by ascending integer code, with gaps where MS-ERREF has no value or this generated table intentionally omits one.

## Important APIs, Types, And Data

The main data structure in this chunk is:

```python
ERROR_MESSAGES = {
    0x00000000: ("ERROR_SUCCESS", "The operation completed successfully."),
    ...
}
```

Important properties of this structure:

- Keys are Python integers written as fixed-width hexadecimal literals.
- Values are two-element tuples of strings: `(symbolic_name, verbose_message)`.
- The table is defined at import time and is globally mutable because it is an ordinary dictionary, although local code treats it as a constant.
- This chunk contributes 2,105 entries to the full mapping, covering codes from `0x0` through `0x21c0`.
- Names are not exported as individual constants in this assigned range; the separate `ERROR_FOO = 0x...` constant block starts after the dictionary in a later part of the file.

Representative groups covered by this range include:

- Basic DOS/Win32 filesystem and process errors: `ERROR_FILE_NOT_FOUND`, `ERROR_PATH_NOT_FOUND`, `ERROR_ACCESS_DENIED`, `ERROR_INVALID_HANDLE`, `ERROR_SHARING_VIOLATION`, `ERROR_MORE_DATA`.
- Network and logon errors: `ERROR_BAD_NETPATH`, `ERROR_NETNAME_DELETED`, `ERROR_NO_LOGON_SERVERS`, `ERROR_LOGON_FAILURE`, account and SID validation failures.
- Service Control Manager errors: `ERROR_SERVICE_DOES_NOT_EXIST`, `ERROR_SERVICE_DISABLED`, `ERROR_SERVICE_MARKED_FOR_DELETE`.
- Registry, tape/media, device, printer, and spooler errors.
- RPC and endpoint mapper errors: `RPC_S_INVALID_STRING_BINDING`, `RPC_S_SERVER_UNAVAILABLE`, `EPT_S_NOT_REGISTERED`, `RPC_X_BAD_STUB_DATA`.
- WINS, PeerDist, WMI, app container, media library, remote storage, reparse point, secure boot, and offload errors.
- Cluster service errors and Transactional NTFS/KTM errors.
- Terminal Services/RDP context errors.
- File Replication Service errors.
- The beginning and majority of Active Directory/Directory Service errors, including schema, naming, replication, FSMO, SPN, search, audit, and domain rename states.

## Control Flow

There are no functions, classes, conditionals, loops, imports, or runtime branching in this chunk. Importing the module executes the dictionary literal construction. All control flow happens in consumers that import this module and perform dictionary lookups.

The lookup pattern across Impacket is typically:

```python
if key in system_errors.ERROR_MESSAGES:
    error_msg_short = system_errors.ERROR_MESSAGES[key][0]
    error_msg_verbose = system_errors.ERROR_MESSAGES[key][1]
```

Several DCE/RPC modules use this pattern inside `DCERPCSessionError.__str__` implementations. Some consumers first check HRESULT or NTSTATUS tables, then fall back to `system_errors.ERROR_MESSAGES`, sometimes masking an HRESULT with `key & 0xffff` to obtain the embedded Win32 code.

This means the effective control-flow contract for this chunk is simple and data-driven: if an integer code is present, exception formatting can produce stable symbolic and verbose text; if absent, the caller normally emits an "unknown error code" path or checks another error table.

## State And Persistence Behavior

The chunk creates only in-process module state:

- `ERROR_MESSAGES` is allocated when `impacket.system_errors` is imported.
- There is no file, registry, network, cache, database, or credential persistence.
- The mapping is process-local and survives for the lifetime of the Python interpreter/module cache.
- Because it is mutable, accidental edits by runtime code would affect all later consumers in the same process. The observed codebase uses it read-only.

The messages are static source data copied from the error reference. They are not localized at runtime and do not query Windows APIs such as `FormatMessage`.

## Dependencies And Integration Points

This chunk has no direct imports. Its dependency is conceptual rather than executable: the entries must match MS-ERREF/Win32 system error semantics.

Integration points found elsewhere in the Impacket tree include:

- `impacket/dcerpc/v5/rprn.py`, `wkst.py`, `rrp.py`, `scmr.py`, `srvs.py`, `even6.py`, `dssp.py`, `bkrp.py`, `raa.py`, `rpch.py`, `nrpc.py`, and similar protocol modules import `system_errors` to format DCE/RPC exceptions.
- `impacket/dcerpc/v5/dhcpm.py` uses `system_errors.ERROR_MESSAGES` in combination with DHCP-specific messages and also uses constants such as `ERROR_MORE_DATA` from the later constant block to drive pagination loops.
- `impacket/dcerpc/v5/drsuapi.py` and `tsch.py` use the low 16 bits of a returned code (`key & 0xffff`) to resolve embedded system errors after checking HRESULT messages.
- Example tools such as `examples/reg.py`, `examples/regsecrets.py`, and `examples/secretsdump.py` import system error constants or use `ERROR_MESSAGES` to produce user-visible diagnostics.
- `impacket/smbserver.py` imports constants such as `ERROR_INVALID_LEVEL` from the later half of this same module.

For the lines in this chunk specifically, the message mapping matters most for exception text. The individual constant names mentioned in this chunk are not bound until the later constant block, so a consumer doing `from impacket.system_errors import ERROR_MORE_DATA` depends on another chunk of this file, not on lines 1-2124 alone.

## Risks And Edge Cases

Important maintenance risks in this chunk:

- The data is hand-maintained or generated static source. A typo in a key, symbolic name, or message will silently produce misleading diagnostics rather than a runtime error.
- Missing codes are indistinguishable from intentionally unsupported codes to consumers; most callers simply report an unknown error.
- Some messages include Windows insertion placeholders such as `%1`, `%2`, `%s`, and URLs. Impacket returns them verbatim rather than performing Windows message formatting.
- The dictionary is mutable. Any runtime mutation changes process-wide error formatting and could create hard-to-track diagnostics differences.
- The table contains protocol-specific ranges adjacent to each other. Adding or sorting entries manually can accidentally place a code in the wrong range or duplicate a code; Python would keep only the last duplicate key in the literal.
- This chunk ends mid-dictionary. A syntax or merge error around chunk boundaries would prevent importing the entire module, not just later entries.
- Consumers that mask HRESULTs to 16 bits rely on the system error code being present in this table. If a relevant low-word code is missing or incorrectly named, DRSUAPI/Task Scheduler-style exceptions degrade to generic output.

Potential correctness checks should focus on the table as data, not on algorithmic behavior.

## Test Signals

Useful test signals for this chunk include:

- Import smoke test: `python -c "from impacket import system_errors; print(system_errors.ERROR_MESSAGES[5])"` should import without syntax errors and return the `ERROR_ACCESS_DENIED` tuple.
- Shape invariant: every entry in `ERROR_MESSAGES` should have an integer key and a two-string tuple value.
- Known-value checks for high-traffic codes used by Impacket callers, including `0x00000005` (`ERROR_ACCESS_DENIED`), `0x0000007a` (`ERROR_INSUFFICIENT_BUFFER`), `0x000000ea` (`ERROR_MORE_DATA`), `0x000006ba` (`RPC_S_SERVER_UNAVAILABLE`), `0x0000052e` (`ERROR_LOGON_FAILURE`), and `0x0000203a` (`ERROR_DS_SERVER_DOWN`).
- Consumer formatting tests can instantiate or trigger DCE/RPC session errors in modules that use `system_errors.ERROR_MESSAGES` and assert that known system codes produce symbolic plus verbose output.
- Static validation against MS-ERREF or a generated authoritative source would catch stale, missing, duplicated, or mistranscribed codes.
- Because the module later exports numeric constants mirroring these names, a full-file reconciliation test should verify that each constant value agrees with the corresponding `ERROR_MESSAGES` key once all chunks are merged.
