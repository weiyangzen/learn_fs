# sources/distributed-fs/ceph-client/drivers/net/wireless/realtek/rtlwifi/rtl8723ae/hw.h

Purpose: `hw.h` is the public local interface for RTL8723AE hardware operations implemented in `hw.c`. It exposes lifecycle, register, interrupt, beacon, media, rate, security, RF-kill, Bluetooth coexistence, and suspend/resume functions to `sw.c` and adjacent driver modules.

Important APIs/types: prototypes include `rtl8723e_hw_init`, `rtl8723e_card_disable`, `rtl8723e_read_eeprom_info`, `rtl8723e_get_hw_reg`, `rtl8723e_set_hw_reg`, `rtl8723e_interrupt_recognized`, `rtl8723e_enable_interrupt`, `rtl8723e_disable_interrupt`, `rtl8723e_update_interrupt_mask`, network/beacon/QoS setters, rate-table update, `rtl8723e_gpio_radio_on_off_checking`, hardware security and key programming, BT coexistence readers/initializers, and empty suspend/resume hooks. `CHK_SVID_SMID` is a convenience macro for matching EFUSE subsystem IDs in contexts where `rtlefuse` is in scope.

Control flow: the header does not execute logic; it defines the call surface that `rtl_hal_ops` binds into rtlwifi. Hardware initialization and disable run through these APIs, and runtime operations such as scan, association, encryption, and interrupt handling call back into the prototypes.

State and persistence: no state is defined here, but the signatures show the shared state carriers: `struct ieee80211_hw`, `struct rtl_int`, `struct ieee80211_sta`, `enum nl80211_iftype`, and key material parameters. Implementations mutate `rtlpriv`-attached persistent driver and hardware register state.

Dependencies/integration: requires prior inclusion of rtlwifi/mac80211 types. The header is consumed by `sw.c`, `hw.c`, and modules needing hardware hooks. Its function set mirrors `struct rtl_hal_ops` fields in `sw.c`.

Risks: declarations must stay synchronized with `hw.c` and with rtlwifi operation signatures. The `CHK_SVID_SMID` macro depends on an implicit local variable name and can be fragile if reused outside the intended scope. Suspend/resume declarations exist despite no-op implementation.

Test signals: compile coverage is the primary signal. Any rtlwifi API signature changes should fail at build time. Runtime coverage comes from successful probe, suspend/resume callbacks, association, interrupt handling, and encryption operations routed through these declarations.
