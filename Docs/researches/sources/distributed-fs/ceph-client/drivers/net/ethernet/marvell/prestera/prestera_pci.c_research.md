# sources/distributed-fs/ceph-client/drivers/net/ethernet/marvell/prestera/prestera_pci.c

Purpose: PCI transport and firmware loader for Prestera devices. It maps BARs, downloads firmware through loader registers, initializes firmware command/event queues, handles MSI interrupts, and registers the core Prestera device.

Important APIs/types/functions: PCI probe/remove, firmware loader structs/register offsets, `struct prestera_fw`, event queue helpers, command queue send path, `prestera_fw_init/uninit/load()`, firmware version/header parsing, IRQ handler, and `prestera_fw_send_req()` implementing `prestera_device->send_req`.

Control flow: Probe enables PCI, requests BARs, sets DMA mask, maps control and packet-processor regions, allocates `prestera_fw`, loads firmware if loader is ready, waits for FW ready, discovers command/event queue locations, allocates event buffer, creates event workqueue, enables MSI, requests IRQ, then calls `prestera_device_register()`. Command sending serializes by queue mutex, writes request to IO memory, signals firmware, waits for reply, bounds-checks reply length, copies response, and acknowledges. IRQ handles RX status for packets and schedules event queue drain work.

State and persistence: Runtime state includes mapped IO addresses, firmware image pointer during load, loader ring indexes, command/event queue descriptors, event message buffer, workqueue, PCI device data, firmware revision, and core `prestera_device`. Firmware binary is requested and released during load; no persistent driver storage.

Dependencies/integration: Depends on Linux PCI, firmware loader, MSI IRQ, IO polling, circular buffer helpers, and the core Prestera registration API in `prestera_main.c`. Firmware paths vary for selected ARM64-based device IDs and fall back from supported version 4.1 to 4.0.

Risks: Firmware ABI and register offsets are critical. Loader send writes 32-bit chunks from firmware data and assumes safe alignment/length handling. Queue counts from firmware are trusted against fixed arrays. Event work disables/enables event control around draining; missed ordering could affect event delivery. Command queue `qid` is not range-checked in `prestera_fw_send_req()`. Fallback firmware may lack newer features expected elsewhere.

Test signals: PCI ID matching, BAR layout on AC3X/Aldrin/AC5X variants, firmware request/fallback/header/version/CRC paths, loader timeout/status errors, FW ready timeout, command timeout/oversize reply, MSI event and packet interrupts, event queue wraparound, module remove cleanup, and core switch registration after firmware ready.
