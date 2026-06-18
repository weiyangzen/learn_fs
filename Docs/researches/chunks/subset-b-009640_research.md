# sources/user-network-fs/impacket/impacket/system_errors.py lines 2125-4899

## Scope

This chunk covers the tail of Impacket's `ERROR_MESSAGES` table and the first large block of module-level numeric aliases for Windows system error codes.

The assigned range starts at line 2125 inside the `ERROR_MESSAGES` dictionary with Active Directory Lightweight Directory Services/domain-join errors, continues through DNS, Winsock, IPsec, side-by-side assembly, event log, MUI, monitor configuration, package/app model/state repository, and Store licensing entries, and reaches the dictionary close at line 2771. It then resumes at line 2776 with exported integer constants beginning at `ERROR_SUCCESS = 0x00000000` and ends at line 4899 with `DNS_ERROR_RCODE_BADTIME = 0x0000233a`. Later DNS constants and later system-error families continue after this chunk.

Within this exact range there are 646 dictionary entries and 2,122 constant assignments.

## Purpose

`system_errors.py` is Impacket's local copy of Windows system error metadata from `[MS-ERREF]`. It provides two related interfaces:

- `ERROR_MESSAGES`: maps a numeric Win32/system error code to a pair of `(symbolic_name, human_readable_message)`.
- Module-level constants: expose symbolic names as integer values so protocol code and tests can compare status values without hard-coded literals.

The dictionary portion in this chunk is used to turn returned RPC/DCE/RPC and service status codes into useful exception strings. The constant portion is used by callers that need to compare protocol return values, set default pagination status, or assert expected status codes.

## Important APIs, Types, And Data

There are no functions or classes in this range. The important API surface is import-time global data:

- `ERROR_MESSAGES` entries have integer keys and 2-tuples of strings. Consumers expect index `0` to be the short symbolic name and index `1` to be the verbose message.
- The dictionary slice begins with `0x000021c1: ("ERROR_DS_HIGH_ADLDS_FFL", ...)` and ends with `0x00003df6: ("STORE_ERROR_UNLICENSED_USER", ...)`.
- Constant aliases begin at `ERROR_SUCCESS = 0x00000000` and, in this chunk, continue through `DNS_ERROR_RCODE_BADTIME = 0x0000233a`.
- The dictionary and constants intentionally duplicate names and values. For example, `ERROR_DS_HIGH_ADLDS_FFL` appears as a dictionary payload in the first half and as a numeric constant near this chunk's end.

Major error families represented in the dictionary slice include:

- Active Directory and AD LDS completion/failure codes around `0x21c1-0x21c6`.
- DNS server, DNSSEC, zone, record, update, and directory-partition status codes around `0x2329-0x26b2`.
- Winsock `WSA*` socket and resolver errors around `0x2714-0x2afc`.
- IPsec/IKE, filter, and policy negotiation errors around `0x32c8-0x3654`.
- Side-by-side activation/context/XML/manifest errors around `0x36b0-0x371d`.
- Event log and event subscription/query errors around `0x3a98-0x3abf`.
- MUI/resource-loading errors around `0x3afc-0x3b65`.
- Monitor configuration, graphics, and MCA status codes around `0x3b60-0x3b92`.
- Windows installer, package deployment, app model, state repository, and Store licensing errors around `0x3cf0-0x3df6`.

The constant slice restarts from low-numbered common system errors and reaches partway into the DNS family. It therefore overlaps earlier dictionary entries from the full file as well as the dictionary entries in this chunk.

## Control Flow

The code has only module initialization flow:

1. Python imports `impacket.system_errors`.
2. The interpreter builds the `ERROR_MESSAGES` dictionary from literal entries.
3. It binds every uppercase error-name constant to its numeric integer value.
4. Downstream modules read the dictionary or constants directly.

Exception formatting in consuming modules usually follows the same pattern: check whether a returned integer status exists in `system_errors.ERROR_MESSAGES`, pull the short and verbose strings, and interpolate them into a protocol-specific `SessionError` string. Constant consumers import names such as `ERROR_MORE_DATA`, `ERROR_NO_MORE_ITEMS`, `ERROR_INVALID_LEVEL`, or `ERROR_NOT_SUPPORTED` and compare them directly to returned status values.

