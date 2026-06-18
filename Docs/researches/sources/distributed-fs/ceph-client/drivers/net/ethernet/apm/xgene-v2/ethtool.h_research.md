## sources/distributed-fs/ceph-client/drivers/net/ethernet/apm/xgene-v2/ethtool.h

Purpose: defines v2 ethtool statistic mapping structures, MAC statistics register offsets, and the ethtool installation prototype.

Important APIs, types, and functions: `struct xge_gstrings_stats` stores an ethtool stat name and structure offset. `struct xge_gstrings_extd_stats` stores an ethtool stat name, CSR address, and sampled value. Register constants cover RX/TX size buckets, multicast/broadcast counters, pause/control frames, alignment/FCS/length errors, drops, jabbers, overruns, underruns, and fragments. It declares `xge_set_ethtool_ops`.

Control flow, state, and dependencies: included through `main.h`; no runtime state lives here. `ethtool.c` uses the offsets to build ethtool string and value arrays.

Integration points: offsets must match MAC counter registers used by the v2 hardware block and must remain aligned with the names array in `ethtool.c`.

Risks: wrong addresses silently report bad diagnostics. Adding/removing counters requires updating count/string/value logic together.

Test signals: `ethtool -S` should print stable names and plausible increments under directed traffic and error injection.
