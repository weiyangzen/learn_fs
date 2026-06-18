<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/crypto/Kconfig

## Purpose

`drivers/crypto/Kconfig` is the top-level hardware crypto configuration menu. It gates all hardware crypto devices under `CRYPTO_HW`, sources vendor submenus, and declares many platform accelerator options and their crypto API dependencies.

## Important APIs, Types, And Functions

This file is declarative Kconfig. It defines `menuconfig CRYPTO_HW`, sources `drivers/crypto/allwinner/Kconfig`, and includes options for PadLock, s390 protected keys, Talitos, OMAP, Atmel, CCP, QCE, Rockchip, Tegra, Xilinx, Safexcel, CCREE, TI, and other drivers. Each config selects needed crypto primitives such as `CRYPTO_SKCIPHER`, `CRYPTO_HASH`, `CRYPTO_ENGINE`, `CRYPTO_AES`, `CRYPTO_SHA*`, `HW_RANDOM`, or fallback libraries.

## Control Flow

Build configuration flows from enabling `CRYPTO_HW`; if disabled, the submenu and all nested hardware drivers are skipped. Selected options then control Makefile object inclusion and compile-time feature branches in individual drivers.

## State And Persistence Behavior

Kconfig has no runtime state, but selected symbols persist in `.config` and determine which modules, algorithms, debug features, RNG providers, and fallback dependencies exist in the kernel image.

## Dependencies And Integration Points

It integrates architecture symbols, platform dependencies, crypto API algorithm selections, hwrng, debugfs-dependent debug options, and sourced vendor Kconfig files.

## Risks And Test Signals

Risks include missing `select` dependencies causing link or runtime algorithm failures, overly broad defaults, impossible dependency combinations, and vendor submenu omissions. Test with randconfig/allmodconfig, architecture-specific builds, and verifying requested algorithms register when each driver is enabled.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/Kconfig -->
