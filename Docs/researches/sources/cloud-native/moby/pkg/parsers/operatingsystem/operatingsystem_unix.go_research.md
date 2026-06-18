<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_unix.go -->
# sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_unix.go

Purpose: generic Darwin/FreeBSD operating-system helpers. `GetOperatingSystem` returns the machine field from `uname`, while version and containerization detection return unsupported errors or false/error. State is host uname data only. Dependencies include x/sys/unix. Risks include returning machine architecture rather than marketing OS name and unsupported feature errors. Test signal is compile-time/platform coverage.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/operatingsystem_unix.go -->
