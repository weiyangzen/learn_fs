# sources/distributed-fs/ceph-client/drivers/net/wireless/intel/iwlwifi/mei/iwl-mei.h

Purpose: Defines the public iwlwifi-to-iwlmei interface for CSME/SAP ownership arbitration, CSME-provided NVM, RF-kill coordination, netdev datapath sharing, association notifications, and product-reset coordination.

Important APIs and types: Types include `enum iwl_mei_nvm_caps`, `struct iwl_mei_nvm`, pairwise cipher/auth enums, `struct iwl_mei_conn_info`, `struct iwl_mei_colloc_info`, SAP version enum, and callback table `struct iwl_mei_ops`. Real APIs under `CONFIG_IWLMEI` include connection/NVM/ownership queries, RF-kill/NIC/country/power updates, register/unregister, netdev binding, DHCP copy, association/disassociation/device-state notifications, PLDR request, and alive notification. Disabled builds provide stubs.

Control flow: iwlwifi registers callbacks, may request NVM and ownership from CSME, publishes RF-kill/device/netdev state, reports association state, and unregisters in two phases. iwlmei calls back with CSME connection status, RF-kill, roaming restrictions, SAP connection, and NIC stolen events. Datapath hooks allow CSME TX via netdev and selected RX/TX packet forwarding.

State and persistence: Header declares context-free/global API assumptions: only one relevant device, iwlmei owns global module state, and requests may be cached while MEI bus is unavailable. NVM returned by `iwl_mei_get_nvm()` is caller-freed.

Dependencies and integration points: Includes SKB, Ethernet, and ieee80211 headers; integrates iwlwifi PCI/opmode flows with MEI bus SAP implementation, CSME WLAN firmware, mac80211 RF-kill semantics, netdev RX handlers, and NVM parser.

Risks: Calls can sleep and must not originate from iwlmei callbacks. Single-device global context is an architectural constraint. Ownership handoff with active CSME sessions has timing and RF-kill implications. Netdev must be cleared before unregister and waits with `synchronize_net()`. Stubs alter behavior when `CONFIG_IWLMEI` is disabled.

Test signals: Build with and without IWLMEI, registration/unregistration ordering, CSME-owned boot NVM retrieval, ownership request timeout/success, active-session RF-kill flow, netdev set/clear synchronization, DHCP copy to CSME, association/collocated AP reporting, PLDR request before firmware load, and stub behavior.
