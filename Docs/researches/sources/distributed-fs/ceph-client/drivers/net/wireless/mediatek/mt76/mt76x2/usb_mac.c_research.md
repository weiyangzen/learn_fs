# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/mt76x2/usb_mac.c

Purpose: USB-specific MAC reset, crystal trim, timing, and stop sequencing for MT76x2U devices.

Important APIs: `mt76x2u_mac_reset` and `mt76x2u_mac_stop`. Internal `mt76x2u_mac_fixup_xtal` interprets EEPROM crystal trim fields and programs XO/FCE/timing registers.

Control flow: reset enables WPDMA bits, initializes PBF limits and common MAC defaults, configures TX link, auto response, max length, WMM, clears MAC/BBP reset, disables coexistence for MT7612, enables CCA settings, disables ALC bit 31, then applies XTAL fixups. Stop temporarily removes RTS retry limit, disables ED CCA/40 MHz TX hold, polls USB TX DMA idle, waits TX page counts, disables MAC TX/RX, waits MAC idle, toggles BBP reset bits if needed, waits RX page counts and MAC RX idle, then waits USB RX DMA idle and restores RTS config.

State and persistence: persistent trim values come from EEPROM. Runtime state includes removed-device bit, TX/RX DMA busy state, queue page counters, MAC status, and restored RTS configuration.

Dependencies and integration: called during hardware init, channel switching, stop, cleanup, suspend/resume, and calibration. Uses common mt76x02 MAC init tables and raw mt76 register helpers.

Risks: stop loops are hardcoded polling sequences; too-short waits can leave DMA active, too-long waits can stall teardown. XTAL fallback values affect RF stability. The function returns success even after warning that MAC RX failed to stop, so callers need external recovery if hardware is wedged.

Test signals: repeated start/stop, channel switch under load, device removal during stop, suspend/resume, MT7612 coexistence behavior, and observation of no leaked URBs or stuck DMA after teardown.
