# sources/distributed-fs/ceph-client/drivers/char/tpm/tpm_tis.c

## Purpose
Provides the memory-mapped/PNP/platform front-end for the generic TPM TIS FIFO core.

## Important APIs, Types, And Functions
Defines `struct tpm_info` resource/IRQ input and `struct tpm_tis_tcg_phy` containing `tpm_tis_data` plus MMIO base. PHY operations are `tpm_tcg_read_bytes()` and `tpm_tcg_write_bytes()`. Probe paths include `tpm_tis_pnp_init()`, `tpm_tis_plat_probe()`, `tpm_tis_force_device()`, and shared `tpm_tis_init()`.

## Control Flow
Initialization checks whether an ACPI `MSFT0101` TPM2 device should be handled by CRB instead, maps the memory resource, selects IRQ use based on module parameter and device data, enables iTPM workaround if forced or ACPI HID `INTC0102`, then calls `tpm_tis_core_init()`. Module init may create a forced x86 platform device at `0xFED40000`, registers the platform driver, and optionally the PNP driver. Remove unregisters the TPM chip and delegates hardware cleanup to the core.

## State And Persistence
State is per-device mapped MMIO and `tpm_tis_data`; module parameters `interrupts`, `itpm`, `force`, and `hid` affect probe behavior. No persistent data is stored in software.

## Dependencies And Integration Points
Depends on ACPI TPM2 table interpretation, PNP IDs, OF compatibles, platform resources, and `tpm_tis_core_init()`. It integrates with TPM PM by using `tpm_tis_resume()`.

## Risks And Edge Cases
`MSFT0101` devices with non-memory-mapped ACPI TPM2 start methods must be left to CRB. Forced probing can conflict with firmware-described devices. PREEMPT_RT flush reads reduce latency spikes but add MMIO reads. PNP IDs overlap with older vendor drivers such as Infineon.

## Test Signals
PNP and platform probing, forced x86 probe, ACPI TPM2 CRB handoff, MMIO read/write modes, iTPM workaround selection, IRQ module parameter behavior, and suspend/resume.
