# sources/cloud-native/moby/daemon/libnetwork/drivers/overlay/encryption_nft_linux.go

Purpose: Implements nftables enforcement for encrypted overlay VNIs as an alternative to legacy iptables rules.

Important APIs and functions: constants define table, chain, set names, and the VXLAN VNI expression. `ensureOverlayEncNftTable` lazily creates the `docker-overlay` table, encrypted VNI set, output route chain that marks matching VXLAN packets, and input raw chain that drops unencrypted matching VXLAN packets. `programOverlayEncVNINft` cleans stale iptables rules, ensures the table, then adds or deletes a VNI set element. `cleanupNft` deletes the entire overlay table on startup when nftables is not the active backend.

Control flow: table creation is protected by `overlayEncNftInitMu` and cached in `overlayEncNftTable`. VNI elements are formatted as 24-bit hex with `vni&0xffffff`.

State and persistence: mutates nftables kernel ruleset and caches an nftables table handle in the driver.

Dependencies and integration points: called from `programOverlayEncryptionFirewall`; depends on `nftables` internal package, `overlayutils.VXLANUDPPort`, and `driver.isIPv6Transport`.

Risks: stale iptables cleanup failures are logged but not fatal. If transport address is unknown, table setup fails. Cached table validity must reflect actual nftables state.

Test signals: no direct nftables tests in this subset.
