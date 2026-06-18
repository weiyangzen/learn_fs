# sources/distributed-fs/ceph-client/drivers/ata/ahci_seattle.c

Purpose: AMD Seattle AHCI platform driver with optional SGPIO LED/enclosure-management support.

Important APIs/types: `struct seattle_plat_data`, `seattle_transmit_led_message`, `ahci_seattle_get_port_info`, `ahci_seattle_probe`, generic and LED-capable port-info profiles.

Control flow: probe gets/enables resources, selects port info based on SGPIO resource availability and port count, and activates. LED transmit decodes PMP slot, updates activity/locate/fault bits for the port, writes SGPIO register, and records LED state under lock.

State/persistence: SGPIO MMIO pointer, `ahci_port_priv.em_priv[pmp].led_state`, SGPIO per-port LED bits, and generic platform PM state.

Dependencies/integration: ACPI ID `AMDI0600`, `ahci_platform`, AHCI EM constants, libata LED/enclosure hooks, and PM.

Risks/test signals: missing SGPIO silently degrades to generic AHCI; bit layout assumes three bits per port. Test SGPIO enable log, LED sysfs changes, activity state, and normal probe without SGPIO.
