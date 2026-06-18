<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mpp.h -->
## sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mpp.h

### Purpose
`mpp.h` encodes Orion5x multi-purpose pin function definitions and SoC availability masks.

### Important APIs, Types, And Functions
The `MPP()` macro encodes pin number, select value, input/output capability, and availability on F5181, F5182, and F5281 variants. It defines function constants for MPP0 through MPP19 and declares `orion5x_mpp_conf()`.

### Control Flow
There is no executable flow. Board files build null-terminated MPP arrays from these constants.

### State, Persistence, And Dependencies
The header has no state. Its encodings are interpreted by plat-orion MPP code.

### Integration Points
Every Orion5x board setup file uses these constants to describe pin muxing.

### Risks
Some select values differ by SoC variant, and availability bits protect only if the variant mask is correct. The file covers only MPP0-19; boards using higher GPIOs must mark them valid separately.

### Test Signals
Board-level validation should confirm all muxed pins perform their intended GPIO/peripheral role.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/arch/arm/mach-orion5x/mpp.h -->
