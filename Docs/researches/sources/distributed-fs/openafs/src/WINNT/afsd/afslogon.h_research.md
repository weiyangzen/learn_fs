# sources/distributed-fs/openafs/src/WINNT/afsd/afslogon.h

## Purpose
`afslogon.h` declares the Windows network-provider interface and shared logon configuration structures for OpenAFS integrated logon. It centralizes registry value names, default policy values, trace/logon flag macros, length limits, exported NP entry points, debugging helpers, and AD/PAG helper prototypes used by `afslogon.c` and companion logon modules.

## Important APIs, Types, And Constants
Registry constants cover service/provider domain configuration, retry and sleep intervals, fail-silent policy, trace/debug flags, logon options, logon script, realm, username mapping, `TheseCells`, and logoff token preservation. `LogonOptions_t` carries effective policy and allocated strings for one logon. Macros classify trace (`ISLOGONTRACE`), integrated logon (`ISLOGONINTEGRATED`), and flags for remote, AD realm, and LSA credentials. Public declarations include `DllEntryPoint`, `NPGetCaps`, `NPLogonNotify`, `NPPasswordChangeNotify`, debug functions, service status helpers, `GetDomainLogonOptions`, cell/home-path lookup helpers, `AFSCreatePAG`, and `LogonSSP`.

## Control Flow And Integration
The header is consumed by the network-provider DLL implementation and AD helper code. `afslogon.c` fills `LogonOptions_t` from registry policy, passes it into token acquisition and home-path discovery, and uses the declared external helper functions to impersonate logon sessions and create auth groups.

## State, Dependencies, Risks, And Test Signals
This header has no storage besides `extern DWORD TraceOption`, but its struct contains owning pointers that callers must free consistently. It depends on Windows NPAPI, SSPI context handles, LSA/security types, and OpenAFS conventions. ABI risks include static declaration of `UnicodeStringToANSI` in a header and tight coupling to registry string names. Test signals are compile coverage across C/C++ consumers, correct struct initialization/freeing, registry value compatibility, and network-provider entry-point signature matching.
