# sources/distributed-fs/ceph-client/arch/sh/mm/alignment.c

Purpose: tracks unaligned access statistics and exposes user/kernel alignment-fault policy controls.

Important APIs and state: counters `se_user`, `se_sys`, `se_half`, `se_word`, `se_dword`, `se_multi`; policy variables `se_usermode`, `se_kernmode_warn`; exported increment helpers; `unaligned_user_action`, `get_unalign_ctl`, `set_unalign_ctl`, and `unaligned_fixups_notify`.

Control flow: trap handlers increment counters and call policy helpers. `/proc/cpu/alignment` and `/proc/cpu/kernel_alignment` show counts and accept single-digit policy updates.

State and persistence: global counters/policies live until reboot. Per-task unaligned control flags in `thread.flags` can override global warn/signal/fixup behavior.

Dependencies and integration: used directly by `traps_32.c`, prctl unaligned control, procfs, and ratelimited logging.

Risks: proc write accepts only the first byte and does not reject invalid policy combinations beyond the digit range; comments note some combinations are invalid.

Test signals: procfs read/write, prctl UAC flags, unaligned user access fixup/signal behavior, and counter increments.
