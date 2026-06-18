# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_infineon.c

## Purpose
Implements legacy Infineon SLD9630/SLB9635 TPM access over PNP-discovered I/O ports or MMIO, using Infineon's vendor-layer framing and WTX wait-extension protocol.

## Important APIs, Types, And Functions
Global `struct tpm_inf_dev tpm_dev` stores resource type and register locations. Low-level accessors are `tpm_data_in/out()` and `tpm_config_in/out()`. Transport helpers include `empty_fifo()`, `wait()`, `wait_and_send()`, `tpm_wtx()`, `tpm_wtx_abort()`, `tpm_inf_send()`, and `tpm_inf_recv()`. PNP lifecycle is `tpm_inf_pnp_probe()`, `tpm_inf_pnp_remove()`, and `tpm_inf_resume()`.

## Control Flow
Probe obtains I/O or memory resources, requests/remaps them, reads vendor/product/version through config registers, programs data-register base, activates the device, disables reset/low-power/IRQ control, allocates a TPM chip, and registers it. Send clears FIFO, waits for transmit FIFO empty, emits vendor-layer header, data header, and command bytes. Recv reads a four-byte vendor header, handles data frames by copying out the TPM payload, acknowledges or aborts WTX packets up to a maximum, and reports error frames.

## State And Persistence
Global state records the active resource mapping and data/config offsets. `number_of_wtx` counts WTX packets during a receive. Hardware configuration is reprogrammed on resume.

## Dependencies And Integration Points
Uses PNP IDs `IFX0101`/`IFX0102`, port I/O or MMIO accessors, TPM core callbacks, and TPM PM helpers.

## Risks And Edge Cases
The driver is singleton and global-state based. WTX handling can loop until the maximum is reached, then aborts. Receive code assumes vendor frame sizes and shifts payload in place. Resource cleanup differs for port and MMIO paths and must match probe branch. Cancellation is effectively unsupported.

## Test Signals
PNP port and MMIO resource discovery, vendor/product ID reads, WTX grant and abort behavior, malformed vendor frames, FIFO drain timeout, resume reconfiguration, and conflict with generic `tpm_tis` on IFX IDs.
