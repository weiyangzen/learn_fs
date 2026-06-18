# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/bh.h

Purpose: Public interface for the CW1200 bottom-half worker and IRQ bridge.

Important APIs and types: Declares `cw1200_register_bh`, `cw1200_unregister_bh`, `cw1200_irq_handler`, `cw1200_bh_wakeup`, `cw1200_bh_suspend`, `cw1200_bh_resume`, `cw1200_enable_powersave`, and `wsm_release_tx_buffer`.

Control flow: Bus drivers call `cw1200_irq_handler` from SDIO/SPI IRQ context. TX and WSM code call `cw1200_bh_wakeup` and `wsm_release_tx_buffer`. PM paths call suspend/resume wrappers. `cw1200_enable_powersave` must run from the BH thread.

State and persistence: No state is defined here; all state is in `struct cw1200_common`.

Dependencies and integration: Included by bus, firmware, PM, main, and WSM-facing code to share BH lifecycle and wakeup APIs.

Risks: The header documents a key context rule for `cw1200_enable_powersave`; violating it can race device sleep state. IRQ enable/disable locking is handled elsewhere and must remain consistent with BH semantics.

Test signals: Link-time coverage of all prototypes and runtime validation through bus IRQ delivery, BH registration/unregistration, and PM suspend/resume.
