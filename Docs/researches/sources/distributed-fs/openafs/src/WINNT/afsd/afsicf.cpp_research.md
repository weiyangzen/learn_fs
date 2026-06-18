# sources/distributed-fs/openafs/src/WINNT/afsd/afsicf.cpp

## Purpose

`afsicf.cpp` configures Windows Firewall exceptions for OpenAFS client and server ports. It supports modern `INetFwPolicy2` rule-based configuration and falls back to older `INetFwProfile` globally-open-port APIs.

## Important APIs, Types, and Functions

- `global_afs_port_t` describes an AFS port rule: display name, numeric port, string port, and protocol.
- `afs_clientPorts` defaults to callback port 7001 UDP and optionally TCP.
- `afs_serverPorts` lists AFS server ports 7000 through 7009 for file, protection, VLDB, auth, volume, error, bos, update, and remote cache manager services, with optional TCP variants under `AFS_TCP`.
- `icf_CheckAndAddPorts2()` uses `INetFwPolicy2`, `INetFwRules`, and `INetFwRule` to add or update application-scoped allow rules grouped as `OpenAFS Firewall Rules`.
- `icf_OpenFirewallProfile()` opens the legacy current firewall profile through `INetFwMgr` and `INetFwPolicy`.
- `icf_CheckAndAddPorts()` uses legacy `INetFwOpenPorts` and `INetFwOpenPort` to enable or create globally open ports.
- `icf_CheckAndAddAFSPorts(int port)` is the exported C-callable entry point. `AFS_PORTSET_SERVER` selects server ports; other values configure the client callback port.
- A `TESTMAIN` block provides standalone manual testing.

## Control Flow

`icf_CheckAndAddAFSPorts()` chooses server or client port descriptors, initializes COM, tries `icf_CheckAndAddPorts2()`, and falls back to `icf_OpenFirewallProfile()` plus `icf_CheckAndAddPorts()` if the policy2 path fails. Return codes are coarse: `0` on accepted path, `1` invalid client port formatting, `2` legacy profile unavailable, and `3` legacy port creation failure.

For policy2, each port is looked up by rule name. Missing rules are created, associated with the current executable path, configured for protocol/local port/all profiles/allow/enabled/edge traversal/all interface types, and grouped. Existing rules have service name cleared, application, edge traversal, interface types, protocol, local ports, grouping, and action refreshed.

## State and Persistence Behavior

The persistent state is Windows Firewall configuration. The code creates or updates named allow rules or globally open ports. In non-test builds the application path comes from `GetModuleFileNameW(NULL, ...)`, tying rules to the installed executable. Client callback port state mutates the global `afs_clientPorts[0]` descriptor for the duration of the call.

## Dependencies and Integration Points

The file depends on Windows COM, `netfw.h`, BSTR allocation, `OutputDebugString`, and the public `afsicf.h` declaration. It is used by service/install code that needs firewall holes for the cache manager callback or server suite.

## Risks

- `icf_CheckAndAddPorts2()` unconditionally returns `0`, so failures from COM/rule operations are hidden and fallback is usually not triggered.
- `icf_CheckAndAddPorts2()` calls `CoUninitialize()` based on a local `hrComInit` that is never assigned from `CoInitializeEx()` in that function; COM lifetime is actually handled by the caller, so this can unbalance COM initialization.
- `pFwRule` is reused in a loop and only released once at cleanup, so existing per-port rule references can leak or be overwritten.
- `icf_CheckAndAddPorts()` releases `fwPorts` before `cleanup`, then may release it again because the pointer is not nulled.
- For client ports, `afs_clientPorts[0].str_port` is set to a stack buffer. It is safe only because the descriptor is consumed synchronously before return.
- Enabling edge traversal and all interface types broadens firewall exposure and should be validated against deployment expectations.

## Test Signals

- Tests should mock or integration-test both Policy2 and legacy firewall APIs, including forced Policy2 failure to prove fallback.
- Verify idempotence: running twice should update existing rules without duplicates.
- Validate non-default callback ports, server portset behavior, optional `AFS_TCP`, and returned error codes on COM/firewall failures.
- Static analysis should flag COM lifetime imbalance and double-release risks.
