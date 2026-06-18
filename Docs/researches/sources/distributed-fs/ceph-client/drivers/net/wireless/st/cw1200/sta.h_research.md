# Research: sources/distributed-fs/ceph-client/drivers/net/wireless/st/cw1200/sta.h

Purpose: Public prototypes for CW1200 mac80211 STA/AP operations, WSM callbacks, event handling, and internal STA helpers.

Important APIs and types: Declares mac80211 callback implementations for start/stop, interface management, config, filters, EDCA, stats, keying, RTS threshold, flush, multicast preparation, PM setting, TIM, STA add/remove/notify, BSS info changes, AMPDU action, and suspend/resume indications. Defines inline `cw1200_cqm_bssloss_sm` wrapper that serializes `__cw1200_cqm_bssloss_sm` with `bss_loss_lock`.

Control flow: `main.c` binds these declarations into `cw1200_ops`; WSM and workqueue code call the callback declarations to route firmware events into driver state transitions.

State and persistence: No state is defined here, but APIs operate heavily on `struct cw1200_common`.

Dependencies and integration: Shared by main, scan, PM, TX/RX, WSM, and STA implementation code.

Risks: The header exposes many internal work functions, so call context and locking expectations are implicit. The CQM inline wrapper assumes `priv->bss_loss_lock` is initialized.

Test signals: Compile-time consistency with `sta.c` and `main.c`; runtime coverage through mac80211 callback exercise and WSM event delivery.
