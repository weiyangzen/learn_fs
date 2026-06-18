# sources/distributed-fs/ceph-client/drivers/net/ethernet/sfc/ethtool.c

Purpose: Provides the main `ethtool_ops` table and local SFC implementations for LED identification, register dumps, interrupt coalescing, ring sizing, Wake-on-LAN, FEC stats, timestamp info, and integration with common ethtool helpers.

Important APIs and functions: `efx_ethtool_ops` is exported through `efx.h`. Local helpers include `efx_ethtool_phys_id()`, `efx_ethtool_get_regs_len()`, `efx_ethtool_get_regs()`, coalesce get/set, ringparam get/set, WOL get/set, FEC stats, and timestamp info. Many operations delegate to `ethtool_common.h`, filters, RSS, module EEPROM, link settings, selftest, and stats helpers.

Control flow: Coalesce get reads current IRQ moderation; set interprets standard and legacy irq fields, allows RX to override TX only when TX was unchanged on shared channels, calls `efx_init_irq_moderation()`, then pushes moderation to every channel. Ringparam set validates RX/TX bounds, raises TX size to `EFX_TXQ_MIN_ENT()` if needed, and calls `efx_realloc_channels()` to rebuild queues. LED identify maps ethtool states to MCDI LED modes. Timestamp info defaults to TX software timestamping then augments via PTP helper.

State and persistence: Mutates IRQ moderation fields, channel hardware timer state, queue entry counts through channel reallocation, WOL configuration through NIC type callbacks, and LED state. Settings are runtime or firmware-backed depending on callback.

Dependencies and integration points: Uses `efx_channels.c` for moderation and channel reallocation, `efx_common.c` for feature/MTU interactions indirectly, NIC type callbacks for registers/WOL/FEC, MCDI LED control, PTP timestamp helpers, RSS/filter ethtool common code, and Linux ethtool ABI.

Risks: Shared RX/TX channels cannot support independent moderation unless RX override is allowed. Ring resize stops datapath and can fail or roll back. TX maximum depends on EF10 workaround-adjusted limits. Unsupported ethtool fields are intentionally ignored for compatibility, which may surprise tools expecting strict validation.

Test signals: `ethtool -c/-C`, shared vs separate TX channels, invalid coalesce/ring values, ring resize under traffic, register dump length/content, LED identify states, WOL get/set, timestamp info with PTP, FEC stats, RSS context operations, and selftest/stat string coverage.
