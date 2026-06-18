# sources/distributed-fs/ceph-client/Documentation/networking/mac80211_hwsim/wpa_supplicant.conf

Purpose: this is a minimal wpa_supplicant configuration for connecting a mac80211_hwsim station to the companion hostapd test AP.

Important APIs, types, and functions: it sets `ctrl_interface=/var/run/wpa_supplicant` and defines one `network` block with `ssid="mac80211 test"`, `psk="12345678"`, `key_mgmt=WPA-PSK`, `proto=WPA2`, `pairwise=CCMP`, and `group=CCMP`.

Control flow: wpa_supplicant parses the network block, scans for the SSID, performs WPA2-PSK authentication and four-way handshake, and then exposes control operations through the configured control interface path.

State and persistence: static config is stored in this file. Runtime state includes scan cache, association state, negotiated keys, and control socket state in `/var/run/wpa_supplicant`.

Dependencies and integration: depends on `wpa_supplicant`, nl80211/cfg80211, a station hwsim interface, and the companion hostapd config using matching SSID/passphrase/ciphers.

Risks: fixed credentials and control path are intended for local testing only. If the hwsim topology or interface names differ, the config alone is insufficient. Test signals include config parse success, association to the hostapd AP, WPA2 handshake completion, and `wpa_cli` visibility through the control interface.
