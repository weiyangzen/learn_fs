<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp.h -->
# sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp.h

## Purpose
Defines the internal data model and APIs for the ACPI PCI hotplug driver. It connects generic hotplug slots, ACPI namespace functions, PCI bridge/bus state, and optional platform attention-LED providers.

## Important APIs, Types, and Functions
Important structs are `slot`, `acpiphp_bridge`, `acpiphp_slot`, `acpiphp_func`, `acpiphp_context`, `acpiphp_root_context`, and `acpiphp_attention_info`. It defines flags `SLOT_ENABLED`, `SLOT_IS_GOING_AWAY`, `FUNC_HAS_STA`, and `FUNC_HAS_EJ0`, plus `ACPI_STA_ALL`. Inline helpers convert hotplug slots and ACPI hotplug contexts back to driver objects.

## Control Flow
The header declares the contract between `acpiphp_core.c` and `acpiphp_glue.c`: core registers/deregisters slots and attention providers, while glue enables/disables slots and computes status. Platform extensions register `acpiphp_attention_info` callbacks.

## State and Persistence
The structures declared here define runtime state. A bridge owns a list of slots, a kref, PCI bus/device references, and a going-away flag. A slot owns a PCI bus/device number and functions. Function contexts tie ACPI device hotplug callbacks to slot membership.

## Dependencies and Integration Points
Depends on ACPI, mutex declarations, and `pci_hotplug.h`. It is shared by the ACPI core, glue, Ampere extension, and IBM extension.

## Risks and Edge Cases
Header-level invariants matter: one physical slot may contain multiple ACPI function objects; bridge references protect notification handlers against removal; and attention callbacks are global to acpiphp. Mismanaging `SLOT_IS_GOING_AWAY` or context references can cause use-after-free during ACPI notifications.

## Test Signals
Compile-test all ACPI hotplug files, verify structure assumptions in slot enumeration, test attention provider registration/unregistration, and exercise dock/eject events where contexts and bridge refs are stressed.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/pci/hotplug/acpiphp.h -->
