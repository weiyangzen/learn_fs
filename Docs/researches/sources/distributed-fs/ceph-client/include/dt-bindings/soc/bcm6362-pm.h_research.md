# sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6362-pm.h

Source read summary: 22 lines, 695 bytes.

Purpose: `sources/distributed-fs/ceph-client/include/dt-bindings/soc/bcm6362-pm.h` declares device-tree constants for the Broadcom power-management binding, covering power domains, boot modes, protocol selectors, endpoint IDs, or firmware resource classes depending on the SoC.

Important APIs, types, and functions: The file exports 14 visible constants or packing macros; representative names are `BCM6362_POWER_DOMAIN_SAR`, `BCM6362_POWER_DOMAIN_IPSEC`, `BCM6362_POWER_DOMAIN_MIPS`, `BCM6362_POWER_DOMAIN_DECT`, `BCM6362_POWER_DOMAIN_USBH`, `BCM6362_POWER_DOMAIN_USBD`, `BCM6362_POWER_DOMAIN_ROBOSW`, `BCM6362_POWER_DOMAIN_PCM`, `BCM6362_POWER_DOMAIN_PERIPH`, `BCM6362_POWER_DOMAIN_ADSL_PHY`, `BCM6362_POWER_DOMAIN_GMII_PADS`, `BCM6362_POWER_DOMAIN_FAP`, `BCM6362_POWER_DOMAIN_PCIE`, `BCM6362_POWER_DOMAIN_WLAN_PADS`. This header does not define C functions or runtime data structures; its exported API is the set of stable macro names and numeric encodings used by DTS and drivers.

Control flow: DTS and subsystem drivers include the header to keep numeric firmware or register selectors shared between board descriptions and runtime driver code.

State and persistence behavior: There is no runtime persistence in this header. The values become persistent platform ABI once compiled into device trees, firmware handoff tables, or board descriptions, so compatibility depends on preserving numeric assignments.

Dependencies and integration points: It is self-contained and depends only on the device-tree C preprocessor include model.

Risks and edge cases: The values are ABI tokens. Wrong numbering can bind a device to the wrong power domain, protocol mux, boot mode, display endpoint, or firmware TCS class without a compiler error.

Test signals: Run dtbs_check/build coverage for DTS users, compare constants with binding YAML and firmware/register documentation, and exercise the owning driver probe paths.
