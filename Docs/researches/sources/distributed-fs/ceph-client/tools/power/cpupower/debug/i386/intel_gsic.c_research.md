<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/intel_gsic.c -->
# sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/intel_gsic.c

## Purpose
Debug helper that invokes the BIOS GSIC interface through vm86/real-mode interrupt 0x15 using liblrmi. It reports SpeedStep SMI command/event ports and flags or dumps registers if unsupported.

## Important APIs, Types, And Functions
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.

## Control Flow
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.

## State And Persistence
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.

## Dependencies And Integration Points
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.

## Risks And Edge Cases
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.

## Test Signals
Control flow initializes LRMI, sets EAX/EDX signature values, calls `LRMI_int(0x15)`, and formats returned registers with warnings for non-default SMI command/port values. State is BIOS interrupt side effects limited to the query. Dependencies are liblrmi, x86 real-mode BIOS availability, and sufficient privileges/environment to perform LRMI calls. Risks include not working on x86_64/UEFI-only systems, BIOS-specific behavior, and suggesting module parameters that can be risky if misused. Test signals are build/link with `-llrmi`, LRMI init failure, supported BIOS output, and unsupported-register dump.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/power/cpupower/debug/i386/intel_gsic.c -->
