# sources/distributed-fs/coda/coda-src/repair/Makefile.am

Purpose: automake recipe for the client-side `repair` program.

Integration: when `BUILD_CLIENT` is enabled, builds `repair` from `repair.cc`/`repair.h`, installs `repair.1`, and includes base, kerndep, util, vicedep, partition, auth, vv, and librepair headers. Link dependencies include client repair libraries (`libclnrepair`, `librepio`), version vectors, auth, kerndep, base, readline, and termcap.

Risks/test signals: ties the `repair` CLI to the librepair outputs researched in this subset. Build/link coverage catches API drift between `repair`, `repio`, and resolve/auth/vv dependencies; behavioral tests require actual Coda conflict scenarios.
