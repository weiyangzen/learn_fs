# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt7615/usb_mcu.c

Purpose: USB-specific MCU message transport and power-on sequence for MT7663U.

Important APIs and functions: `mt7663u_mcu_send_message()` fills mt7615 MCU descriptors, selects in-band command or firmware scatter endpoint, prepends USB length, pads to required alignment, sends a bulk message, and frees the skb. `mt7663u_mcu_power_on()` issues the vendor power-on request and polls firmware power state. `mt7663u_mcu_init()` installs USB MCU ops, enables firmware download routing, restarts/powers on firmware when recovering from power-off, loads firmware, disables firmware download routing, and marks MCU running.

Control flow: USB probe may call power-on before queue allocation. Later async MCU work calls `mt7663u_mcu_init()`, which sets mt76 MCU headroom/tailroom and send/parse ops, handles prior power-off state, loads firmware via `__mt7663_load_firmware()`, then sets `MT76_STATE_MCU_RUNNING`.

State and persistence: Updates UDMA firmware-download register bit, `MT76_STATE_POWER_OFF`, `MT76_STATE_MCU_RUNNING`, and firmware memory contents. No persistent storage.

Dependencies: mt76 USB bulk/vendor helpers, mt7615 MCU fill/parse, common firmware loader, USB/UDMA register definitions, and firmware power state constants from `mcu.h`.

Risks: Endpoint selection must keep firmware scatter packets on the data endpoint and normal commands on in-band command endpoint. Padding/length framing is USB ABI. `mt7663u_mcu_power_on()` sets an error on timeout but returns 0 in the current code, which can mask a power-on failure signal. Firmware download routing must be cleared after load.

Test signals: MCU command replies over USB, firmware scatter load, power-on polling behavior, firmware restart from power-off, and command timeout absence after init.
