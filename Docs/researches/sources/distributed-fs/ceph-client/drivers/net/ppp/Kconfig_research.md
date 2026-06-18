# sources/distributed-fs/ceph-client/drivers/net/ppp/Kconfig

Purpose: Defines the build-time feature matrix for PPP core support, PPP compressors/encryption, PPP transports, filtering, multilink, and tty line disciplines.

Important symbols: `PPP` is the parent tristate and selects `SLHC`. `PPP_BSDCOMP`, `PPP_DEFLATE`, and `PPP_MPPE` enable BSD-Compress, Deflate, and MPPE CCP modules; Deflate selects zlib inflate/deflate, and MPPE selects ARC4/SHA1 crypto libraries. `PPP_FILTER` gates BPF pass/active filter support in `ppp_generic.c`. `PPP_MULTILINK` gates RFC 1990 bundle code. `PPPOATM`, `PPPOE`, `PPTP`, and `PPPOL2TP` configure transport modules with ATM, GRE demux, or L2TP dependencies. Under `if TTY`, `PPP_ASYNC` selects `CRC_CCITT` and `PPP_SYNC_TTY` enables frame-oriented sync tty PPP.

Control flow and state: All child options are nested under `if PPP`, so no PPP compressor, transport, filter, multilink, or tty mode is exposed without the generic layer. PPPoE hash-size choice derives integer `PPPOE_HASH_BITS`. Kconfig state persists in `.config` and changes which code blocks compile, especially `CONFIG_PPP_FILTER` and `CONFIG_PPP_MULTILINK` inside `ppp_generic.c`.

Dependencies and integration points: Integrates with Kbuild, tty, ATM, L2TP, GRE demux, zlib, crypto, CRC, and SLHC. Help text documents expected userspace such as `pppd`, RP-PPPoE, PPTP plugins/daemons, and tunneled L2TP/ATM stacks.

Risks and test signals: The `PPP_BSDCOMP` help says it is always compiled as a module, but the symbol is a normal tristate in this tree. Missing line discipline or compressor options surface later as failed pppd operations or `ppp-compress-*` autoload failures. Test build matrices for `PPP=y/m`, each compressor, filters, multilink, TTY disabled, transport dependency absence/presence, and PPPoE hash-bit choices.
