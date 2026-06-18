<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/reg.h -->
# sources/distributed-fs/ceph-client/drivers/net/wireless/ath/reg.h

Purpose: Defines shared ath hardware register offsets and bit fields used by common BSSID, counter, and key-cache helpers.

Important APIs/types/functions: Provides `AR_MIBC` flags, station ID registers, BSSID mask registers, cycle counter registers, key table base/address macros, key cache size, reserved WEP entries, key type constants, valid bit, and key/MAC register address macros.

Control flow: No executable flow; macro expansion is used by `hw.c` and `key.c`.

State and persistence: Defines hardware register interface constants only.

Dependencies and integration points: Consumed by ath common hardware helpers and hardware-specific drivers that implement register read/write ops.

Risks and test signals: Risks are incorrect offsets or bit definitions causing hardware misprogramming. Test signals include successful key programming, BSSID mask behavior, and sane cycle counter reads across ath hardware families.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/net/wireless/ath/reg.h -->
