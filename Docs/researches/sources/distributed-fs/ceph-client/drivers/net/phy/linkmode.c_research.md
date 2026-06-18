<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/linkmode.c -->
# sources/distributed-fs/ceph-client/drivers/net/phy/linkmode.c

## Purpose
`linkmode.c` provides common helpers for pause-frame advertisement and resolution using ethtool linkmode bitmaps. It is a small shared utility used by PHY and MAC code that needs IEEE 802.3 pause/asymmetric pause negotiation behavior.

## Important APIs, Types, And Functions
The exported APIs are `linkmode_resolve_pause()` and `linkmode_set_pause()`, both exported GPL. They operate on ethtool link mode masks and standard bits `ETHTOOL_LINK_MODE_Pause_BIT` and `ETHTOOL_LINK_MODE_Asym_Pause_BIT`.

## Control Flow
`linkmode_resolve_pause()` computes the intersection of local and partner advertisements. If both advertise symmetric pause, it enables TX and RX pause. If only asymmetric pause intersects, it enables TX pause when the partner advertises Pause and RX pause when the local side advertises Pause. Otherwise, it disables both directions.

`linkmode_set_pause()` translates ethtool `tx`/`rx` pause booleans into advertised Pause and Asym_Pause bits: Pause follows RX capability, and Asym_Pause is set when TX and RX differ. The comments document why this mapping is imperfect but conventional.

## State And Persistence
The file has no persistent state. All behavior is pure bitmap transformation through caller-provided masks and output booleans.

## Dependencies And Integration Points
It depends on `linux/linkmode.h` and ethtool link mode bit definitions. It integrates with PHYLIB pause resolution, MAC pause configuration, and autonegotiation advertisement setup.

## Risks
The main risk is semantic confusion between local TX/RX pause capability and IEEE Pause/AsymDir advertisement rules. `linkmode_resolve_pause()` assumes the provided bitmaps are already valid negotiated advertisements. `linkmode_set_pause()` intentionally cannot guarantee all requested unidirectional outcomes with every partner advertisement.

## Test Signals
Unit-style tests should enumerate all combinations of local/partner Pause and Asym_Pause bits and compare output with the documented table. Advertisement tests should verify the four `tx`/`rx` inputs map to expected Pause/Asym_Pause bit states and that unrelated linkmode bits are preserved.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/phy/linkmode.c -->
