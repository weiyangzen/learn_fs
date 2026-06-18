# sources/distributed-fs/ceph-client/drivers/usb/host/xhci-caps.h

## Purpose
`xhci-caps.h` defines bit extractors and capability masks for xHCI host-controller capability registers, following xHCI specification section 5.3. It is a low-level header used by xHCI code to decode controller limits and feature support from MMIO capability registers.

## Important APIs, Types, And Functions
Macros decode `hc_capbase` (`HC_LENGTH`, `HC_VERSION`), `HCSPARAMS1` (`HCS_MAX_SLOTS`, `HCS_MAX_INTRS`, `HCS_MAX_PORTS`), `HCSPARAMS2` (`HCS_IST_VALUE`, `HCS_IST_UNIT`, `HCS_ERST_MAX`, `HCS_MAX_SCRATCHPAD`), `HCSPARAMS3` (`HCS_U1_LATENCY`, `HCS_U2_LATENCY`), `HCCPARAMS1` feature bits (`HCC_64BIT_ADDR`, `HCC_64BYTE_CONTEXT`, `HCC_PPC`, `HCC_LTC`, `HCC_MAX_PSA`, `HCC_EXT_CAPS`), doorbell/runtime offsets (`DBOFF_MASK`, `RTSOFF_MASK`), and `HCCPARAMS2` feature bits (`HCC2_U3C`, `HCC2_CMC`, `HCC2_LEC`, `HCC2_ETC`, `HCC2_GSC`, `HCC2_VTC`, `HCC2_EUSB2_DIC`, `HCC2_E2V2C`).

## Control Flow
The header has no executable control flow. Its macros are used after code reads xHCI capability registers. Callers mask and shift raw little-endian register values to size arrays, choose context size, discover scratchpad requirements, locate operational/runtime/doorbell regions, and enable/avoid features based on advertised capabilities.

## State And Persistence Behavior
No state is stored. The macros interpret hardware capability state that is stable for the life of a controller instance. The decoded values affect runtime allocations and feature paths elsewhere in the xHCI driver.

## Dependencies And Integration Points
The header includes `<linux/bits.h>` for `BIT()`. It integrates with xHCI register definitions and initialization paths that read the capability MMIO space. Because it encodes spec bit positions, correctness depends on keeping definitions aligned with xHCI revision 1.2 and any later feature additions.

## Risks And Edge Cases
Incorrect masks or shifts would cause systemic xHCI misconfiguration: wrong context size, wrong number of ports/slots/interrupters, undersized scratchpad allocation, bad runtime/doorbell offsets, or enabling unsupported features. Some comments contain typos, but the macro values are the important contract. Callers must pass CPU-endian register values; using raw little-endian values without conversion would decode incorrectly on big-endian systems.

## Test Signals
Compile-time users should build cleanly. Runtime validation can compare decoded values against known controller register dumps, verify context-size decisions, scratchpad allocation counts, port counts, doorbell/runtime offsets, and feature-gated code paths on controllers with and without HCCPARAMS2 capabilities.
