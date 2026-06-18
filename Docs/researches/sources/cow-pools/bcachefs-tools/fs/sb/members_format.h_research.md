# File Research: sources/cow-pools/bcachefs-tools/fs/sb/members_format.h

Defines the on-disk member-device format and limits. Important constants include `BCH_SB_MEMBERS_MAX` 256, invalid member sentinel 255, deleted-member UUID, minimum bucket count, member bucket-count cap, and max btree bitmap shift.

`struct bch_member` stores UUID, bucket geometry, flags, IOPS estimates, persistent error counters, sequence, btree allocation bitmap, last journal position, device identity strings, flush errors, and serial. Bitfield macros encode state, discard, allowed data types, disk group, durability, freespace/resize/rotational/initialized flags. Also defines v1 fixed-size entries and v2 variable-size member sections.
