# sources/distributed-fs/ceph-client/drivers/net/wireless/silabs/wfx/main.c

Purpose: Implements common WFx device allocation/probe/release, mac80211 capability registration, firmware/PDS startup, bus-driver registration, and module init/exit.

Important APIs and functions: `wfx_init_common()` allocates `ieee80211_hw`, sets hardware/wiphy capabilities, copies platform data, gets wakeup GPIO, initializes locks/completions/work/queues/HIF command state, and attaches devm cleanup. `wfx_probe()` creates the BH workqueue, loads firmware via `wfx_init_device()`, waits for startup, validates API/secure-link mode, applies regulatory hints, uploads PDS, subscribes IRQs, enables multi-TX confirmations and power mode, selects MAC addresses, registers mac80211, and initializes debugfs. `wfx_release()` unregisters hw, sends shutdown, unsubscribes IRQ, flushes BH, and destroys the workqueue. Module init/exit register/unregister SPI and SDIO drivers depending on Kconfig.

Control flow and integration: Bus probe calls `wfx_init_common()` then `wfx_probe()`. Early boot disables wakeup GPIO use and uses polled IRQ until firmware startup indication arrives. After PDS and IRQ setup, the driver switches to quiescent or doze power mode and exposes the device to mac80211. Release reverses registration and sends a no-reply shutdown.

State and persistence: Initializes persistent `wfx_dev` state: platform data, bus ops/private pointer, vif array, addresses, firmware caps, keyset, locks, queues, work items, stats locks, key map, packet ID, and BH workqueue. Firmware caps and MAC addresses drive later runtime behavior.

Dependencies: Depends on mac80211/cfg80211, OF MAC/PDS properties, firmware loader, GPIO, SPI/SDIO driver symbols, WFx FWIO/BH/HIF/MIB/debug/key/scan/sta/data modules, and firmware startup indication.

Risks and test signals: Risks include probe failure unwind ordering, wakeup GPIO races during boot, PDS absence or corruption, unsupported firmware API, enforced secure-link rejection, IRQ misconfiguration, MAC address fallback/randomization, TDLS feature gating, and bus-driver symbol availability. Tests should cover successful SPI/SDIO probe, firmware timeout, PDS missing vs invalid, API/secure-link rejection, IRQ subscribe failure, mac80211 registration failure, debugfs failure unwind, release path, and module init rollback if second bus registration fails.

Test signals: Source read size: 525 lines, 15880 bytes.
