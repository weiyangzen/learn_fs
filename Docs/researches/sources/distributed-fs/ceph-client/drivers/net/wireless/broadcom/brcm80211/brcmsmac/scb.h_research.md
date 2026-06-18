# sources/distributed-fs/ceph-client/drivers/net/wireless/broadcom/brcm80211/brcmsmac/scb.h

Purpose: Defines station control block data for per-peer flags, sequence tracking, and AMPDU initiator state.

Important APIs/types: Defines AMPDU TX block-ack window size, max TID count, SCB flags for WME, HT, 40 MHz, and STBC capability, `SCB_MAGIC`, `struct scb_ampdu_tid_ini` with per-window retry counters, `struct scb_ampdu` with aggregate sizing/release/RX-length fields and per-TID initiator arrays, and `struct scb` containing magic, flags, RX duplicate sequence controls, software TX sequence numbers, and AMPDU state.

Control flow and state: No executable flow. The structures persist per-station state across TX/RX processing: duplicate detection, WME priority sequence numbers, AMPDU retry accounting, and negotiated peer capabilities.

Dependencies and integration: Includes Ethernet, Broadcom utility, generic definitions, and common types. Integrates with mac80211 station handling, AMPDU TX/RX logic, rate/STF capability decisions, and per-TID queues. Risks include fixed-size arrays bound to `NUMPRIO` and BA window constants, stale flag state causing wrong HT/STBC decisions, and magic-value checks only being useful where enforced. Test signals include association/teardown, AMPDU session setup/flush, duplicate detection, per-priority sequence progression, and peer capability changes.
