# sources/distributed-fs/openafs/src/WINNT/afsrdr/common/AFSProvider.h

## Purpose
Defines user/kernel IOCTL and packed data contracts for the OpenAFS Windows network provider interface, including adding, cancelling, querying, listing, and inspecting redirector connections.

## Important APIs, Types, And Functions
Defines `AFS_RDR_DEVICE_NAME`, provider IOCTLs `IOCTL_AFS_ADD_CONNECTION`, `IOCTL_AFS_CANCEL_CONNECTION`, `IOCTL_AFS_GET_CONNECTION`, `IOCTL_AFS_LIST_CONNECTIONS`, and `IOCTL_AFS_GET_CONNECTION_INFORMATION`, plus `AFS_NETWORKPROVIDER_INTERFACE_VERSION_1`. Packed structs are `AFSNetworkProviderConnectionCB` and `AFSCancelConnectionResultCB`.

## Control Flow
Provider code opens the redirector device and sends buffered IOCTLs. Enumeration uses `CurrentIndex`; cancel returns status and local drive name.

## State And Persistence
No header state. IOCTLs affect redirector provider connection lists, local drive mappings, authentication IDs, comments, remaining path, and remote names.

## Dependencies And Integration Points
Depends on Windows `CTL_CODE`, filesystem device type constants, `LARGE_INTEGER`, and `WCHAR`. Integrates network provider DLL/service code with kernel redirector connection management.

## Risks
Packed variable-length structs require strict offset/length validation. `LocalName` plus `RemoteName[1]` is flexible-array style and can overrun if buffer sizes are wrong. Version fields must be checked.

## Test Signals
Map/unmap/list connections, validate enumeration indexes, long remote/comment strings, authentication ID propagation, and malformed buffer rejection.
