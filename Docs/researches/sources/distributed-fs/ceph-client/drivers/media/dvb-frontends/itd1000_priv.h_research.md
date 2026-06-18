# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/itd1000_priv.h

### Purpose
`itd1000_priv.h` contains private state and register definitions for the ITD1000 tuner implementation.

### Important APIs, Types, And Functions
`struct itd1000_state` stores the config pointer, I2C adapter, last programmed frequency, and a 256-byte shadow register cache. `enum itd1000_register` names the register range used by initialization, PLL, VCO, RF tracking, gain, and reserved register programming.

### Control Flow
The header has no executable logic. `itd1000.c` uses the enum values for table-driven register writes and shadow-cache access.

### State, Persistence, And Dependencies
The shadow array is memory state used to work around controller read behavior and to preserve register values across writes. The enum documents register addresses from `0x65` through `0x9b`, including reserved values.

### Integration Points
Only the ITD1000 implementation should include this header; it is not a public board-driver interface.

### Risks
Reserved and undocumented register names are still programmed by the driver, so changing enum values or table alignment can break hardware. Shadow cache correctness is required for safe reads.

### Test Signals
Compile-check enum users, verify shadow cache is initialized before reads, and compare register traces against known-good ITD1000 initialization.
