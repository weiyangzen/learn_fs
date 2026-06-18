# sources/distributed-fs/ceph-client/drivers/mmc/host/sdhci-acpi.c

## Purpose

`sdhci-acpi.c` is the ACPI platform glue for SDHCI controllers. It maps ACPI HID/UID combinations to slot descriptions, applies vendor quirks for Intel, Qualcomm, and AMD controllers, wires card-detect GPIOs and DMI quirks, manages runtime/system PM, and registers an SDHCI host through the generic SDHCI core.

## Important APIs, Types, And Functions

- `struct sdhci_acpi_chip` carries reusable `sdhci_ops`, quirks, caps, and PM caps for a controller family.
- `struct sdhci_acpi_slot` describes per-HID/UID slot policy: chip pointer, quirks/caps, flags, private data size, and optional probe/remove/free/setup hooks.
- `struct sdhci_acpi_host` is the SDHCI private state.
- Intel DSM support uses `__intel_dsm()`, `intel_dsm_init()`, `intel_start_signal_voltage_switch()`, `intel_probe_slot()`, and `intel_setup_host()`.
- Qualcomm PWRCTL interrupt support is handled by `sdhci_acpi_qcom_handler()`, `qcom_probe_slot()`, and `qcom_free_slot()`.
- AMD HS200/HS400 support uses `amd_select_drive_strength()`, `sdhci_acpi_amd_hs400_dll()`, `amd_set_ios()`, `amd_sdhci_execute_tuning()`, and `amd_sdhci_reset()`.

## Control Flow

Probe finds the ACPI companion, applies the first matching DMI quirk, selects a slot from `sdhci_acpi_uids`, powers up the ACPI device, performs Bay Trail IOSF setup/defer logic, allocates `sdhci_host` plus slot private data, maps IRQ and MMIO, and invokes slot-specific probe hooks. It then merges chip and slot quirks/caps into the host, configures card-detect GPIO and DMI-specific pull-up/write-protect/active-high behavior, runs `sdhci_setup_host()`, calls slot setup hooks, and registers with `__sdhci_add_host()`.

System and runtime suspend mark retuning needed when appropriate, suspend the SDHCI host, and optionally use Intel DSM to reset SD signal voltage to 3.3 V on affected systems. Resume reapplies Bay Trail IOSF settings and resumes the host. Remove disables runtime PM, calls slot cleanup hooks, removes the host, and frees slot resources.

## State And Persistence Behavior

Slot and chip tables are static. Runtime state is in `struct sdhci_acpi_host` and vendor private storage. Intel private state caches the DSM function mask and high-speed capabilities; AMD private state tracks whether tuning succeeded and whether the HS400 DLL is enabled. DMI quirks are evaluated at probe and copied into host caps/flags.

## Dependencies And Integration Points

This file integrates ACPI device matching, DMI quirks, GPIO descriptors via `mmc_gpiod_request_cd()`, generic SDHCI setup/add/remove, runtime PM, x86 IOSF MBI on Bay Trail, Intel ACPI DSM methods, Qualcomm secondary IRQs, and AMD eMMC timing callbacks.

## Risks And Edge Cases

- ACPI tables with missing or inaccurate HID/UID data fall back to default SDHCI ops and may miss board-specific quirks.
- Intel DSM failures are mostly non-fatal; firmware behavior directly affects advertised modes.
- DMI quirks can regress card-detect/write-protect or suspend voltage behavior if system identifiers are too broad or too narrow.
- Qualcomm secondary IRQ failure leaves the host running without the extra PWRCTL acknowledgement path.
- AMD HS400 tuning state is sticky across timing changes and resets.

## Test Signals

Runtime signals include ACPI probe by HID/UID, card-detect GPIO polarity and pull-up behavior, Intel voltage DSM calls during CMD11 and suspend, Bay Trail deferred probe, Qualcomm PWRCTL IRQ handling, AMD HS200/HS400 tuning and DLL toggling, runtime PM autosuspend/resume, and system suspend/resume with retune requests.
