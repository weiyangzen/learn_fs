# sources/distributed-fs/ceph-client/Documentation/networking/mac80211_hwsim/hostapd.conf

Purpose: this is a minimal hostapd configuration for mac80211_hwsim testing. It starts a WPA2-PSK access point on simulated interface `wlan0`.

Important APIs, types, and functions: hostapd keys include `interface=wlan0`, `driver=nl80211`, `hw_mode=g`, `channel=1`, `ssid=mac80211 test`, `wpa=2`, `wpa_key_mgmt=WPA-PSK`, `wpa_pairwise=CCMP`, and `wpa_passphrase=12345678`.

Control flow: hostapd consumes this declarative file at startup, opens the nl80211 driver backend for `wlan0`, configures 2.4 GHz channel 1, advertises the SSID, and enables WPA2 personal authentication with CCMP.

State and persistence: the file itself is static. Runtime AP state, beaconing, association tables, and keys are held by hostapd and the mac80211_hwsim kernel module while the process is running.

Dependencies and integration: depends on `hostapd`, nl80211, cfg80211/mac80211, and a hwsim radio exposed as `wlan0`. It pairs with the sibling `wpa_supplicant.conf`, which uses the same SSID and passphrase.

Risks: fixed interface name, channel, SSID, and weak test passphrase make it suitable only for controlled test namespaces/labs. Interface naming may differ when multiple hwsim radios exist. Test signals include hostapd parsing, AP startup on `wlan0`, beacon visibility, and successful WPA2 association from the paired supplicant config.
