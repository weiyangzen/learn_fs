# sources/distributed-fs/openafs/src/sys/pioctl_nt.c

## Purpose
`pioctl_nt.c` implements Windows `pioctl` and `pioctl_utf8` by translating Unix-style ViceIoctl calls into SMB redirector or AFS redirector ioctl file transactions. It locates an AFS ioctl path, marshals opcode/path/input data, sends it to the cache manager, and copies output data back to the caller.

## Important APIs, types, and functions
Important helpers include `CMtoUNIXerror`, `InitFSRequest`, `IoctlDebug`, `RDR_Ready`, `DisableServiceManagerCheck`, `GetServiceStatus`, `UnicodeToANSI`, `GetLSAPrincipalName`, `DriveSubstitution`, `DriveIsMappedToAFS`, `DriveIsGlobalAutoMapped`, `GetIoctlHandle`, `Transceive`, `MarshallLong`, `UnmarshallLong`, `MarshallString`, `fs_GetFullPath`, `pioctl_int`, `pioctl_utf8`, and `pioctl`.

## Control flow
`pioctl`/`pioctl_utf8` delegate to `pioctl_int`. For mountpoint and symlink creation in Freelance root paths, `pioctl_int` may rewrite UNC paths through `\afs\all`. It obtains an ioctl handle with `GetIoctlHandle`, marshals opcode, normalized full path, optional UTF-8 marker, and input bytes into an `fs_ioctlRequest_t`, calls `Transceive`, unmarshals the cache-manager return code, maps CM errors to errno, and copies output bytes. `GetIoctlHandle` verifies service/redirector readiness, resolves NetBIOS name, drive mappings, SUBST drives, UNC paths, global automaps, and may establish SMB connections with Explorer, LSA Kerberos, or SAM-compatible usernames before opening the hidden ioctl file.

## State and persistence behavior
The file reads Windows registry settings under OpenAFS client keys, service status, drive mappings, current directory, LSA Kerberos ticket cache, and network resources. It can establish SMB connections with `WNetAddConnection2`. Its primary persistent effect is cache-manager pioctl state mutation based on opcode.

## Dependencies and integration points
It integrates with Windows Win32 APIs, Service Control Manager, registry, LSA/Kerberos package APIs, Network Provider APIs, OpenAFS redirector structures and ioctl numbers, SMB ioctl filenames, lana helper code, and cache-manager error definitions.

## Risks
The code contains many fixed-size `char` buffers and unbounded `sprintf`/`strcat` paths; long UNC paths, NetBIOS names, or current directories can overflow or truncate. `fs_GetFullPath` temporarily changes process current directory, which is process-global and unsafe for multithreaded callers. Authentication retry logic is complex and may leak environment-specific behavior. `follow` is accepted but not visibly marshalled. Error mapping is lossy and uses several hack errno values.

## Test signals
Test local drive mappings, UNC `\afs\all`, Freelance root mountpoint/symlink creation, SUBST drives, global automaps, redirector-ready and SMB fallback modes, disabled service-manager checks, registry debug toggles, UTF-8 paths, long paths, sharing-violation retry, and CM error-to-errno mappings.
