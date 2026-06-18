## sources/distributed-fs/lizardfs/src/mount/special_release.cc

Purpose: releases per-open resources for special inodes.

Important APIs: stats release frees snapshot buffer, optionally resets all stats if the file was written, destroys mutex, and frees `sinfo`. Oplog/history release their log handles. Tweaks release parses `name=value` from the accumulated `MagicFile` value and calls `gTweaks.setValue`, then deletes the file object. Masterinfo has no resource beyond logging.

State and dependencies: consumes `fi->fh` state allocated by `special_open`; touches global stats, oplog, and tweaks.

Risks: tweaks apply only on release, so write errors may surface late only via logs. Stats reset is triggered by any write, regardless of content. No dispatch range check. Release must be called exactly once for allocated state.

Test signals: write stats then release resets counters, write tweaks with and without `=`, newline trimming, double/invalid release protection through caller layer, and oplog handle cleanup.
