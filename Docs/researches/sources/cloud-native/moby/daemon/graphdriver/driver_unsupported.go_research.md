# sources/cloud-native/moby/daemon/graphdriver/driver_unsupported.go

Purpose: priority declaration for platforms that are not Linux, Windows, or FreeBSD.

Important APIs and control flow: under build tag `!linux && !windows && !freebsd`, defines `priority = "unsupported"`. `graphdriver.New` will try a driver named `unsupported` first, then fall back to any registered drivers if present.

State, dependencies, and risks: no state is managed here. The integration point is compile-time platform selection, ensuring the package has a `priority` variable everywhere. Unsupported platforms typically lack concrete driver registrations, so selection should fail with "no supported storage driver found." Build coverage is the primary test signal.
