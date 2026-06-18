# sources/distributed-fs/ceph-client/drivers/accel/amdxdna/aie2_psp.c

Purpose: handles AMD Platform Security Processor interaction for validating, starting, wait-mode polling, and stopping NPU firmware. It prepares an aligned firmware buffer and drives PSP command registers.

Important APIs/functions: `aie2m_psp_create()` allocates a managed `psp_device`, copies PSP register mappings from `psp_config`, allocates an aligned firmware buffer, computes a physical address acceptable to PSP, and copies firmware bytes. `aie2_psp_start()` sends `PSP_VALIDATE` with firmware address/size, then `PSP_START` with copy-fw mode. `aie2_psp_stop()` sends `PSP_RELEASE_TMR`. `aie2_psp_waitmode_poll()` waits for firmware wait mode via the PWAITMODE register. Internal `psp_exec()` writes command/argument registers, toggles interrupt, polls ready, and checks response.

Control flow: `aie2_init()` creates the PSP handle after BAR mapping and firmware loading; `aie2_hw_start()` starts PSP before mailbox firmware handshake; `aie2_hw_stop()` stops PSP after firmware suspend/mailbox teardown.

State and persistence: `struct psp_device` keeps DRM device, aligned firmware backing memory, physical firmware address, firmware size, and PSP register pointers. Firmware state persists in hardware until stop/reset, not on disk.

Dependencies: depends on BAR offset tables from register files, PSP indices from `aie2_pci.h`, Linux polling helpers, DRM managed allocation, and the firmware loader path in `aie2_pci.c`.

Risks: PSP requires physical address alignment; using `virt_to_phys()` on the managed allocation assumes suitable memory. Command timeouts or nonzero firmware responses become probe/start failures. Register tables must map PSP command, argument, status, interrupt, response, and wait-mode slots accurately per device.

Test signals: valid and corrupt firmware images, timeout/error response simulation, alignment checks, start/stop cycles across runtime/system suspend, and per-generation PSP register table validation.
