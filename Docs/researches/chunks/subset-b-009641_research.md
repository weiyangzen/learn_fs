# sources/user-network-fs/impacket/impacket/system_errors.py lines 4900-5526

## Scope

This chunk covers the final block of `system_errors.py`, from `DNS_ERROR_KEYMASTER_REQUIRED` through `STORE_ERROR_UNLICENSED_USER`. It is the tail of the module-level symbolic constants that mirror the large `ERROR_MESSAGES` dictionary defined earlier in the same file. The range starts in the DNS error-code family and then covers Winsock, IPsec/IKE, side-by-side assembly, Windows Event Log, event collector, MUI/MRM, monitor configuration, GPIO, runlevel, package deployment, app model, state repository, API availability, and Store licensing constants.

The chunk contains no classes, functions, imports, or executable logic beyond Python assignment statements evaluated at import time.

## Purpose

`system_errors.py` centralizes Windows system error values from MS-ERREF for Impacket. Earlier in the file, `ERROR_MESSAGES` maps numeric Windows error codes to `(symbol, description)` tuples for rendering RPC and protocol exceptions. The constant section gives callers stable Python names for the same numeric values, so code can compare return codes without copying integers.

This chunk extends that public constant namespace for later Windows subsystems:

- DNSSEC, DNS zone, DNS record, and DNS directory-partition errors in the `0x238d` through `0x26b2` ranges.
- Winsock and Winsock QoS errors in the `0x2714` through `0x2b19` ranges.
- IPsec policy, IKE negotiation, packet-processing, and DOS protection errors in the `0x32c8` through `0x366c` ranges.
- Side-by-side assembly and XML activation context errors in the `0x36b0` through `0x371e` ranges.
- Windows Event Log and Event Collector errors in the `0x3a98` through `0x3aed` ranges.
- Resource localization, monitor configuration, GPIO, runlevel, package deployment, app model, state-store, API, and Store licensing errors in the `0x3afc` through `0x3df6` ranges.

## Important APIs And Data

The only API surface in this range is a set of module globals. They are imported directly by callers that need symbolic constants and are also available through `impacket.system_errors` when modules import the whole namespace.

Representative constants include:

- `DNS_ERROR_DNSSEC_IS_DISABLED`, `DNS_ERROR_ZONE_DOES_NOT_EXIST`, `DNS_ERROR_RECORD_ALREADY_EXISTS`, and `DNS_ERROR_DP_FSMO_ERROR` for DNS management/status handling.
- `WSAEWOULDBLOCK`, `WSAECONNRESET`, `WSAETIMEDOUT`, `WSAHOST_NOT_FOUND`, `WSANO_DATA`, and `WSA_IPSEC_NAME_POLICY_ERROR` for socket and resolver failures.
- `ERROR_IPSEC_QM_POLICY_NOT_FOUND`, `ERROR_IPSEC_IKE_AUTH_FAIL`, `ERROR_IPSEC_IKE_NEGOTIATION_DISABLED`, `ERROR_IPSEC_BAD_SPI`, and `ERROR_IPSEC_DOSP_NOT_INSTALLED` for IPsec policy, IKE, and packet-layer reporting.
- `ERROR_SXS_MANIFEST_PARSE_ERROR`, `ERROR_SXS_XML_E_MISSINGQUOTE`, `ERROR_SXS_COMPONENT_STORE_CORRUPT`, and `ERROR_SXS_FILE_HASH_MISSING` for side-by-side assembly manifest and component-store issues.
- `ERROR_EVT_INVALID_QUERY`, `ERROR_EVT_CHANNEL_NOT_FOUND`, `ERROR_EVT_MESSAGE_NOT_FOUND`, and `ERROR_EC_CRED_NOT_FOUND` for Event Log/Event Collector protocol surfaces.
- `ERROR_MUI_INVALID_LOCALE_NAME`, `ERROR_MRM_NO_CANDIDATE`, `ERROR_MCA_UNSUPPORTED_MCCS_VERSION`, `ERROR_GPIO_OPERATION_DENIED`, `ERROR_INSTALL_PACKAGE_NOT_FOUND`, `APPMODEL_ERROR_NO_PACKAGE`, `ERROR_STATE_WRITE_SETTING_FAILED`, `ERROR_API_UNAVAILABLE`, and `STORE_ERROR_UNLICENSED_USER` for newer Windows platform subsystems.

There are no custom types. Every binding is an `int` literal written in hexadecimal to preserve visual alignment with Windows documentation.

## Control Flow

Control flow is limited to import-time execution:

