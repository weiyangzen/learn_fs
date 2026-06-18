# sources/distributed-fs/beegfs/client_module/source/common/toolkit/NicAddressFilter.h

## Purpose
Declares the NIC-address filter interface used to accept, reject, and rank network interfaces.

## Important APIs and types
The implementation type `NicAddressFilter` is forward-declared. Public functions are `NicAddressFilter_construct`, `NicAddressFilter_destruct`, `NicAddressFilter_isAllowed`, `NicAddressFilter_getPosition`, and `NicAddressFilter_getNumFilterEntries`. Inputs are `StrCpyList` configuration rows and `NicAddress` candidates.

## State, dependencies, integration
The header depends on BeeGFS `NicAddress` and `Common` definitions. It hides the parsed entry layout, keeping callers focused on boolean allow and ordered position semantics.

## Risks and test signals
Callers must handle a `NULL` construct result for invalid configuration or allocation failure. Because `getPosition` returns `SIZE_MAX` both for no match and explicit denial, tests should assert caller handling of denied interfaces does not treat them as lowest-priority accepted NICs.
