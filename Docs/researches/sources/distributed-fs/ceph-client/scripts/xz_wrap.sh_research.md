# sources/distributed-fs/ceph-client/scripts/xz_wrap.sh

Purpose: `xz_wrap.sh` wraps `xz` for kernel image compression, selecting architecture-appropriate BCJ filters and LZMA2 literal-position options.

Important APIs, types, and functions: `is_enabled()` tests `include/config/auto.conf` for a `CONFIG_* = y` line. The script reads `XZ_VERSION` from `$XZ --robot --version`, sets `ALIGN` and `BCJ` based on `$SRCARCH`, and maps alignment to `LZMA2OPTS`: none for 1-byte, `lp=1` for 2-byte, and `lp=2,lc=2` for 4-byte instruction alignment.

Control flow: the architecture case handles ARM/Thumb2, arm64 with XZ 5.4 arm64 filter gating, csky, loongarch, mips/micromips, parisc, powerpc big-endian filter, riscv compressed ISA with XZ 5.6 filter gating, s390, sh, sparc, x86, and a warning fallback. It then execs `$XZ --check=crc32 --threads=1 $BCJ --lzma2=$LZMA2OPTS,dict=128MiB`.

State and persistence: no internal output file handling; it replaces itself with xz and lets caller-provided stdin/stdout or xz arguments control data flow.

Dependencies and integration points: used by architecture compressed kernel image rules. Depends on `XZ`, `SRCARCH`, generated config, and an xz version whose robot version is numerically comparable.

Risks: missing arch tuning falls back to 2-byte alignment and may reduce compression. New BCJ filters are version-gated by numeric thresholds that must track XZ Utils releases. It forces single-threaded compression for ratio/RAM reasons, affecting build time.

Test signals: run for each supported `SRCARCH` and relevant config combinations, verify chosen command line, and compare decompressor compatibility with `lib/decompress_unxz.c`.
