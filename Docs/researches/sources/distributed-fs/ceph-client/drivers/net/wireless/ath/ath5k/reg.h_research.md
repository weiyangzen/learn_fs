# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath5k/reg.h

## Purpose

`reg.h` is the ath5k hardware register map for Atheros AR5210/AR5211/AR5212-era MAC, QCU/DCU, PCU, EEPROM, PHY/RF, and WiSoC platform registers. It defines register addresses, bit masks, shifts, queue-indexed address macros, and version-dependent address aliases used by the rest of the driver.

## Important APIs, Types, and Definitions

This header has no functions or persistent objects. Its important interface is its macro vocabulary. Address families include MAC DMA/control (`AR5K_CR`, `AR5K_CFG`, `AR5K_TXCFG`, `AR5K_RXCFG`), interrupts (`AR5K_ISR`, `AR5K_PISR`, `AR5K_SISR*`, `AR5K_IMR`, `AR5K_PIMR`, `AR5K_SIMR*`), QCU registers (`AR5K_QUEUE_TXDP()`, `AR5K_QCU_TXE`, `AR5K_QUEUE_CBRCFG()`, `AR5K_QUEUE_RDYTIMECFG()`, `AR5K_QUEUE_MISC()`, `AR5K_QUEUE_STATUS()`), DCU registers (`AR5K_QUEUE_QCUMASK()`, `AR5K_QUEUE_DFS_LOCAL_IFS()`, `AR5K_QUEUE_DFS_RETRY_LIMIT()`, `AR5K_QUEUE_DFS_CHANNEL_TIME()`, `AR5K_QUEUE_DFS_MISC()`), reset/sleep/PCI/GPIO registers, EEPROM access registers, PCU registers, key table sizing, PHY/RF registers, TX power tables, and WiSoC reset/enable registers.

Several macros intentionally depend on a live `ah` variable to choose AR5210 versus AR5211+ addresses or flags, for example `AR5K_EEPROM_DATA`, `AR5K_EEPROM_STATUS`, `AR5K_STA_ID1_PCF`, `AR5K_USEC`, `AR5K_BEACON`, `AR5K_TIMER*`, `AR5K_RX_FILTER`, `AR5K_DIAG_SW`, `AR5K_TSF_L32`, and `AR5K_PHY_FRAME_CTL`. Queue-indexed macros use `AR5K_QUEUE_REG(_r, _q)` to compute per-queue offsets.

## Control Flow

As a header, control flow is indirect. Code in `phy.c`, `qcu.c`, reset, interrupt, EEPROM, GPIO, beacon, and DMA modules reads these definitions to build register values with local helpers such as `AR5K_REG_SM`, `AR5K_REG_MS`, `AR5K_REG_WRITE_BITS`, `AR5K_REG_ENABLE_BITS`, and `AR5K_REG_DISABLE_BITS` from shared headers.

The register map is organized by hardware block. MAC DMA and base interrupt definitions appear first, followed by QCU/DCU scheduling blocks, reset/sleep/PCI/GPIO, EEPROM access, PCU/TSF/beacon/MIB/XR/QoS/key-related registers, then PHY and RF registers. This order mirrors how reset and initialization code tends to bring the device up: DMA and interrupts, queue scheduling, power/reset, EEPROM, PCU, then PHY/RF.

## State and Persistence Behavior

`reg.h` itself stores no state, but its macros define all memory-mapped hardware state manipulated by ath5k. Writes to these addresses persist in device registers until reset, sleep transition, or later driver writes. Read-and-clear interrupt aliases (`AR5K_RAC_PISR`, `AR5K_RAC_SISR*`) have destructive read semantics by design. MIB counters are cleared on read or controlled by `AR5K_MIBC`. EEPROM macros define persistent nonvolatile access paths, although actual read/write sequencing lives elsewhere.

Version-dependent macros are a major state coupling: the same logical register often has different addresses or bit meanings on AR5210 versus AR5211/AR5212. Users must only expand those macros in contexts with a valid `struct ath5k_hw *ah` named `ah`.

## Dependencies and Integration Points

The file includes `../reg.h` for shared register helper macros and uses ath5k hardware version constants defined elsewhere. It is included by most hardware-facing ath5k source files. `phy.c` uses the PHY/RF, spur, antenna, calibration, and TX power definitions. `qcu.c` uses the QCU/DCU, IFS, retry, interrupt mask, and AR5210 no-QCU definitions. EEPROM code uses `AR5K_EEPROM_*`; reset/power code uses reset, sleep, PCI, GPIO, and PCU definitions; interrupt code uses ISR/IMR/SISR/SIMR fields.

The header also integrates older 5210 behavior with newer 5211/5212 behavior through aliases, keeping call sites mostly hardware-family-neutral while still exposing family-specific bits when needed.

## Risks and Edge Cases

This header is high blast radius because a wrong address, mask, or shift changes hardware behavior across many modules. Several definitions are reverse-engineered or annotated with uncertainty, so changes must be treated as hardware behavior changes rather than cosmetic cleanup. Overlapping addresses are intentional in many cases, either because AR5210 and AR5211+ use different blocks at the same offset or because one register has multiple interpretations by radio generation.

Macros that reference `ah` can fail unexpectedly if used outside the local naming convention or in contexts where the version is not initialized. Typographical mistakes in macros are especially risky because they may compile into incorrect register programming; for example rate-table and PHY masks should be cross-checked with all consumers before modification. Queue and interrupt masks represent only a subset of hardware queues in some registers, so callers must respect queue count and QCU/DCU representation limits.

Read-clear registers and MIB counters need careful sequencing to avoid losing interrupt or counter information. EEPROM write macros expose persistent device storage; code using them must enforce status polling and protection semantics.

## Test Signals

Validation signals are mostly integration-level: successful reset, EEPROM reads, interrupt enable/status behavior, queue scheduling, beacon timers, GPIO/rfkill interrupts, MIB counter updates, PHY calibration, channel programming, and TX power table writes across supported chip families. Static review should compare every changed address/mask/shift against consumers and known hardware references. Build coverage should include all files that include `reg.h`, and runtime coverage should include both AR5210-specific aliases and AR5211/AR5212 paths.
