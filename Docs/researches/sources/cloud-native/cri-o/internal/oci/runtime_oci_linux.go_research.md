# sources/cloud-native/cri-o/internal/oci/runtime_oci_linux.go

## Purpose
Linux-specific OCI runtime helpers for port forwarding into a container network namespace and cgroup-FD process placement for exec commands.

## Important APIs and Control Flow
`PortForwardContainer` enters `netNsPath` with CNI `ns.WithNetNSPath`, dials `localhost:<port>` with Happy Eyeballs fallback disabled, copies bytes bidirectionally between the client stream and namespace TCP connection, handles context cancellation, and gives the second copy direction one second to finish. `setSysProcAttr` sets `UseCgroupFD` and `CgroupFD` on an `exec.Cmd`.

## Integration, Risks, and Tests
Called through `Runtime.PortForwardContainer` for OCI and delegated by pod runtime. Risks include namespace entry failures, half-closed stream behavior, localhost IPv4/IPv6 ordering, and goroutine copy errors. No dedicated tests in this subset.
