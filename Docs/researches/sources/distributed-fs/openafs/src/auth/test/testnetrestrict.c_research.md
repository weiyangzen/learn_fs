# sources/distributed-fs/openafs/src/auth/test/testnetrestrict.c

## Purpose
Standalone test harness for NetInfo and NetRestrict parsing, using a file-backed fake interface list.

## Important APIs, Types, and Functions
Provides its own `rx_getAllAddrMaskMtu` implementation, then calls `afsconf_ParseNetInfoFile`, `afsconf_ParseNetRestrictFile`, and `afsconf_ParseNetFiles`.

## Control Flow
`main` expects three files: interface list, NetInfo, and NetRestrict. It parses each path, prints return values/reasons, and dumps final address/mask/MTU arrays in host-readable hex/decimal form.

## State and Persistence
All state is local process memory. Persistent inputs are the three text files. It does not write output except stdout/stderr.

## Dependencies and Integration Points
Links with auth/cellconfig code and uses `arpa/inet.h` conversions. The fake `rx_getAllAddrMaskMtu` lets the auth parser run without real kernel interface discovery.

## Risks and Test Signals
The interface-list parser uses simple integer scanning and does not validate octet ranges. It is a diagnostic tool, not a pass/fail suite. Useful signals are parser return codes, reason strings, and expected final address sets for crafted NetInfo/NetRestrict cases.
