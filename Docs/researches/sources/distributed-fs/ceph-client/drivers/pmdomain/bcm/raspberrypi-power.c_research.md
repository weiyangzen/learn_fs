# sources/distributed-fs/ceph-client/drivers/pmdomain/bcm/raspberrypi-power.c

Purpose: Raspberry Pi firmware-mediated generic PM-domain provider. It controls domains through mailbox firmware properties rather than direct PM registers, including compatibility with the old firmware power-state interface for USB.

Important APIs/types/functions: `struct rpi_power_domain` wraps genpd with firmware domain ID, old/new interface flag, and firmware handle. `struct rpi_power_domains` owns onecell data and all domains. `rpi_firmware_set_power()` sends `RPI_FIRMWARE_SET_POWER_STATE` or `RPI_FIRMWARE_SET_DOMAIN_STATE`; `rpi_domain_on/off()` are genpd callbacks; `rpi_has_new_domain_support()` probes new interface support; `rpi_init_power_domain()` and `rpi_init_old_power_domain()` populate domains; `rpi_power_probe()` registers the provider.

Control flow: probe allocates provider data, obtains the firmware phandle and firmware handle, detects whether the new domain-state interface responds, initializes new-interface domains only when supported, always initializes USB with the old interface, then registers an OF onecell provider. Genpd callbacks build a two-word packet of firmware domain and boolean state and call the chosen mailbox tag.

State and persistence: software tracks firmware handle, per-domain firmware IDs, old/new mode, and genpd reference state. Domains are intentionally initialized as off from Linux's perspective because firmware may already keep hardware on, and Linux should only release references it acquired. Firmware/hardware owns actual persistent state.

Dependencies/integration: depends on built-in Raspberry Pi firmware driver, OF firmware phandle, generic PM domains, DT binding indices from `raspberrypi-power.h`, and platform consumers for I2C, HDMI, V3D, ISP, camera, DSI, USB, ARM, and media blocks.

Risks: firmware unknown-tag behavior requires sentinel detection; if detection is wrong, new-interface domains may be absent or miscontrolled. USB uses the old interface deliberately for compatibility. Firmware calls can fail asynchronously with platform firmware state. Direct BCM2835 PM driver must not race firmware ownership for the same domain.

Test signals: provider probes only with a valid firmware node, new-interface detection changes which domains are registered, USB power works on old firmware, mailbox set calls succeed for each consumer domain, and Linux genpd refcounts do not power off firmware-owned domains that Linux never enabled.
