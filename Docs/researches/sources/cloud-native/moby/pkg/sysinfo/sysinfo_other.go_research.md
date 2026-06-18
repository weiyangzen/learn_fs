# sources/cloud-native/moby/pkg/sysinfo/sysinfo_other.go

Purpose: non-Linux fallback for sysinfo.

APIs and flow: `New` ignores options and returns an empty `SysInfo`; `isCpusetListAvailable` always returns false with no error.

State and dependencies: no imports, filesystem access, or persistence.

Integration points: keeps packages compiling on non-Linux platforms while making Linux-specific capability detection unavailable.

Risks and tests: consumers must treat empty fields as unsupported/unknown on non-Linux. Linux-specific tests do not run for this build-tagged file.
