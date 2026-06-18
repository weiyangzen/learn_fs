# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis_spi_cr50.c

## Purpose
Specializes the TIS SPI PHY for Google Cr50 firmware timing, wake, ready-IRQ, and firmware-version behavior.

## Important APIs, Types, And Functions
`struct cr50_spi_phy` wraps `tpm_tis_spi_phy` with access-delay tracking, mutex, last-access timestamp, and IRQ confirmation state. Important functions are `cr50_spi_irq_handler()`, `cr50_ensure_access_delay()`, `cr50_wake_if_needed()`, `cr50_spi_flow_control()`, `tpm_tis_spi_cr50_transfer()`, `cr50_print_fw_version()`, `cr50_spi_probe()`, and `tpm_tis_spi_resume()`.

## Control Flow
Probe allocates Cr50 PHY, sets custom flow control, initializes wake and access-delay state, requests an optional rising-edge ready IRQ, initializes the generic SPI TIS layer in polling IRQ mode, prints firmware version from `TPM_CR50_FW_VER`, and marks the chip firmware-power-managed by default. Transfers take a mutex, ensure required inter-transaction delay or IRQ confirmation, wake Cr50 by toggling chip select after sleep, delegate to `tpm_tis_spi_transfer()`, then update last access. Resume resets wake timing before calling core resume.

## State And Persistence
Runtime state tracks when Cr50 may sleep, whether ready IRQs are confirmed, current access delay policy, and the embedded SPI/TIS core state. TPM persistent state remains in the device firmware.

## Dependencies And Integration Points
Depends on the generic SPI TIS transfer engine, Cr50 OF/SPI dispatch in `tpm_tis_spi_main.c`, TPM core resume, and the firmware-power-managed property.

## Risks And Edge Cases
Ready IRQ is used only after confirmation; otherwise fixed delays are used. Jiffies wrap can cause harmless extra delays but is acknowledged. Flow control waits until bit 0 is set and times out with `-EBUSY`. Wake toggling assumes asserting chip select is sufficient after sleep.

## Test Signals
Cr50 SPI with and without IRQ, IRQ confirmation fallback, inter-transaction delay, wake-after-sleep behavior, flow-control timeout, firmware-version readout, firmware-power-managed property, and suspend/resume.
