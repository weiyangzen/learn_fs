# sources/distributed-fs/ceph-client/lib/net_utils.c

Purpose: Parses textual MAC addresses into binary Ethernet addresses.

Important APIs/types/functions: Exports `mac_pton(const char *s, u8 *mac)`.

Control flow: Verifies the string is at least `MAC_ADDR_STR_LEN`, validates two hex digits per byte and colon separators between bytes, then converts nibbles with `hex_to_bin`. The output buffer is not modified until validation succeeds.

State and persistence: Stateless.

Dependencies/integration: Uses Ethernet constants, ctype, string, hex helpers, and exported for networking users.

Risks: Accepts strings with additional trailing characters because it only requires minimum length and validates the MAC prefix. Caller must provide at least `ETH_ALEN` output bytes.

Test signals: No local tests; important cases are malformed separators, non-hex characters, short strings, trailing data, and uppercase/lowercase hex.
