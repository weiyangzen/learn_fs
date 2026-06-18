# File Research: sources/block-storage/bcache-tools/Makefile

The top-level Makefile builds `make-bcache`, `probe-bcache`, `bcache-super-show`, `bcache-register`, and `bcache`; `bcache-test` has dependencies but is not part of `all`. It installs administrative tools under `${PREFIX}/sbin`, helper programs under `${UDEVLIBDIR}`, rules under `${UDEVLIBDIR}/rules.d`, man pages, and initramfs/dracut integration files.

Build dependencies are explicit through `pkg-config`: `make-bcache` and `bcache` use `uuid`/`blkid`, `bcache-super-show` uses `uuid`, and `bcache-test` uses OpenSSL plus libm. Shared object reuse is simple: `crc64.o`, `lib.o`, `make.o`, `zoned.o`, `features.o`, and `show.o` back the command variants.