## State And Persistence Behavior

This chunk creates process-local immutable-by-convention metadata. It does not perform I/O, open sockets, write files, cache runtime results, or persist anything outside the Python process.

The state risk is global mutability: `ERROR_MESSAGES` is a normal dictionary, and constants are normal module globals. Impacket code treats them as read-only, but accidental mutation after import would affect all later error formatting in the same interpreter. There is no defensive copy or frozen mapping.

Import cost is proportional to the full generated table. This range alone contributes thousands of literal objects, but lookup behavior remains constant-time dictionary access for messages and direct global-name access for constants.

## Dependencies And Integration Points

This file has no imports in the inspected range and no external runtime dependencies beyond Python's literal evaluation. Its semantic dependency is Microsoft's `[MS-ERREF]` error-code catalog; accuracy depends on keeping codes, names, and messages aligned with that source.

Observed integration points in the Impacket tree include:

- `impacket/dcerpc/v5/rprn.py`, `rpch.py`, `rrp.py`, `tsts.py`, `srvs.py`, `wkst.py`, and `dhcpm.py`: consult `system_errors.ERROR_MESSAGES` when formatting DCE/RPC service exceptions.
- `impacket/dcerpc/v5/drsuapi.py`: falls back to `system_errors.ERROR_MESSAGES[key & 0xffff]` after HRESULT lookup, making low-word correctness important for directory replication errors.
- `impacket/dcerpc/v5/rrp.py` and `dhcpm.py`: compare returned status values against constants such as `ERROR_MORE_DATA` for enumeration loops.
- `examples/reg.py`: imports `ERROR_NO_MORE_ITEMS` for registry enumeration termination.
- `impacket/smbserver.py`: imports `ERROR_INVALID_LEVEL`.
- `tests/dcerpc/test_tsch.py`: imports `ERROR_NOT_SUPPORTED` for expected scheduler behavior.

The chunk's DNS constants may also be used by callers outside the repository through the public `impacket.system_errors` module API.

## Risks And Maintenance Notes

- The table is mechanical and duplicate-heavy. A typo in either the dictionary entry or the constant alias can create confusing disagreement between formatted messages and numeric comparisons.
- Several consumers assume `ERROR_MESSAGES[key]` is exactly a 2-tuple. Changing the value shape would break exception formatting.
- `drsuapi.py` masks HRESULT-style values with `0xffff` before lookup, so low-word collisions or missing low-word system errors can produce misleading messages.
- The chunk boundary is not an API boundary. It starts inside the dictionary and ends inside the DNS constant family; whole-file conclusions must be reconciled with adjacent chunks.
- Because this module has no validation logic, duplicate values, stale messages, or missing aliases are not detected at import time.
- Messages are user-visible in exceptions. Updating from `[MS-ERREF]` can change test expectations or downstream tooling that matches exact strings.
- The dictionary is mutable at runtime. Tests or callers that monkey-patch it can affect unrelated protocol modules in the same process.

## Test Signals

Useful tests for this data should verify:

- `impacket.system_errors` imports successfully and `ERROR_MESSAGES` is populated.
- Representative dictionary entries from this chunk resolve correctly, such as `0x00002329` to `DNS_ERROR_RCODE_FORMAT_ERROR`, `0x00002746` to `WSAECONNRESET`, and `0x00003df6` to `STORE_ERROR_UNLICENSED_USER`.
- Representative constants in this chunk have the expected integer values, including `ERROR_SUCCESS == 0x00000000`, `ERROR_MORE_DATA == 0x000000ea`, `ERROR_DS_HIGH_ADLDS_FFL == 0x000021c1`, and `DNS_ERROR_RCODE_BADTIME == 0x0000233a`.
- Protocol exception classes that use `system_errors.ERROR_MESSAGES` include both symbolic and verbose strings for known system errors and fall back cleanly for unknown codes.
- Enumeration loops that compare against constants such as `ERROR_MORE_DATA` and `ERROR_NO_MORE_ITEMS` still terminate correctly.

For maintenance, a generated consistency check would be valuable: every constant name/value pair that has a corresponding `ERROR_MESSAGES` entry should agree with the dictionary's symbolic name for that numeric value, allowing for intentional aliases only when documented.
