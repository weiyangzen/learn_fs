# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2841er.h

## Purpose
Public attachment and configuration interface for the Sony CXD2841ER-family demodulator. It lets board/frontend drivers describe the I2C address, crystal frequency, and feature flags before attaching satellite or terrestrial/cable frontend variants.

## Important APIs, Types, and Functions
Defines feature flags such as `CXD2841ER_USE_GATECTRL`, `CXD2841ER_AUTO_IFHZ`, `CXD2841ER_TS_SERIAL`, `CXD2841ER_ASCOT`, `CXD2841ER_EARLY_TUNE`, `CXD2841ER_NO_WAIT_LOCK`, `CXD2841ER_NO_AGCNEG`, and `CXD2841ER_TSBITS`. `enum cxd2841er_xtal` enumerates 20.5, 24, and 41 MHz crystals. `struct cxd2841er_config` carries `i2c_addr`, `xtal`, and `flags`. Exported attach APIs are `cxd2841er_attach_s()` and `cxd2841er_attach_t_c()`, with inline disabled stubs when `CONFIG_DVB_CXD2841ER` is not reachable.

## Control Flow
The header has no runtime control flow; callers include it, fill `struct cxd2841er_config`, and call the appropriate attach routine. Kconfig reachability selects either real declarations or warning stubs returning `NULL`.

## State and Persistence
The only state is caller-owned configuration passed to the driver during attach. No persistent data is stored here.

## Dependencies and Integration Points
It depends on Linux DVB frontend APIs and I2C adapter types. Integration is with board drivers that compose demodulator frontends and optionally tuner gate/transport-stream behavior through flags.

## Risks and Edge Cases
Flag bits are positional ABI between board code and the implementation; reusing bits can silently change hardware setup. Disabled stubs require callers to handle `NULL`. The comment says CXD2441ER, likely a typo for this CXD2841ER family.

## Test Signals
Build with `CONFIG_DVB_CXD2841ER=y/m/n`, attach users under each mode, and verify valid boards create frontend objects while disabled builds produce only the expected warning path and no unresolved symbols.
