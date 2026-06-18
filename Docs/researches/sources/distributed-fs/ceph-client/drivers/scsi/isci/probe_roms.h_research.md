# sources/distributed-fs/ceph-client/drivers/scsi/isci/probe_roms.h

Purpose: defines the persistent OEM parameter table format and the user/OEM parameter structures consumed by ISCI controller, PHY, and port setup. It also declares the firmware/option-ROM/EFI loaders from `probe_roms.c`.

Important APIs/types/functions: `struct sci_user_parameters` contains per-PHY spin-up, ALIGN insertion, and max-speed settings plus controller-wide spin-up and inactivity/occupancy timeouts. `enum sci_port_configuration_mode` selects manual or automatic port configuration. `struct sci_oem_params` contains controller mode, spin-up, SSC, cable length, per-port PHY masks, per-PHY SAS addresses, and AFE TX amplitude controls. `struct isci_orom` wraps an ISCI BIOS table header plus two controller parameter blocks. Validation and lookup prototypes include `sci_oem_parameters_validate()`, `isci_request_oprom()`, `isci_request_firmware()`, and `isci_get_efi_var()`.

Control flow: the header has no runtime flow. Its constants and packed structs define the binary contract that `probe_roms.c` validates and host initialization copies into live controller settings. Comments document the interpretation of port mode: APC is selected when no explicit PHY masks are provided, while any explicit mask implies MPC.

State and persistence: `struct isci_orom` mirrors persistent firmware data. `struct sci_user_parameters` is runtime driver configuration, typically derived from defaults/module parameters. All table structs are packed, so field order and width are ABI-sensitive.

Dependencies and integration points: under `__KERNEL__`, the header includes firmware, PCI, EFI, and ISCI definitions; outside the kernel it supplies small SCI dimension constants for tooling. It is consumed by host initialization, port configuration, PHY setup, and ROM/EFI/firmware probing.

Risks and test signals: packed bitfields and versioned table constants make compatibility fragile across compilers and firmware revisions. Port masks must remain within `0x0..0xf`, max speed within generation 3, and controller count/PHY count fixed at current hardware limits. Test signals include OEM validation for each supported ROM version, APC/MPC mode derivation, boundary values for speed and PHY masks, endianness of SAS address fields, and ABI size checks for packed structures.
