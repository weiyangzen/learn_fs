## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_pin.h

### Purpose
This header defines the early PIC32MZDA PPS function and pin identifiers used by `early_pin.c` and early UART setup.

### Important APIs, Types, And Functions
It defines an enum of input functions, macros for input pin selector values, an enum of output pins, macros for output function selector values, and prototypes for `pic32_pps_input()` and `pic32_pps_output()`.

### Control Flow
There is no runtime control flow. The values are consumed by table lookups in `early_pin.c`.

### State, Persistence, And Dependencies
No state exists. The header encodes PIC32MZDA PPS selector values and depends on callers using function/pin combinations supported by the chip.

### Integration Points
Early console includes this header to configure UART2 or UART6 pin muxing before full pinctrl.

### Risks
Several output function macro names are repeated with different values because PPS output functions are bank-dependent. This is legal for the hardware encoding style but risky for generic callers. Values are not type-safe.

### Test Signals
Compile users with duplicate macro warnings disabled as expected, and verify each early UART mapping writes the documented register selector values.
