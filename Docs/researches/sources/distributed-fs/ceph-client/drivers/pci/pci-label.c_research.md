# sources/distributed-fs/ceph-client/drivers/pci/pci-label.c

## Purpose
Exposes firmware-provided PCI device labels and indexes through sysfs. ACPI `_DSM` device names are preferred; SMBIOS type 41 onboard-device names are used as a fallback when ACPI naming is unavailable.

## APIs, Types, And Functions
Defines attribute groups `pci_dev_smbios_attr_group` and `pci_dev_acpi_attr_group`. Helpers include `device_has_acpi_name()`, `find_smbios_instance_string()`, `dsm_get_label()`, `dsm_label_utf16s_to_utf8s()`, and sysfs show callbacks for `label`, `index`, and `acpi_index`.

## Control Flow
Visibility callbacks hide SMBIOS attributes when ACPI naming DSM exists and hide ACPI attributes when it does not. SMBIOS lookup scans DMI onboard device records and matches segment, bus, and devfn. ACPI lookup evaluates the PCI device-name DSM, validates a two-element package, emits the integer index, and emits either ASCII string data or UTF-16 buffer data converted to UTF-8.

## State And Persistence
No state is stored. Sysfs output is generated on demand from ACPI and DMI firmware tables.

## Dependencies And Integration
Depends on DMI, ACPI DSM APIs, NLS UTF-16 conversion, sysfs, `pci_acpi_dsm_guid`, and PCI device identity fields. The attribute groups are referenced by PCI device sysfs group definitions elsewhere in the PCI core.

## Risks And Test Signals
Risks include malformed DSM packages, UTF-16 conversion length handling, SMBIOS/ACPI precedence, matching wrong segment/bus/devfn, and visibility inconsistencies when firmware data is incomplete. Test signals include ACPI-label systems, SMBIOS-only systems, no-label systems, UTF-16 buffer labels, invalid DSM return objects, and sysfs attribute visibility checks.
