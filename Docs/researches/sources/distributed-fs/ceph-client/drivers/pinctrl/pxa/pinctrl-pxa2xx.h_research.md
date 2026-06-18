# sources/distributed-fs/ceph-client/drivers/pinctrl/pxa/pinctrl-pxa2xx.h

## Purpose
Defines the shared PXA2xx pin descriptor DSL, driver data structures, and initializer prototype used by the PXA25x and PXA27x pinctrl drivers.

## Important APIs, Types, And Functions
Macros include `PXA_FUNCTION`, `PXA_PIN`, `PXA_GPIO_PIN`, `PXA_GPIO_ONLY_PIN`, and `PXA_PINCTRL_PIN`. Types include `struct pxa_desc_function`, `struct pxa_desc_pin`, and `struct pxa_pinctrl`. The header declares `pxa2xx_pinctrl_init()`.

## Control Flow
There is no executable flow. Chip-specific files use the macros to build static arrays that the common implementation later scans to derive pinctrl groups and pinmux functions.

## State And Persistence
No runtime state is allocated by the header. `struct pxa_pinctrl` describes runtime state stored by the common implementation, including MMIO bases, generated groups/functions, pinctrl descriptor, and spinlock.

## Dependencies And Integration Points
Depends on generic pinctrl types through included C files and is included by `pinctrl-pxa2xx.c`, `pinctrl-pxa25x.c`, and `pinctrl-pxa27x.c`.

## Risks
The macro DSL hides compound-literal function arrays inside static pin tables, so descriptor lifetime depends on static storage usage in chip files. Direction and alternate-function encoding are packed into `muxval`; incorrect macro arguments directly program wrong hardware bits.

## Test Signals
Compile both chip drivers, inspect generated function/group state, and validate that macro-generated GPIO input/output functions are present on every GPIO-capable pin.
