## sources/control-plane/longhorn-engine/pkg/util/util.go

### Purpose
`util.go` collects general Longhorn engine helpers for address parsing, HTTP logging filtering, device node duplication/removal, volume name validation, file allocation statistics, label parsing, backup URL handling, backing file resolution, data-server address selection, and ID generation.

### Important APIs, Types, And Functions
Address helpers include `ParseAddresses`, `GetGRPCAddress`, `GetPortFromAddress`, and `GetAddresses`. Generic helpers include `Filter`, `Now`, `UUID`, and `RandomID`. HTTP handling is implemented by `FilteredLoggingHandler` and `filteredLoggingHandler.ServeHTTP`. Device helpers are `DuplicateDevice`, private `mknod`, `RemoveDevice`, `removeAsync`, and `remove`. File helpers are `GetFileActualSize`, `GetHeadFileModifyTimeAndSize`, and `ResolveBackingFilepath`. Validation and parsing helpers include `ValidVolumeName`, `Volume2ISCSIName`, `ParseLabels`, `UnescapeURL`, and `CheckBackupType`.

### Control Flow
`ParseAddresses` requires a host:port and derives control, data, and sync addresses by incrementing ports. `GetAddresses` switches between TCP and UNIX data-server protocols, using a host-mounted socket path for UNIX while still returning control and sync addresses. `FilteredLoggingHandler` bypasses combined logging for configured GET paths. Device removal runs asynchronously with a 30-second timeout to avoid hanging callers. `ResolveBackingFilepath` returns a path directly for files, or requires a directory to contain exactly one non-directory file.

### State, Persistence, And Dependencies
The file manipulates OS device nodes and reads file stat allocation data but stores no internal state. It depends on `net`, `http`, `url`, `os`, `syscall`, `unix`, gorilla handlers, logrus, Google UUIDs, and local `types`.

### Integration Points
Engine startup, frontend setup, backup restore, replica file accounting, CLI parsing, and HTTP servers use these helpers. `ParseLabels` integrates with Kubernetes-style validation from `validation.go`.

### Risks
`ParseAddresses` ignores `Atoi` errors after `SplitHostPort`, so malformed numeric ports can turn into zero-derived ports. Device major/minor calculation is Linux-specific. `remove` can leave a still-running goroutine if `os.Remove` blocks beyond the timeout. `UnescapeURL` only replaces the first escaped ampersand form of each pattern. `RandomID` assumes UUID string length is sufficient and uses a typoed constant name `randomIDLenth`.

### Test Signals
Existing tests cover label parsing, backing file resolution, and shared timeouts. Additional focused tests should cover address parsing invalid ports, UNIX socket address output, filtered logging behavior, device removal timeout with fakes, actual-size stat behavior, and URL unescaping edge cases.
