<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/sanity_linux.go -->
# sources/cloud-native/moby/internal/testutil/netnsutils/sanity_linux.go

Purpose: asserts that a socket's network namespace matches the current thread namespace on Linux. The main API is `AssertSocketSameNetNS`. Control flow obtains a raw socket control callback, calls `unix.GetsockoptInt` with `SO_NETNS_COOKIE`, compares it to the current netns cookie obtained from `netns.Get`, and fails the test on mismatch. State is observed kernel namespace identity only. Dependencies include syscall `Conn`, `vishvananda/netns`, `unix`, and assertions. Risks include kernel support for netns cookies, raw connection access, and false failures when sockets are intentionally cross-namespace. Test signal is strong for namespace setup bugs.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/internal/testutil/netnsutils/sanity_linux.go -->
