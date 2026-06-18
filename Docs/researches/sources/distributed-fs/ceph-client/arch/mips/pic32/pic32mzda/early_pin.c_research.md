## sources/distributed-fs/ceph-client/arch/mips/pic32/pic32mzda/early_pin.c

### Purpose
This file provides minimal early Peripheral Pin Select configuration for PIC32MZDA before the full pinctrl driver is initialized. It maps abstract input functions and output pins to PPS register offsets and writes selected values.

### Important APIs, Types, And Functions
`input_pin_reg[]` maps `IN_FUNC_*` identifiers to input PPS registers. `output_pin_reg[]` maps `OUT_*` pin identifiers to output PPS registers. `pic32_pps_input()` maps the PPS block and writes a pin value to the matching function register. `pic32_pps_output()` maps the PPS block and writes a function value to the matching pin register.

### Control Flow
Each function linearly scans its table for the requested function or pin. On match it writes the requested value and returns. If no match is found, it unmaps before returning.

### State, Persistence, And Dependencies
Persistent effects are PPS hardware register assignments. Dependencies are the identifier definitions in `early_pin.h`, raw MMIO, and the fixed PPS base `0x1f800000`.

### Integration Points
`early_console.c` calls these helpers to route UART RX/TX pins for early printk. Later pinctrl may reconfigure pins for normal drivers.

### Risks
Successful paths return without `iounmap()`, leaving early mappings live. This may be intentional for early boot but should be documented or converted to static mapping. Linear tables lack validation for function/pin compatibility beyond caller convention.

### Test Signals
Confirm early UART pins route correctly for supported ports and verify later pinctrl can take over without conflicting PPS state.
