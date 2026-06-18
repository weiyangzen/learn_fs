# sources/distributed-fs/ceph-client/drivers/net/wireless/mediatek/mt76/testmode.h

## Purpose
Defines the mt76 nl80211 testmode ABI shared by mt76 drivers and user space. It enumerates command attributes, statistics attributes, RX detail attributes, test states, and TX PHY modes.

## Important APIs, Types, And Functions
Important enums are `mt76_testmode_attr`, `mt76_testmode_stats_attr`, `mt76_testmode_rx_attr`, `mt76_testmode_state`, and `mt76_testmode_tx_mode`. `MT76_TM_TIMEOUT` controls common wait timing, and `mt76_tm_policy[]` is declared for the parser in `testmode.c`.

## Control Flow
No executable flow. The enum order defines netlink attribute numbers and therefore is ABI-sensitive. Parser and dumper code use these ids to validate attributes, fill `phy->test`, and emit stats.

## State And Persistence
The header defines externally visible state names such as OFF, IDLE, TX_FRAMES, RX_FRAMES, TX_CONT, and ON. It also defines persistent parameter ids for MTD source, TX count/length/rate/power/timing, frequency offset, driver-specific nested data, and MAC addresses.

## Dependencies And Integration Points
Depends on netlink headers and is included by mt76 core and chip-specific testmode implementations. User-space tools must match the enum values.

## Risks
Reordering existing enum entries would break the ABI. Documentation comments contain a minor duplicated `TX_QUEUED` wording issue for `TX_DONE`, so readers should trust the enum names. New attributes must be appended before the `NUM_*` sentinel.

## Test Signals
ABI compatibility with existing testmode tools, successful parsing of all listed attributes, nested TX power/MAC address handling, and correct dump formatting for common stats.
