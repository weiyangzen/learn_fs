# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/ath9k/reg_wow.h

## Purpose
`reg_wow.h` is the ath9k Wake-on-Wireless register definition header. It defines pattern memory, pattern-length registers, wake status bits, keep-alive and beacon-miss controls, software WoW control bits, transmit-buffer windows, and supported pattern masks used by the hardware WoW implementation.

## Important APIs, types, and constants
Important definitions include `AR_WOW_PATTERN`, `AR_WOW_COUNT`, `AR_WOW_BCN_EN`, `AR_WOW_BCN_TIMO`, `AR_WOW_KEEP_ALIVE*`, `AR_WOW_PATTERN_MATCH`, `AR_WOW_LENGTH1..4`, `AR_SW_WOW_CONTROL`, wake enable/status bits such as `AR_WOW_MAGIC_EN`, `AR_WOW_PATTERN_EN`, `AR_WOW_MAGIC_PAT_FOUND`, `AR_WOW_KEEP_ALIVE_FAIL`, and `AR_WOW_BEACON_FAIL`, plus `AR_WOW_TB_PATTERN`, `AR_WOW_TB_MASK`, and length-mask helpers for 16 patterns.

## Control flow and integration
No functions are defined. HAL WoW routines use the masks to write packet patterns and masks into transmit-buffer memory, set length fields, enable magic/user/beacon/keepalive wake sources, and clear wake events during resume. `wow.c` maps cfg80211 triggers into HAL-level WoW trigger bits that eventually use these register definitions.

## State and persistence behavior
WoW state persists in low-power hardware while the host sleeps. Pattern contents, masks, enable bits, keepalive timers, beacon miss thresholds, and wake status bits remain relevant across suspend until resume clears or reinitializes them.

## Dependencies
This header depends on ath9k HAL WoW code for interpretation. The file assumes pattern count and size constants from the driver/HAL and must be matched to chip generation because legacy devices support fewer patterns than newer ones.

## Risks
Risks include incorrect pattern length packing, enabling unsupported pattern slots, failing to clear stale wake status, and mismatched mask semantics that cause false wakes or missed disassociation/magic-packet wakes. Because these registers operate during system sleep, failures can be hard to diagnose after resume.

## Test signals
Test signals include suspend with magic packet, user pattern, beacon miss, and deauth/disassoc wake triggers; validating wake reason bits on resume; repeated suspend/resume cycles; and ensuring unsupported pattern slots are not exposed through wiphy WoW capabilities.