1. Python evaluates the earlier `ERROR_MESSAGES` dictionary.
2. Python evaluates each constant assignment in order.
3. The module namespace then exposes both lookup table data and named integer constants to importers.

No branches, loops, error handling, lazy initialization, or runtime mutation occur in this chunk. The ordering is still meaningful for maintainability because constants follow the numeric ordering and family grouping from MS-ERREF.

## State And Persistence Behavior

The state introduced here is immutable-by-convention process memory. Each symbol is bound once when the module is imported. Python does not enforce immutability for module globals, but the file treats these names as constants and no local code mutates them.

There is no persistence, I/O, cache, environment dependency, or per-instance state. Re-imports use Python's normal module cache, so the assignments are executed once per interpreter load unless the module is explicitly reloaded.

## Dependencies And Integration Points

The constants depend semantically on Microsoft MS-ERREF numeric assignments. The file header states that `system_errors.py` is intended to be the central source for SYSTEM errors, and many Impacket DCE/RPC modules integrate through it.

Observed integration patterns include:

- RPC session exception renderers, such as `dcerpc/v5/rpch.py`, `rprn.py`, `rrp.py`, `scmr.py`, `srvs.py`, `wkst.py`, `even6.py`, and related modules, check `system_errors.ERROR_MESSAGES` to turn numeric return codes into symbolic names and descriptions.
- Some protocol modules compare direct constants from this module, for example registry and service helpers checking `ERROR_MORE_DATA`, `ERROR_INSUFFICIENT_BUFFER`, or similar system status values.
- `dcerpc/v5/drsuapi.py` and `dcerpc/v5/tsch.py` mask HRESULT-like values with `0xffff` before consulting `ERROR_MESSAGES`, so constants in this file also matter when only the low 16 bits carry a system error.
- Examples and tests, including secrets dumping paths, search rendered exception text such as `ERROR_DS_DRA_BAD_DN`, demonstrating that consistency between `ERROR_MESSAGES` and constants affects user-visible diagnostics.

This specific chunk's later subsystem constants may be used by current or future modules that bind to DNS, Event Log, IPsec, package deployment, or app model interfaces. Even when direct constant imports are absent today, the matching `ERROR_MESSAGES` entries allow exception formatting for these code ranges.

## Risks And Maintenance Notes

- Numeric drift is the primary risk. A wrong hex value can make equality checks fail silently or render an unrelated Windows error name.
- The file duplicates information in two forms: `ERROR_MESSAGES` entries and module-level constants. Additions or corrections should keep the integer-to-name mapping and the named constant aligned.
- This chunk contains only names and values, so unit tests that import the module will catch syntax errors but not semantic mismatches against MS-ERREF.
- Direct `from impacket.system_errors import NAME` users rely on these symbols remaining stable. Renaming or removing constants is a compatibility break even if `ERROR_MESSAGES` still contains the code.
- These are Win32/system error values, not NTSTATUS or HRESULT values. Callers need to use `nt_errors` or `hresult_errors` where appropriate, or apply the same masking pattern used by DRSUAPI/TSCH only when the protocol returns a wrapped system code.
- The module has no generated-code marker. Because the list is long and repetitive, manual edits are easy to misalign; review should compare against authoritative MS-ERREF ranges rather than relying on nearby visual patterns alone.

## Test Signals

Useful verification for this chunk is mostly static and integration-oriented:

- `python -m py_compile sources/user-network-fs/impacket/impacket/system_errors.py` confirms the large dictionary and constant tail remain syntactically valid.
- Import smoke tests can assert representative bindings, for example `DNS_ERROR_KEYMASTER_REQUIRED == 0x238d`, `WSAECONNRESET == 0x2746`, `ERROR_IPSEC_IKE_AUTH_FAIL == 0x35e9`, `ERROR_SXS_COMPONENT_STORE_CORRUPT == 0x3712`, `ERROR_EVT_INVALID_QUERY == 0x3a99`, and `STORE_ERROR_UNLICENSED_USER == 0x3df6`.
- Consistency tests can check that every constant in this range has the same numeric key/name pair in `ERROR_MESSAGES` where the message table includes that code.
- Existing DCE/RPC exception tests indirectly validate lookup behavior when a returned system error code is present in `ERROR_MESSAGES`; targeted tests for Event Log or DNS RPC errors would give stronger coverage for constants in this range.
- Static analysis should flag duplicate constant values only when MS-ERREF does not intentionally alias names. In this chunk, several families are contiguous ranges, so gaps are expected and should not automatically fail validation.
