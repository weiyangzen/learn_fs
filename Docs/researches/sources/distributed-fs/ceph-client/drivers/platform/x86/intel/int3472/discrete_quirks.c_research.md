<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete_quirks.c -->
# sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete_quirks.c

## Purpose
Holds DMI quirks for INT3472 discrete devices.

## Important Data
Currently defines a Lenovo Miix 510-12IKB quirk that maps AVDD to a second sensor device name `i2c-OVTI2680:00`.

## Control Flow And State
`skl_int3472_discrete_quirks[]` is consulted by `discrete.c` probe. If matched, quirk data is copied into the runtime discrete device and later used when registering regulators.

## Dependencies And Integration Points
Depends on DMI matching and `struct int3472_discrete_quirks` from platform data headers.

## Risks And Test Signals
Risks are overly broad DMI matches or stale sensor names. Test on Lenovo Miix 510 to confirm both sensors receive the expected AVDD consumer supply and non-matching systems are unaffected.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/platform/x86/intel/int3472/discrete_quirks.c -->
