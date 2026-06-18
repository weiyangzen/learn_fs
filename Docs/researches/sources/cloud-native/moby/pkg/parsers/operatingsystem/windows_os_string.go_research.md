<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/windows_os_string.go -->
# sources/cloud-native/moby/pkg/parsers/operatingsystem/windows_os_string.go

Purpose: formats Windows release metadata into strings resembling `winver.exe`. Important type is `windowsOSRelease` with server/client flag, display version, build, and UBR. Control flow appends `Server`, optional `Version <display>`, and `OS Build <build>[.<UBR>]`. State is pure value data. Dependencies are fmt and strings. Risks include string compatibility expectations with existing CLI/API output and omission of unset fields. Test signal is comprehensive table coverage in `windows_os_string_test.go`.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/parsers/operatingsystem/windows_os_string.go -->
