# sources/distributed-fs/ceph-client/sound/soc/amd/acp/acp-pci.c

## Purpose
`acp-pci.c` is the generic PCI front end for legacy AMD ACP audio. It binds the AMD ACP PCI function, selects revision-specific resources and machines, maps ACP registers, initializes hardware, requests IRQs, creates child platform devices, and wires runtime/system PM.

## Important APIs, Types, and Functions
The main functions are `acp_pci_probe()`, `acp_pci_remove()`, `snd_acp_suspend()`, `snd_acp_resume()`, `create_acp_platform_devs()`, `acp_fill_platform_dev_info()`, and the wrapper `irq_handler()`. It consumes `struct acp_chip_info`, `struct acp_resource`, `snd_soc_acpi_mach` tables, and revision-specific `*_hw_ops_init()` functions.

## Control Flow
Probe first calls `snd_amd_acp_find_config()` and accepts only legacy or legacy-DMIC modes. It enables the PCI device, requests regions, sets bus mastering, chooses revision-specific names/resources/hardware ops/ACPI machine tables, maps BAR0, initializes ACP hardware, requests the shared IRQ, and calls `check_acp_config()` to detect I2S/PDM configuration. If an I2S or PDM controller is usable, it registers the revision-named ACP platform device and optional `dmic-codec`, saves platform device references, selects the machine device, initializes stream list/lock, and enables autosuspend.

## State and Persistence
`struct acp_chip_info` is devm-allocated and stored as PCI drvdata. It holds register base, revision, machine table, child platform devices, stream list, resource pointer, flags, and configuration booleans. Child devices persist until PCI remove. No persistent storage is used.

## Dependencies and Integration Points
The driver depends on PCI, platform-device, IRQ, PM runtime, ACP common hardware ops, `mach-config.h`, revision resources, and ACPI machine tables. It creates the platform devices that `acp-renoir.c`, `acp-rembrandt.c`, `acp63.c`, `acp70.c`, `acp-platform.c`, `acp-pdm.c`, and machine drivers bind to.

## Risks
Probe has many staged resources; incorrect unwind can leave hardware enabled or child devices registered. `chip->acp_hw_ops_init(chip)` is not checked for failure. Platform device creation can proceed with `chip->res` only when configuration says I2S/PDM exists. Suspend/resume assumes `dev_get_drvdata()` is valid and re-enables interrupts after `acp_hw_init()`.

## Test Signals
Test signals include correct probe by PCI revision `0x01`, `0x6f`, `0x63`, `0x70-0x72`, successful child platform creation, IRQ activity through revision IRQ handlers, runtime suspend/resume, no child devices on unsupported BIOS configs, and clean remove with no registered-device leaks.
