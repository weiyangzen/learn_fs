<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.c -->
# sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.c

## Purpose
`emac-sgmii.c` is the common internal SGMII PHY layer for the Qualcomm EMAC driver. It selects SoC-specific SGMII operations, maps the internal PHY resources, initializes autonegotiation, manages SGMII interrupts, and provides reset/open/close/link-change hooks to the MAC driver.

## Important APIs, Types, and Functions
- Thin exported dispatchers: `emac_sgmii_init()`, `emac_sgmii_open()`, `emac_sgmii_close()`, `emac_sgmii_link_change()`, and `emac_sgmii_reset()`.
- `emac_sgmii_link_init()` enables SGMII autonegotiation and clears forced TX/RX autoneg bits.
- `emac_sgmii_irq_clear()` implements the interrupt-clear handshake and polls status before finalizing the clear.
- `emac_sgmii_interrupt()` handles decode/disp errors, counts consecutive decode errors, and schedules MAC reinit after `DECODE_ERROR_LIMIT`.
- Common ops `emac_sgmii_common_open()`, `emac_sgmii_common_close()`, `emac_sgmii_common_link_change()`, and `emac_sgmii_common_reset()` are shared by the SoC-specific initializers.
- `emac_sgmii_config()` finds the internal PHY using ACPI child devices or DT `internal-phy`, maps resources, chooses ops, initializes SGMII, records the optional IRQ, and releases the platform-device reference.

## Control Flow
Probe-time configuration selects ops from ACPI `_HRV` or DT compatible, maps base/digital resources, calls the selected initializer, enables autonegotiation, and records an IRQ if present. Open clears and masks interrupts before registering the SGMII IRQ. Link-up clears and enables decode-error interrupts; link-down disables and synchronizes the IRQ. Interrupt handling masks to decode-related bits, increments the consecutive decode-error counter, schedules `adpt->work_thread` when the threshold is reached or when clearing fails, and acknowledges the hardware.

## State and Persistence
`struct emac_sgmii` stores MMIO mappings, optional IRQ, an atomic decode-error counter, and selected ops. Hardware state persists in the internal PHY registers. The file uses scheduled work on the parent adapter for recovery rather than resetting directly in IRQ context.

## Dependencies and Integration Points
It depends on platform resources, OF/ACPI matching, IRQ APIs, `readl_poll_timeout_atomic()`, and EMAC wrapper registers from `emac.h`. It is called by `emac_probe()`, `emac_open()`, `emac_close()`, link adjustment in the MAC/PHY path, and `emac_reinit_locked()`.

## Risks and Edge Cases
- `emac_sgmii_common_close()` unconditionally calls `free_irq(sgmii->irq, adpt)` after masking; if no IRQ was registered, callers rely on only platforms with common ops having a valid IRQ.
- ACPI child matching returns success only for known `_HRV` values; unknown hardware silently leaves no internal PHY.
- Manual `ioremap()` resources must be unmapped on remove and on all error paths.
- SGMII decode errors are treated as recoverable only after consecutive hits; intermittent errors reset the counter.
- The clear sequence uses an 8-bit status variable for a 32-bit read, matching current masks but fragile if higher interrupt bits are added.

## Test Signals
Important tests are DT and ACPI probe for each supported internal PHY, IRQ clear failure injection, link-up/down interrupt masking, repeated decode-error recovery through `work_thread`, and clean remove/unmap behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/ethernet/qualcomm/emac/emac-sgmii.c -->
