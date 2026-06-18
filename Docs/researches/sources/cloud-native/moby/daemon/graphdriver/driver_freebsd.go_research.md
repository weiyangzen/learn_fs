# sources/cloud-native/moby/daemon/graphdriver/driver_freebsd.go

Purpose: FreeBSD graphdriver priority declaration.

Important APIs and control flow: defines package variable `priority = "zfs"`, which `graphdriver.New` splits and uses for prior-driver preference and automatic selection.

State, dependencies, and risks: there is no runtime logic beyond influencing driver selection. On FreeBSD, automatic graphdriver choice prefers ZFS and there is no fallback list in this file. The behavior depends on the ZFS driver being registered and supported at runtime; if not, `New` falls through to any registered drivers via map iteration. Test signal is platform build/driver initialization rather than direct unit tests.
