<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_platform.c -->
# sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_platform.c

## Purpose
Provides platform-bus discovery for IPMI SI interfaces from firmware or synthetic platform devices: Open Firmware/device tree, ACPI, DMI-created devices, hardcoded devices, hotmod devices, and generic platform resources.

## Important APIs, Types, and Functions
- `ipmi_platform_driver` is the platform driver exported for SI platform devices.
- `ipmi_si_platform_init()` and `ipmi_si_platform_shutdown()` manage registration.
- `ipmi_probe()` attempts OF first, then ACPI, then generic platform properties.
- `of_ipmi_probe()`, `acpi_ipmi_probe()`, and `platform_ipmi_probe()` each construct `si_sm_io`.
- `ipmi_get_info_from_resources()` derives address space, base, and spacing from platform resources.
- `acpi_gpe_irq_setup()` and `acpi_gpe_irq_cleanup()` adapt ACPI GPE interrupts to the SI IRQ handler.
- `ipmi_remove_platform_device_by_name()` removes matching platform devices by name.

## Control Flow
The probe dispatcher prefers device tree if `of_node` exists and succeeds. ACPI probe reads `_IFT`, ignores SSIF, parses resources, optional `_GPE` or platform IRQ, DMI slave address, requests `acpi_ipmi`, and registers. Generic platform probe reads `addr-source`, `ipmi-type`, `reg-size`, `reg-shift`, resources, `slave-addr`, optional IRQ, and registers.

## State and Persistence
Module parameters gate discovery lanes: `tryplatform`, `tryacpi`, `tryopenfirmware`, and `trydmi`. `platform_registered` tracks registration. Per-interface state is transferred to the SI core.

## Dependencies and Integration Points
Depends on platform device APIs, device properties, OF address and IRQ parsing, ACPI methods `_IFT` and `_GPE`, DMI slave address decoding, and generic SI state machines. It creates the common bridge from firmware descriptions to `ipmi_si_add_smi()`.

## Risks
Probe order can mask later discovery lanes when an earlier lane returns success. Firmware property validation is strict for OF `reg-size`, `reg-spacing`, and `reg-shift`. ACPI GPE cleanup must coordinate with `ipmi_irq_start_cleanup()` before removing the handler. Generic platform probe calls `ipmi_si_add_smi(&io)` but returns `0`, so registration failure is not propagated from that branch.

## Test Signals
Exercise OF, ACPI, DMI, hardcode, and hotmod sources; verify GPE and standard IRQ setup/cleanup; test invalid firmware properties; validate duplicate or disabled discovery via module parameters.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/char/ipmi/ipmi_si_platform.c -->
