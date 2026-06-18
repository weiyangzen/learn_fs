<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ampere_altra.c -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ampere_altra.c

## Purpose
Provides an Ampere Altra ACPI hotplug extension that controls slot attention LEDs by making ARM SMCCC calls to system firmware.

## Important APIs, Types, and Functions
`set_attention_status()` maps hotplug LED state to firmware LED commands and sends `HANDLE_OPEN`, `REQUEST`, and `HANDLE_CLOSE` SMC calls. `get_attention_status()` is unsupported. `altra_led_probe()` reads a firmware UUID property and registers `ampere_altra_attn` with acpiphp. `altra_led_remove()` unregisters it. The ACPI platform ID is `AMPC0008`.

## Control Flow
When the platform device probes, it reads four `u32` UUID words from firmware node property `uuid`, then registers global acpiphp attention callbacks. Setting attention status finds the root port for the slot bus, disables local IRQs, opens a firmware service handle, sends a LED attention request keyed by root-port slot and PCI domain nibble, closes the handle, restores IRQs, and returns firmware errors as `-ENODEV`.

## State and Persistence
The only persistent runtime state is `led_service_id[4]` and registration of the global attention callback while the platform driver is bound.

## Dependencies and Integration Points
Depends on ACPI platform device matching, ARM SMCCC, PCI root-port lookup, hotplug slot structures, and acpiphp attention registration.

## Risks and Edge Cases
The provider cannot report attention status, so reads return `-EINVAL`. Firmware call failures map to `-ENODEV` without detailed status. The request encodes only low PCI domain bits. IRQs are disabled around all SMCCC calls, so firmware latency matters. Only one acpiphp attention provider can be registered globally.

## Test Signals
Probe with and without `uuid`, set LED off/on/blink from hotplug sysfs, verify SMCCC failure handling, unload the module and confirm callback removal, and test systems with no root port for a slot.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp_ampere_altra.c -->
