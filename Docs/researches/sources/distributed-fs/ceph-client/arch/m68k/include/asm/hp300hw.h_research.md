<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hp300hw.h -->
# sources/distributed-fs/ceph-client/arch/m68k/include/asm/hp300hw.h

## Purpose
`hp300hw.h` exposes minimal HP 300 platform hardware identity for m68k code.

## Important APIs, Types, and Functions
The header includes `bootinfo-hp300.h` and declares `extern unsigned long hp300_model`.

## Control Flow, State, and Persistence
There is no local control flow. `hp300_model` is persistent boot-time global state populated by HP300 setup code and then read by platform drivers or diagnostics.

## Dependencies and Integration Points
It depends on HP300 bootinfo definitions and integrates with model-detection code under the HP300 m68k machine port.

## Risks
Consumers rely on initialization ordering: `hp300_model` must be valid before hardware-specific probes branch on it. The file intentionally does not validate model values.

## Test Signals
Build HP300 configs and inspect boot model reporting. Platform-specific driver probes should select the expected path for each supported HP300 model.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/m68k/include/asm/hp300hw.h -->
