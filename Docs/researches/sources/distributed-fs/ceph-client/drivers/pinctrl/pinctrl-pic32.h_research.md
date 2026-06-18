# sources/distributed-fs/ceph-client/drivers/pinctrl/pinctrl-pic32.h

## Purpose
This header centralizes PIC32MZ DA pinctrl register offsets used by `pinctrl-pic32.c`. It defines PORT register offsets for each GPIO bank and Peripheral Pin Select input/output register offsets for remappable peripheral functions and pins.

## Important APIs, Types, And Functions
The file contains macros only. PORT bank offsets include `ANSEL_REG`, `TRIS_REG`, `PORT_REG`, `LAT_REG`, `ODCU_REG`, `CNPU_REG`, `CNPD_REG`, `CNCON_REG`, `CNEN_REG`, `CNSTAT_REG`, `CNNE_REG`, and `CNF_REG`. Input PPS offsets include `INT1R` through `INT4R`, timer clock inputs, input capture inputs, UART RX/CTS inputs, SPI SDI/SS inputs, CAN RX inputs, and reference clock inputs. Output PPS offsets include remappable pin output registers such as `RPA14R`, `RPB0R`, `RPC1R`, `RPD0R`, `RPE3R`, `RPF0R`, and `RPG0R`.

## Control Flow
There is no runtime control flow in this header. The C driver consumes these constants in static pin group tables and when calculating bank register accesses. PPS mux writes use the input/output register macros as `muxreg` values, while GPIO and pinconf callbacks use the PORT register macros relative to each bank's MMIO base.

## State And Persistence
The header has no software state. Its constants define addresses of hardware state that persists in the PIC32 peripheral registers. Any incorrect offset here directly changes which hardware register the driver reads or writes.

## Dependencies And Integration Points
The header is included only by the PIC32 pinctrl implementation in this subset. It depends on the including file for SET/CLR alias address transforms and for the MMIO base. It forms a compact contract between the large static pin group tables and the low-level register writes.

## Risks And Test Signals
Risk is table accuracy: a single incorrect PPS offset can route a peripheral to the wrong pin or fail to route it at all. The header does not encode field widths or valid mux values, so those must remain consistent with `pic32_groups[]`. Tests should verify muxing for every register family, compare offsets against the PIC32MZ DA datasheet, and build-test that every macro referenced by `pinctrl-pic32.c` remains defined.
