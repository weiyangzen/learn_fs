# sources/distributed-fs/ceph-client/drivers/media/pci/mantis/mantis_evm.c

- Purpose: Host-interface event manager for CAM/PCMCIA smart-buffer events and CAM insertion/removal notifications.
- Important APIs/types/functions: `mantis_hifevm_work()`, `mantis_evmgr_init()`, and `mantis_evmgr_exit()`.
- Control flow: IRQ0 schedules `hif_evm_work`. The worker reads GPIF status, handles plugin/unplug by resetting card state and notifying DVB CA EN50221, logs HIF status bits, and wakes HIF operation waiters when smart-buffer operation completes. Init sets work, initializes PCMCIA, schedules an initial scan, then initializes HIF; exit flushes work and tears down HIF/PCMCIA.
- State and persistence: Uses `mantis_ca` slot state, `hif_event`, wait queues, and `sbuf_status`; no persistence.
- Dependencies and integration points: Depends on GPIF registers, `mantis_pcmcia`, `mantis_hif`, and DVB CA EN50221 callbacks.
- Risks: Worker uses MMIO and CA state asynchronously, so teardown ordering is important. CAM event debounce is minimal and hardware-specific. Wait logic depends on IRQ status being copied into `mantis->gpif_status` by the top-half.
- Test signals: Test CAM insertion/removal, EN50221 userspace notifications, HIF read/write completion waits, and unload while events are pending.
