# sources/distributed-fs/ceph-client/drivers/mailbox/tegra-hsp.c

## Purpose
`tegra-hsp.c` implements the NVIDIA Tegra Hardware Synchronization Primitive mailbox controller. It exposes two mailbox controller instances: doorbells for lightweight notifications between masters and shared mailboxes for 32-bit or 128-bit payload exchange.

## Important APIs, Types, and Functions
Core types are `struct tegra_hsp`, `struct tegra_hsp_doorbell`, `struct tegra_hsp_mailbox`, `struct tegra_hsp_channel`, and `struct tegra_hsp_soc`. Mailbox operations are split between `tegra_hsp_db_ops` and `tegra_hsp_sm_ops`. Important routines include `tegra_hsp_doorbell_irq()`, `tegra_hsp_shared_irq()`, `tegra_hsp_doorbell_startup()`, `tegra_hsp_mailbox_send_data()`, `tegra_hsp_mailbox_flush()`, `tegra_hsp_db_xlate()`, `tegra_hsp_sm_xlate()`, `tegra_hsp_probe()`, and `tegra_hsp_resume()`.

## Control Flow, State, and Persistence
Probe maps the HSP register block, reads the dimensioning register, discovers shared and doorbell IRQs, allocates mailbox channels, registers two mailbox controllers, then requests interrupts. Doorbell clients are translated from device-tree master IDs, enabled through the CCPLEX doorbell's enable register at startup, and signaled by writing `HSP_DB_TRIGGER`. Shared mailbox clients choose RX/TX and 32-bit/128-bit modes via phandle flags. TX writes data, marks the mailbox full, and enables EMPTY interrupts until `tegra_hsp_shared_irq()` observes completion. RX handles FULL interrupts and clears registers after delivering data. Runtime state lives in the `hsp->mask` interrupt-enable bitmap, mailbox producer flags, channel `con_priv`, and SoC capability tables; no persistent storage is used beyond hardware registers restored on resume.

## Dependencies and Integration Points
The driver depends on Linux mailbox controller APIs, platform device probing, OF match data, IRQ handling, Tegra fuse silicon detection, PM resume hooks, and `dt-bindings/mailbox/tegra186-hsp.h`. It integrates with device-tree compatibles for Tegra186, Tegra194, Tegra234, and Tegra264 and with clients using HSP phandles.

## Risks and Test Signals
Key risks are interrupt storms from level-triggered EMPTY interrupts, stale `chan` pointers during early doorbell IRQs, incorrect dimensioning shifts for new SoCs, wrong 128-bit mailbox selection, and missed resume reprogramming. Tests should exercise DT xlate paths, startup/shutdown mask changes, full/empty IRQ ordering, flush timeout behavior, suspend/resume with active clients, and unsupported SoC capability combinations.
