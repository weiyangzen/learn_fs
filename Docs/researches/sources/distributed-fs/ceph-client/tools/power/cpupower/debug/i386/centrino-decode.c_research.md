<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/centrino-decode.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/centrino-decode.c

## Purpose
Debug helper for decoding Intel Enhanced SpeedStep Centrino performance status. It either reads `MSR_IA32_PERF_STATUS` from `/dev/cpu/N/msr` for a CPU or decodes a provided raw MSR value.

## Important APIs, Types, And Functions
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.

## Control Flow
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.

## State And Persistence
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.

## Dependencies And Integration Points
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.

## Risks And Edge Cases
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.

## Test Signals
Control flow parses the optional argument: values below `MCPU` are treated as CPU numbers, larger values as raw MSR content. `rdmsr()` opens the msr device, seeks to register 0x198, reads 8 bytes, and `decode()` prints multiplier and millivolts from low bits. State is read-only device access. Dependencies are msr kernel driver, root/read permissions, x86 hardware, and POSIX file APIs. Risks include `cpu > MCPU` allowing cpu 32 despite `MCPU=32`, ambiguous argument mode, old voltage formula applicability, and no detailed errno diagnostics. Test signals are raw decode values, missing msr device, non-root failure, and CPU argument boundaries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/centrino-decode.c -->
