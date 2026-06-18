# sources/cloud-native/containers-storage/pkg/parsers/operatingsystem/operatingsystem_solaris.go

Purpose: implements Solaris OS name and zone/container detection.

Important APIs, types, and functions: package variable `etcOsRelease`, `GetOperatingSystem`, and `IsContainerized`.

Control flow: `GetOperatingSystem` reads `/etc/release`, returns the first trimmed line, or errors if no newline is found. `IsContainerized` calls `getzoneid` and treats any nonzero zone id as containerized.

State and persistence: reads OS release file and current zone id; no mutation.

Dependencies and integration points: depends on cgo `zone.h`, `bytes`, `errors`, and `os`. Selected for `solaris && cgo`.

Risks and edge cases: cgo required. A release file without newline returns an error even if content exists. Containerization is Solaris-zone-specific.

Test signals: no Solaris tests in the requested set.
