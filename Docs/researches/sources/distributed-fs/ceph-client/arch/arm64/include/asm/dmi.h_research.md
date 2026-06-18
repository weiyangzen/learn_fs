## sources/distributed-fs/ceph-client/arch/arm64/include/asm/dmi.h

Purpose: arm64 DMI/SMBIOS integration helpers.

Important APIs/types/functions: declares `dmi_setup`, `dmi_remap`, `dmi_unmap`, and DMI availability behavior depending on configuration.

Control flow: early boot can initialize DMI tables and remap SMBIOS memory for parsing.

State and persistence: DMI core stores parsed table data; remaps are transient virtual mappings.

Dependencies and integration: integrates EFI/ACPI firmware table discovery with Linux DMI matching.

Risks: bad remap ranges can fault during early boot or hide platform quirks. Test signals are DMI table detection on server systems, ACPI/EFI boots, and DMI quirk matching.
