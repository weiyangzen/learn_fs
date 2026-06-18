<!-- BEGIN_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo.go -->
# sources/cloud-native/moby/pkg/meminfo/meminfo.go

Purpose: public entry point and data model for memory information. `Read` delegates to platform-specific `readMemInfo`, and `Memory` stores total/free/available memory plus swap totals/free values. State is a snapshot of host memory at call time. Dependencies are platform-specific files in the package. Risks depend on backend parsing/API behavior; fields may be zero where the platform cannot provide them. Test signal comes from Linux/unix parser tests.
<!-- END_FILE_RESEARCH: sources/cloud-native/moby/pkg/meminfo/meminfo.go -->
