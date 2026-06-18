# subset-b-004056 research

This grouped report covers Sony CXD2841ER public/internal headers and the Sony CXD2880 DVB-T/T2 SPI tuner-demodulator frontend support under `sources/distributed-fs/ceph-client/drivers/media/dvb-frontends`. Each section preserves the original source path for reconciliation into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2841er.h -->
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
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2841er.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2841er_priv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2841er_priv.h

## Purpose
Internal constants and small data types shared by the CXD2841ER implementation. It identifies logical I2C register banks, supported chip IDs, DVB-S polling interval, CNR lookup entries, and DVB-T2 profile choices.

## Important APIs, Types, and Functions
Defines `I2C_SLVX` and `I2C_SLVT` bank selectors. Chip IDs include `CXD2837ER_CHIP_ID`, `CXD2838ER_CHIP_ID`, `CXD2841ER_CHIP_ID`, `CXD2843ER_CHIP_ID`, and `CXD2854ER_CHIP_ID`. `CXD2841ER_DVBS_POLLING_INVL` defines a 10 ms polling interval. `struct cxd2841er_cnr_data` maps raw values to `cnr_x1000`. `enum cxd2841er_dvbt2_profile_t` represents any/base/lite profile selection.

## Control Flow
No executable flow is present. Implementation files use these constants to branch on detected silicon and select standard-specific monitor/tune behavior.

## State and Persistence
No persistent state. The CNR table element type is used for static lookup tables in implementation code.

## Dependencies and Integration Points
This private header is intended for CXD2841ER driver internals, not board code. The chip IDs integrate with device detection and capability selection.

## Risks and Edge Cases
Incorrect chip IDs can reject valid hardware or enable wrong register sequences. The profile enum values need to match the implementation and any frontend delivery-system mapping. Polling interval changes can affect tune latency and CPU wakeups.

## Test Signals
Exercise device identification across all listed chip variants, DVB-S polling timeout paths, and DVB-T2 base/lite profile selection. Compile should reveal accidental external users if the private header becomes inconsistent.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2841er_priv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/Kconfig -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/Kconfig

## Purpose
Declares the `DVB_CXD2880` tristate option for the Sony CXD2880 DVB-T2/T tuner plus demodulator frontend driver.

## Important APIs, Types, and Functions
The key Kconfig symbol is `DVB_CXD2880`. It depends on `DVB_CORE` and `SPI`, defaults to module when media subdriver autoselection is disabled, and exposes help text for frontend support.

## Control Flow
Kconfig visibility and selection determine whether the CXD2880 object list in the Makefile is built into the kernel, emitted as a module, or omitted.

## State and Persistence
The selected tristate value persists in the kernel `.config`. Runtime demodulator state is not handled here.

## Dependencies and Integration Points
The SPI dependency matches the driver's `struct spi_device` transport. `DVB_CORE` provides frontend registration and media subsystem integration. The symbol controls the `IS_REACHABLE()` branch in `cxd2880.h`.

## Risks and Edge Cases
Missing dependencies could expose build failures; overly strict dependencies could hide compile-test coverage. The default `m` behavior changes module composition when autoselection is disabled.

## Test Signals
Run `olddefconfig`, `allmodconfig`, and builds with `DVB_CORE` or `SPI` disabled. Confirm `CONFIG_DVB_CXD2880=m` produces the expected `cxd2880` module and disabled builds use the attach stub.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/Kconfig -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/Makefile -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/Makefile

## Purpose
Defines the composite object list for the CXD2880 frontend module and maps it to `CONFIG_DVB_CXD2880`.

## Important APIs, Types, and Functions
`cxd2880-objs` includes common helpers, SPI device I/O, integration helpers, register I/O, tuner/demod common control, DVB-T/T2 tuning, DVB-T/T2 monitor code, generic monitor code, and `cxd2880_top.o`. `obj-$(CONFIG_DVB_CXD2880) += cxd2880.o` is the Kbuild entry point.

## Control Flow
Kbuild links the listed objects into one built-in or modular driver depending on the Kconfig tristate.

## State and Persistence
There is no runtime state. Persistent effect is build artifact composition.

## Dependencies and Integration Points
The object list is coupled to headers and exported functions across the CXD2880 directory. `cxd2880_top.o` provides DVB frontend glue that consumes lower-level control and monitor APIs.

## Risks and Edge Cases
Missing an object can produce unresolved symbols or silently remove functionality from the module. Formatting lacks spaces before continuations on two lines, but Kbuild still parses them; edits should preserve valid continuation syntax.

## Test Signals
Build `drivers/media/dvb-frontends/cxd2880/` with `CONFIG_DVB_CXD2880=m/y`, run `modinfo cxd2880`, and verify no undefined references from monitor or tuning helpers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/Makefile -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880.h

## Purpose
Public board-driver interface for attaching a CXD2880 SPI-based DVB frontend to an existing `struct dvb_frontend`.

## Important APIs, Types, and Functions
`struct cxd2880_config` carries the SPI device and an external mutex for exclusive SPI access. `cxd2880_attach()` returns a `struct dvb_frontend *` when the driver is reachable. Disabled builds provide an inline warning stub returning `NULL`.

## Control Flow
Caller code prepares `struct cxd2880_config`, including transport synchronization, and calls `cxd2880_attach()`. Kconfig reachability controls whether the real attach declaration or stub is compiled.

## State and Persistence
The header only defines attach-time configuration. The pointed-to SPI device and mutex are externally owned and must outlive the attached frontend.

## Dependencies and Integration Points
Integrates Linux SPI and DVB frontend code. The mutex is a cross-driver coordination point for bus transactions.

## Risks and Edge Cases
The header does not include SPI or DVB declarations directly, so include order must provide complete types where needed. A missing or shared incorrectly mutex risks SPI races. Disabled stubs require robust `NULL` handling by callers.

## Test Signals
Compile attach callers with `CONFIG_DVB_CXD2880` enabled and disabled. Runtime tests should verify attach fails cleanly on missing SPI context and that concurrent frontend operations serialize on the supplied mutex.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_common.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_common.c

## Purpose
Implements a shared numeric helper for converting register bitfields encoded as two's-complement values into signed integers.

## Important APIs, Types, and Functions
`cxd2880_convert2s_complement(u32 value, u32 bitlen)` returns `value` as a signed integer, sign-extending from `bitlen` when `1 <= bitlen < 32`.

## Control Flow
The helper treats `bitlen == 0` or `bitlen >= 32` as already full-width. Otherwise it checks the sign bit, ORs high bits with `GENMASK(31, bitlen)` for negative values, and masks low bits for positive values.

## State and Persistence
No state. It is pure computation.

## Dependencies and Integration Points
Uses `GENMASK()` from kernel bit helpers via `cxd2880_common.h`. Monitor code uses it for RF level, carrier offset, sampling offset, and other signed register values.

## Risks and Edge Cases
Callers must pass the correct field width; wrong widths invert signs or scale readings incorrectly. The `1 << (bitlen - 1)` expression is safe only because bitlen is guarded against zero and 32+.

## Test Signals
Unit-style checks for widths 1, 8, 11, 27, 31, plus zero and 32. Runtime monitor values should change sign correctly around the hardware sign bit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_common.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_common.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_common.h

## Purpose
Central common include for CXD2880 files, collecting kernel utility headers and the two's-complement conversion prototype.

## Important APIs, Types, and Functions
Includes Linux `types`, `errno`, `delay`, `bits`, and `string` headers. Declares `cxd2880_convert2s_complement()`.

## Control Flow
No control flow. It is used by most CXD2880 headers and implementation files.

## State and Persistence
No state.

## Dependencies and Integration Points
By centralizing common Linux includes, it makes low-level driver files rely on one local header for basic types, error codes, sleeps, masks, and memory helpers.

## Risks and Edge Cases
Because many files transitively depend on it, removing includes can cause broad compile failures. Adding heavy includes here increases rebuild and dependency surface.

## Test Signals
Full CXD2880 build and include-order tests for each header compiled from a clean translation unit.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_common.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_devio_spi.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_devio_spi.c

## Purpose
Adapts the generic CXD2880 register I/O abstraction to the chip's SPI command protocol.

## Important APIs, Types, and Functions
`cxd2880_io_spi_create()` installs SPI-backed `read_regs`, `write_regs`, and `write_reg` callbacks into `struct cxd2880_io`. Static helpers `cxd2880_io_spi_read_reg()` and `cxd2880_io_spi_write_reg()` encode commands. `BURST_WRITE_MAX` limits writes to 128 payload bytes.

## Control Flow
Read validates arguments and 8-bit address range, chooses command `0x0b` for SYS or `0x0a` for DMD, then loops in chunks up to 255 bytes through `spi->write_read()`. Write validates size and address range, chooses `0x0f` for SYS or `0x0e` for DMD, appends an extra dummy byte for SYS writes, and calls `spi->write()`.

## State and Persistence
`cxd2880_io_spi_create()` stores the SPI backend pointer, slave select, and zeroes unused I2C address fields. Runtime register state is in hardware.

## Dependencies and Integration Points
Depends on `struct cxd2880_spi` callbacks and generic `cxd2880_io` users in tuner/demod code. It bridges bus-level SPI access to register-bank operations.

## Risks and Edge Cases
Write rejects sizes above 128 despite loop code supporting chunking; callers must split larger sequences. `sub_address + size > 0x100` protects only 8-bit register windows. Missing `spi->write_read` or `spi->write` callback would crash because the helper only checks `io->if_object`.

## Test Signals
SPI trace should show the expected command bytes for SYS/DMD reads and writes, address wrap rejection, 255-byte read chunking, 128-byte write limit, and correct propagation of transport errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_devio_spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_devio_spi.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_devio_spi.h

## Purpose
Declares the SPI-backed constructor for the CXD2880 generic I/O interface.

## Important APIs, Types, and Functions
Includes common, I/O, SPI, and tuner-demod headers. Declares `cxd2880_io_spi_create(struct cxd2880_io *io, struct cxd2880_spi *spi, u8 slave_select)`.

## Control Flow
No executable flow. Consumers call the constructor before creating or initializing `struct cxd2880_tnrdmd`.

## State and Persistence
No state in the header. The constructor populates caller-owned `struct cxd2880_io`.

## Dependencies and Integration Points
Connects SPI transport setup to all demod register access. `cxd2880_top.c` and initialization glue depend on this constructor to wire hardware access.

## Risks and Edge Cases
The unused `slave_select` field may imply support not present in the SPI command code. Include cycles should be watched because it includes `cxd2880_tnrdmd.h` though only I/O and SPI types are needed for the prototype.

## Test Signals
Compile users that include only this header plus required kernel SPI/DVB headers. Runtime attach should fail cleanly if construction receives null pointers.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_devio_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dtv.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dtv.h

## Purpose
Defines generic digital-TV system and bandwidth enums shared by CXD2880 DVB-T and DVB-T2 code.

## Important APIs, Types, and Functions
`enum cxd2880_dtv_sys` covers unknown, DVB-T, DVB-T2, and any. `enum cxd2880_dtv_bandwidth` covers unknown plus 1.7, 5, 6, 7, and 8 MHz values encoded mostly by MHz number.

## Control Flow
No executable flow. Tuning paths switch on these enums to choose standard-specific register programming and validation.

## State and Persistence
Values are stored in `struct cxd2880_tnrdmd` as current tuned system and bandwidth.

## Dependencies and Integration Points
Used by tune parameter structures, common tune helpers, state tracking, and frontend conversion from Linux delivery-system/cache values.

## Risks and Edge Cases
The enum does not include all DVB-T2 bandwidth encodings present in low-level DVB-T2 definitions, such as 10 MHz, so frontend mapping must constrain supported values. Unknown/any must not be sent into hardware programming paths that expect concrete standards.

## Test Signals
Tune attempts for every supported bandwidth, rejection of unknown/unsupported bandwidths, and correct persisted state after successful DVB-T and DVB-T2 tune flows.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dtv.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dvbt.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dvbt.h

## Purpose
Defines DVB-T modulation, hierarchy, coding, guard, FFT mode, profile, and TPS information structures for CXD2880 monitor and tuning code.

## Important APIs, Types, and Functions
Enums model DVB-T constellation, hierarchy, code rates, guard intervals, 2K/8K modes, and high/low priority profiles. `struct cxd2880_dvbt_tpsinfo` contains decoded TPS fields including constellation, hierarchy, HP/LP rates, guard, mode, frame number, length indicator, cell ID, and reserved bits.

## Control Flow
No executable flow. Monitor code fills these types from registers; tune code selects profile.

## State and Persistence
These types are transient result containers. Active profile selection influences hardware registers during tune.

## Dependencies and Integration Points
Used by `cxd2880_tnrdmd_dvbt.c`, `cxd2880_tnrdmd_dvbt_mon.c`, and higher-level frontend statistic/property conversion.

## Risks and Edge Cases
Reserved enum values are represented explicitly; consumers must not treat them as valid modulation settings. TPS lock must be verified before trusting decoded fields.

## Test Signals
Known DVB-T streams with each constellation/rate/guard/mode combination, HP/LP profile selection tests, and invalid TPS lock scenarios returning errors rather than stale data.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dvbt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dvbt2.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dvbt2.h

## Purpose
Defines DVB-T2 protocol enums and decoded signalling structures used by CXD2880 T2 tune and monitor paths.

## Important APIs, Types, and Functions
Enums cover profile, T2 version, S1/S2 signalling, guard, FFT mode, bandwidth code, L1 pre/post fields, PAPR, pilot pattern, PLP code rate/constellation/type/payload/FEC/mode, stream type, and PLP base/common selectors. Structures include `cxd2880_dvbt2_l1pre`, `cxd2880_dvbt2_plp`, `cxd2880_dvbt2_l1post`, `cxd2880_dvbt2_ofdm`, and `cxd2880_dvbt2_bbheader`.

## Control Flow
No direct flow. Monitor functions decode register blocks into these structures; tuning functions use profile and PLP fields to program selection.

## State and Persistence
Result structures are caller-owned snapshots of broadcast signalling. Profile and PLP selection can be persisted in tuner-demod active state through tune calls.

## Dependencies and Integration Points
Used heavily by `cxd2880_tnrdmd_dvbt2.c` and `cxd2880_tnrdmd_dvbt2_mon.c`, plus frontend glue converting monitor output into DVB core statistics.

## Risks and Edge Cases
Many reserved/unknown enum values must be handled explicitly. PLP arrays and counts need bounds checks against the DVB-T2 maximum and caller buffers. Mixed base/lite or MISO/SISO signalling affects diversity behavior and FEF settings.

## Test Signals
Streams covering base, lite, auto profile, multiple PLPs, common/data PLPs, rotated constellations, in-band signalling, and malformed/reserved L1 fields. Monitor output should match known transport metadata.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_dvbt2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_integ.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_integ.c

## Purpose
Provides integration-layer helpers that sequence low-level initialization and expose cancellation for long-running operations.

## Important APIs, Types, and Functions
`cxd2880_integ_init()` runs `cxd2880_tnrdmd_init1()`, polls `cxd2880_tnrdmd_check_internal_cpu_status()` until internal CPU tasks complete, then calls `cxd2880_tnrdmd_init2()`. `cxd2880_integ_cancel()` sets `tnr_dmd->cancel`. `cxd2880_integ_check_cancellation()` returns `-ECANCELED` if cancellation is set.

## Control Flow
Initialization polls every 10 ms with `usleep_range()` and times out after 500 ms using `ktime_get()`. Any low-level error aborts immediately.

## State and Persistence
Uses the atomic `cancel` field in `struct cxd2880_tnrdmd`; the flag persists until reset by initialization or caller behavior. Hardware init state is advanced by low-level functions.

## Dependencies and Integration Points
Depends on tuner-demod core and monitor CPU status APIs. Higher-level tune/scan code can call cancellation checks while waiting for locks.

## Risks and Edge Cases
Timeout tuning is hardware-sensitive; too low can reject slow startup, too high slows failure. Cancellation is not automatically checked inside `cxd2880_integ_init()` itself. The atomic flag must be reset before new operations.

## Test Signals
Successful init, delayed CPU completion near timeout, stuck CPU timeout, transport error propagation, and cancellation checks returning `-ECANCELED`.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_integ.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_integ.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_integ.h

## Purpose
Declares integration-layer initialization and cancellation helpers plus timing constants.

## Important APIs, Types, and Functions
Defines `CXD2880_TNRDMD_WAIT_INIT_TIMEOUT` as 500 ms, `CXD2880_TNRDMD_WAIT_INIT_INTVL` as 10 ms, and `CXD2880_TNRDMD_WAIT_AGC_STABLE` as 100 ms. Declares `cxd2880_integ_init()`, `cxd2880_integ_cancel()`, and `cxd2880_integ_check_cancellation()`.

## Control Flow
No executable flow in the header; constants are consumed by integration waits.

## State and Persistence
No state. APIs operate on `struct cxd2880_tnrdmd`.

## Dependencies and Integration Points
Includes the core tuner-demod header and provides wait parameters to frontend tune/scan code.

## Risks and Edge Cases
Changing constants changes user-visible tuning latency and timeout behavior. AGC stable wait must match hardware requirements.

## Test Signals
Compile users after constant changes and run init/scan timing tests on real hardware or bus-level simulation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_integ.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_io.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_io.c

## Purpose
Implements generic register I/O helpers above the bus-specific read/write callbacks.

## Important APIs, Types, and Functions
`cxd2880_io_common_write_one_reg()` writes a single byte through `write_regs`. `cxd2880_io_set_reg_bits()` performs masked read-modify-write. `cxd2880_io_write_multi_regs()` writes an array of address/value pairs.

## Control Flow
Single-register write delegates directly. Masked write returns immediately for zero mask, reads the current byte unless mask is `0xff`, merges requested bits, and writes back. Multi-write iterates in order and stops on the first error.

## State and Persistence
No local state. It mutates hardware registers through the configured `struct cxd2880_io` callbacks.

## Dependencies and Integration Points
Used across initialization, tune, sleep, GPIO, interrupt, and monitor paths. Requires bus-specific code to populate the callback table.

## Risks and Edge Cases
No checks are made for null callback members, only null `io`. Masked writes are not atomic at the hardware level and can race with other register users unless callers serialize bus access. Multi-write has no rollback on partial failure.

## Test Signals
Mock I/O tests for masks `0x00`, `0xff`, and partial masks, injected read/write failures, and ordered register sequence emission.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_io.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_io.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_io.h

## Purpose
Defines the CXD2880 register I/O abstraction used to decouple tuner-demod logic from bus transport.

## Important APIs, Types, and Functions
`enum cxd2880_io_tgt` selects SYS or DMD register target. `struct cxd2880_reg_value` stores address/value pairs. `struct cxd2880_io` contains `read_regs`, `write_regs`, `write_reg`, transport object, legacy I2C address fields, slave select, and user pointer. Declares generic helper functions.

## Control Flow
No executable flow. Implementations populate callbacks; driver logic invokes them uniformly.

## State and Persistence
`struct cxd2880_io` persists per frontend instance and stores transport binding. Hardware register state persists only while the device is powered.

## Dependencies and Integration Points
SPI device code fills this interface; tuner-demod, standard-specific, and monitor code consume it for all register access.

## Risks and Edge Cases
Callback lifetime and serialization are external concerns. The I2C fields are unused for CXD2880 SPI but inherited from a generic design, which can confuse new code.

## Test Signals
Attach/init should verify callbacks are populated. Fault-injection transport tests should prove all callers propagate I/O errors cleanly.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_io.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi.h

## Purpose
Defines a small SPI transport abstraction for the CXD2880 driver.

## Important APIs, Types, and Functions
`enum cxd2880_spi_mode` maps modes 0 through 3. `struct cxd2880_spi` contains optional `read`, required write/write-read callbacks for this driver, `flags`, and a transport-owned `user` pointer.

## Control Flow
No executable flow. Bus-specific code fills callbacks and higher layers invoke them through `cxd2880_devio_spi.c`.

## State and Persistence
`flags` and `user` persist per transport object. The header does not define flag bits.

## Dependencies and Integration Points
Implemented by `cxd2880_spi_device.c` using Linux SPI APIs and consumed by the register I/O SPI adapter.

## Risks and Edge Cases
The `read` callback is present but not used by the current register protocol. Callers must validate callback availability before use or rely on constructor invariants.

## Test Signals
Create transport objects for each SPI mode and verify write/write-read callback invocation through register I/O commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi_device.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi_device.c

## Purpose
Implements the `struct cxd2880_spi` transport on top of Linux `struct spi_device`.

## Important APIs, Types, and Functions
Static callbacks `cxd2880_spi_device_write()` and `cxd2880_spi_device_write_read()` wrap `spi_sync()` and `spi_write_then_read()`. `cxd2880_spi_device_initialize()` programs SPI mode, speed, and 8 bits per word, then calls `spi_setup()`. `cxd2880_spi_device_create_spi()` fills the generic callback object.

## Control Flow
Write constructs a one-transfer `spi_message`. Write-read uses the kernel helper. Initialize switches driver enum values to `SPI_MODE_*`; invalid modes return `-EINVAL`. Transport errors are normalized to `-EIO`.

## State and Persistence
The Linux SPI device's mode, max speed, and bits-per-word are mutated persistently for the device. The generic SPI wrapper stores a pointer to `struct cxd2880_spi_device`.

## Dependencies and Integration Points
Uses Linux SPI core and feeds `cxd2880_devio_spi.c`. The attached frontend must ensure SPI access is serialized, typically via the mutex in public config.

## Risks and Edge Cases
`cxd2880_spi_device_initialize()` dereferences `spi_device` before null checks, so callers must pass valid objects. Error mapping to `-EIO` loses exact SPI failure detail. `read` is set to `NULL`.

## Test Signals
SPI setup for all four modes, invalid mode rejection, transfer failure propagation, zero-length argument rejection, and bus traces matching expected register commands.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi_device.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi_device.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi_device.h

## Purpose
Declares the Linux SPI-device transport wrapper for CXD2880.

## Important APIs, Types, and Functions
`struct cxd2880_spi_device` stores `struct spi_device *spi`. Declares `cxd2880_spi_device_initialize()` and `cxd2880_spi_device_create_spi()`.

## Control Flow
No executable flow. Users initialize the Linux SPI device settings and then create the generic SPI callback wrapper.

## State and Persistence
The wrapper stores the external SPI device pointer; it does not own the SPI device.

## Dependencies and Integration Points
Includes the generic CXD2880 SPI header. Used by frontend attach/probe code to bridge kernel SPI to the demod register layer.

## Risks and Edge Cases
Prototype parameter `speedHz` differs in style from the implementation's `speed_hz`, but type/order match. Lifetime of the wrapped SPI device is external.

## Test Signals
Compile-time prototype matching and runtime attach/remove tests proving no stale `spi_device` pointer remains after frontend teardown.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_spi_device.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd.c

## Purpose
Core CXD2880 tuner-demodulator control implementation. It creates single or diversity instances, initializes silicon, sequences tune/sleep transitions, manages saved configuration, GPIOs, interrupts, TS output, PID filtering, RF/LNA hooks, and register freeze helpers.

## Important APIs, Types, and Functions
Public APIs include `cxd2880_tnrdmd_create()`, `cxd2880_tnrdmd_diver_create()`, `init1()`, `init2()`, `check_internal_cpu_status()`, `common_tune_setting1()`, `common_tune_setting2()`, `sleep()`, `set_cfg()`, GPIO read/write/config helpers, interrupt helpers, `ts_buf_clear()`, `chip_id()`, `set_and_save_reg_bits()`, `set_scan_mode()`, `set_pid_ftr()`, RF compensation/LNA setters, TS pin/output controls, and `slvt_freeze_reg()`. Static helpers implement long register sequences for power, PLL, tuning, sleep, PID filter, and saved config replay.

## Control Flow
Creation zeroes state and installs IO/create parameters. `init1()` validates main/single mode, resets runtime fields, reads chip IDs, runs power/RF init sequences on main and sub devices, and waits between stages. `init2()` verifies internal CPU completion, finishes RF init, replays saved config, and enters sleep. Common tune setting first sleeps the device, chooses DVB-T versus DVB-T2 power mode, resets PLL, reloads saved config, computes frequency shift for one-seg/diversity/xtal sharing, runs tune stages, checks CPU completion, configures TS clock or PID filter, then the standard-specific `tune2` enables TS output. Sleep disables TS output, runs standard-specific sleep settings, and clears active frequency/system/bandwidth.

## State and Persistence
Runtime state lives in `struct cxd2880_tnrdmd`: chip ID, sleep/active state, clock mode, frequency, system, bandwidth, scan mode, diver mode, sub pointer, cancellation flag, saved register config memory, PID filter config, RF compensation callback, and LNA threshold table pointers. Saved config is replayed after init/tune transitions but is not persistent across driver lifetime.

## Dependencies and Integration Points
Depends on `struct cxd2880_io` register callbacks, standard-specific DVB-T/T2 sleep/tune helpers, monitor CPU status, and Linux atomic operations. Higher-level frontend code uses this as the main hardware control layer.

## Risks and Edge Cases
Most APIs reject direct sub-device use; callers must route through main. Saved config memory is capped at 100 entries and returns `-ENOMEM` when exceeded. Register sequences are hardware-specific and error-prone. Many operations require sleep or active state exactly. Diversity paths must keep main/sub state synchronized. Masked saved writes can race without external SPI serialization.

## Test Signals
Chip-ID validation, init timeout/error paths, single and diversity tuning, sleep from each standard, saved config replay after PLL reset, GPIO/interrupt/TS buffer operations, PID filter behavior for SPI/SDIO output, and register trace comparison with vendor sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd.h

## Purpose
Defines the main CXD2880 tuner-demodulator control interface, state container, configuration IDs, interrupt masks, diversity modes, TS output modes, GPIO modes, and public control prototypes.

## Important APIs, Types, and Functions
Key enums include chip IDs, state, diversity mode, clock mode, TS output interface, crystal sharing, spectrum sense, config IDs, lock result, GPIO modes, and serial TS clock. Structures model saved config entries, PID filters, LNA thresholds, create parameters, diversity create parameters, and `struct cxd2880_tnrdmd`. It also defines `slvt_unfreeze_reg()` and interrupt bit masks. Prototypes mirror the core implementation.

## Control Flow
No executable flow except the `slvt_unfreeze_reg` macro performing a register write. Function declarations define the valid lifecycle: create, init, configure, tune, monitor lock, sleep, and auxiliary GPIO/interrupt/TS operations.

## State and Persistence
`struct cxd2880_tnrdmd` is the persistent per-instance state object for the driver lifetime. It records current active tuning state and saved configuration that is replayed during hardware transitions.

## Dependencies and Integration Points
Includes common, IO, DTV, DVB-T, and DVB-T2 definitions. It is the common contract consumed by all mode-specific and monitor files plus top-level frontend glue.

## Risks and Edge Cases
The unfreeze macro ignores write errors. Public mutable fields make invariants dependent on disciplined internal use. Config IDs have broad hardware effects, and some are only valid in sleep or specific TS output modes.

## Test Signals
Compile all consumers after any struct/enum change, ABI-like checks for top-level frontend assumptions, and runtime state transition tests verifying fields update consistently.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_driver_version.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_driver_version.h

## Purpose
Provides vendor driver version and release date macros for the CXD2880 tuner-demodulator code.

## Important APIs, Types, and Functions
Defines `CXD2880_TNRDMD_DRIVER_VERSION` as `"1.4.1 - 1.0.5"` and `CXD2880_TNRDMD_DRIVER_RELEASE_DATE` as `"2018-04-25"`.

## Control Flow
No control flow.

## State and Persistence
No runtime state. Values are compile-time constants.

## Dependencies and Integration Points
Can be used by logging, diagnostics, or metadata in top-level frontend code.

## Risks and Edge Cases
Version macros can drift from actual patched code if not updated. They should not be used for runtime feature detection unless maintained carefully.

## Test Signals
Compile users of the macros and confirm any exposed diagnostic string matches expected downstream packaging/version policy.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_driver_version.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt.c

## Purpose
Implements DVB-T-specific tuning, demodulator setup, sleep programming, and lock interpretation for CXD2880.

## Important APIs, Types, and Functions
Public APIs are `cxd2880_tnrdmd_dvbt_tune1()`, `cxd2880_tnrdmd_dvbt_tune2()`, `cxd2880_tnrdmd_dvbt_sleep_setting()`, `cxd2880_tnrdmd_dvbt_check_demod_lock()`, and `cxd2880_tnrdmd_dvbt_check_ts_lock()`. Static helpers include register-sequence demod setup, sleep setup, and `dvbt_set_profile()`.

## Control Flow
`tune1()` validates main/single state, calls common tune setup for DVB-T, programs bandwidth/clock dependent demod settings on main and optional sub, then selects HP or LP profile. `tune2()` completes common tune stage, marks main/sub active, and stores frequency/system/bandwidth. Sleep delegates demod-specific sleep settings. Lock checks read sync status and TS lock; diversity reports locked if either branch locks and unlocked only when both branches detect unlock.

## State and Persistence
Updates `struct cxd2880_tnrdmd` active state, tuned frequency, system, and bandwidth. Profile is programmed into hardware but not separately stored in the state object.

## Dependencies and Integration Points
Depends on core tune/sleep helpers and DVB-T monitor sync status. Top-level frontend tune paths call these around tuner setup and lock polling.

## Risks and Edge Cases
Only main/single objects are valid entry points. Lock result semantics differ in diversity mode. Invalid state transitions return `-EINVAL`. Bandwidth and clock-specific register values must match hardware tables.

## Test Signals
DVB-T tune for 5/6/7/8 MHz, HP and LP profile streams, sleep after active tune, demod and TS lock polling in single/diversity modes, and register trace validation against known-good hardware sequences.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt.h

## Purpose
Declares DVB-T tune parameters and control APIs for CXD2880.

## Important APIs, Types, and Functions
`struct cxd2880_dvbt_tune_param` carries center frequency, bandwidth, and HP/LP profile. Prototypes cover two-phase tune, sleep setting, demod lock check, and TS lock check.

## Control Flow
No executable flow. The two-phase tune API lets callers perform common/hardware preparation and then complete activation after any required waits or tuner work.

## State and Persistence
Tune parameters are transient; successful implementation calls update `struct cxd2880_tnrdmd` state.

## Dependencies and Integration Points
Includes common and tuner-demod headers. Used by top-level DVB frontend operations for DVB-T delivery systems.

## Risks and Edge Cases
Callers must use valid bandwidth/profile combinations and call phases in order. Lock APIs require active state.

## Test Signals
Compile frontend glue against this contract and test tune1/tune2 sequencing, invalid profile rejection through implementation, and active-only lock checks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2.c

## Purpose
Implements DVB-T2-specific tune setup, PLP selection, profile programming, sleep behavior, diversity FEF handling, L1-post validity check, and lock interpretation.

## Important APIs, Types, and Functions
Public APIs include `cxd2880_tnrdmd_dvbt2_tune1()`, `tune2()`, `sleep_setting()`, `check_demod_lock()`, `check_ts_lock()`, `set_plp_cfg()`, `diver_fef_setting()`, and `check_l1post_valid()`. Static helpers program bandwidth/clock demod settings, sleep settings, and base/lite/any profile selection.

## Control Flow
`tune1()` validates state, rejects `ANY` profile in diversity mode, performs common DVB-T2 tune setup, programs main/sub demod settings, sets profile on both branches, and configures automatic or explicit PLP ID. `tune2()` chooses FEF intermittent control by profile, completes common tune stage, and marks active state. Lock checks mirror DVB-T semantics using DVB-T2 sync monitors. `diver_fef_setting()` reads OFDM data and programs diversity FEF registers only for mixed signals.

## State and Persistence
Successful tune stores active frequency/system/bandwidth in main and sub state. PLP, profile, and FEF behavior are programmed into hardware registers. FEF enable flags are stored in `struct cxd2880_tnrdmd`.

## Dependencies and Integration Points
Depends on core tune helpers and DVB-T2 monitor functions for sync, OFDM, and L1 status. Higher-level frontend code uses it for DVB-T2 scan/tune and PLP management.

## Risks and Edge Cases
PLP ID auto versus explicit selection needs correct caller mapping; invalid PLP detection is exposed through tune info elsewhere. Diversity cannot use profile ANY. L1-post validity can change during acquisition. Register tables are sensitive to bandwidth and clock mode.

## Test Signals
Base/lite/any profile tuning, explicit and auto PLP, invalid PLP cases, diversity mixed FEF streams, TS/demod lock in single/diversity modes, L1-post validity polling, and sleep after T2 tune.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2.h

## Purpose
Declares DVB-T2 tune parameters, tune result metadata, PLP selection constant, and control APIs for CXD2880.

## Important APIs, Types, and Functions
`enum cxd2880_tnrdmd_dvbt2_tune_info` reports OK or invalid PLP ID. `struct cxd2880_dvbt2_tune_param` carries center frequency, bandwidth, data PLP ID, profile, and tune info. `CXD2880_DVBT2_TUNE_PARAM_PLPID_AUTO` requests automatic PLP selection. Prototypes cover tune phases, sleep, lock checks, PLP config, diversity FEF setting, and L1-post validity.

## Control Flow
No executable flow. The API separates setup/activation and exposes additional DVB-T2 signalling controls needed after acquisition.

## State and Persistence
Tune parameters are transient; implementation updates tuner-demod state and hardware PLP/profile registers.

## Dependencies and Integration Points
Includes the tuner-demod core and is consumed by top-level frontend tune/scanning code.

## Risks and Edge Cases
`data_plp_id` is 16-bit but hardware programming casts explicit IDs to 8-bit; callers must constrain values. Profile ANY is not valid in diversity mode.

## Test Signals
Automatic and explicit PLP tune flows, invalid PLP reporting, profile handling, L1-post wait loops, and lock checks after tune2.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2_mon.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2_mon.c

## Purpose
Implements DVB-T2 monitor/statistics functions for synchronization, carrier offset, L1 signalling, OFDM, PLPs, BB headers, TS rate, spectrum sense, SNR, packet errors, sampling offset, QAM/code rate/profile, and SSI.

## Important APIs, Types, and Functions
Exports all functions declared in `cxd2880_tnrdmd_dvbt2_mon.h`. Static helpers include the DVB-T2 SSI reference table, SNR register reader/calculator, and SSI calculator. Decoders fill `cxd2880_dvbt2_l1pre`, `cxd2880_dvbt2_l1post`, `cxd2880_dvbt2_plp`, `cxd2880_dvbt2_ofdm`, and `cxd2880_dvbt2_bbheader`.

## Control Flow
Most functions validate active state, select a demod bank, optionally freeze SLV-T registers for coherent multi-byte snapshots, read register blocks, decode bitfields, then unfreeze. Some monitors require sync/L1 lock before reading detailed signalling. Diversity variants delegate to the sub demod or combine main/sub SNR. SSI derives from RF level, constellation, code rate, and profile-specific reference tables.

## State and Persistence
Monitor functions do not intentionally persist state, except hardware freeze/unfreeze side effects during reads. They consume current `tnr_dmd` state and optional RF compensation hooks.

## Dependencies and Integration Points
Depends on common conversion helpers, tuner-demod freeze macros, RF monitor, DVB-T2 data definitions, and frontend statistic paths. Lock checks in tune code depend on sync monitor output.

## Risks and Edge Cases
Failure to unfreeze after errors can stall subsequent register updates; code paths must preserve cleanup. Reserved/unknown bitfield values must not be misreported as valid. Multi-PLP reads require caller buffers large enough. Integer scaling for SNR/SSI/TS rate can overflow or lose precision if formulas change.

## Test Signals
Known DVB-T2 streams with base/lite, multiple PLPs, varied constellations/code rates, MISO/mixed modes, packet errors, spectrum inversion, SNR/RF edge values, and injected I/O errors around freeze/unfreeze.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2_mon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2_mon.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2_mon.h

## Purpose
Declares the DVB-T2 monitoring interface for CXD2880.

## Important APIs, Types, and Functions
Prototypes cover sync status, sub sync status, carrier offset, L1-pre/version/OFDM/data PLPs/active PLP/data PLP error/L1 change/L1-post/BB header/in-band B TS rate, spectrum sense, SNR and diversity SNR, packet error number, sampling offset, QAM, code rate, profile, and SSI for main/sub.

## Control Flow
No executable flow. APIs generally require active DVB-T2 state and return decoded signalling or statistics through output pointers.

## State and Persistence
No state in the header. Implementations read current hardware state and fill caller-owned outputs.

## Dependencies and Integration Points
Includes tuner-demod and DVB-T2 definitions. Used by lock logic and top-level frontend statistic/property reporting.

## Risks and Edge Cases
Many APIs expose raw protocol detail; callers must check return codes and respect active-state requirements. Sub variants are valid only in diversity-main contexts.

## Test Signals
Compile users against each prototype and run frontend stat reads across acquisition, lock, unlock, and diversity modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt2_mon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt_mon.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt_mon.c

## Purpose
Implements DVB-T monitor/statistics functions for sync, mode/guard, carrier offset, TPS information, packet errors, spectrum sense, SNR, sampling offset, and SSI.

## Important APIs, Types, and Functions
Exports the functions declared in `cxd2880_tnrdmd_dvbt_mon.h`. Static helpers include `is_tps_locked()`, `dvbt_read_snr_reg()`, `dvbt_calc_snr()`, and `dvbt_calc_ssi()`. `ref_dbm_1000` maps modulation and code rate to SSI reference levels.

## Control Flow
Functions validate active state, select demod banks, read and decode registers, and use SLV-T freeze/unfreeze for coherent reads where needed. TPS-dependent functions check TPS lock before decoding. Carrier and sampling offsets are sign-extended and scaled by bandwidth/clock-specific formulas. Diversity SNR combines main/sub readings.

## State and Persistence
No persistent driver state is modified, except transient hardware register freeze/unfreeze. Outputs are snapshots of current hardware acquisition state.

## Dependencies and Integration Points
Depends on common conversion helpers, core tuner-demod state/freeze operations, RF level monitor, and DVB-T protocol definitions. DVB-T lock checks call sync monitor functions.

## Risks and Edge Cases
Reading detailed metrics before TPS lock can return invalid data and should produce errors. Register freeze cleanup on error is critical. SSI depends on RF compensation callback correctness. Integer formulas and bandwidth branches are easy to regress.

## Test Signals
DVB-T streams with QPSK/16QAM/64QAM, all code rates and guards, spectrum inversion, packet errors, low/high RF levels, diversity SNR combining, and injected I/O errors during frozen reads.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt_mon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt_mon.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt_mon.h

## Purpose
Declares the DVB-T monitoring interface for CXD2880.

## Important APIs, Types, and Functions
Prototypes cover sync status, sub sync status, mode/guard, carrier offset main/sub, TPS info, packet error number, spectrum sense, SNR and diversity SNR, sampling offset main/sub, and SSI main/sub.

## Control Flow
No executable flow. APIs are expected to be called after DVB-T activation and return current acquisition or statistic snapshots.

## State and Persistence
No state in the header. Implementations read hardware into caller-owned outputs.

## Dependencies and Integration Points
Includes tuner-demod and DVB-T definitions. Used by lock checks and top-level frontend stat reporting.

## Risks and Edge Cases
Callers must not ignore return codes, especially for TPS-dependent metrics. Sub APIs require diversity-main objects.

## Test Signals
Compile all monitor users and read all metrics before lock, after lock, after unlock, and in diversity mode.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_dvbt_mon.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_mon.c -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_mon.c

## Purpose
Implements common monitor helpers shared across DVB-T and DVB-T2: RF level measurement and internal CPU status reads.

## Important APIs, Types, and Functions
`cxd2880_tnrdmd_mon_rf_lvl()` triggers and reads RF level measurement, converts an 11-bit signed value, scales by 125, and applies optional RF compensation callback. `cxd2880_tnrdmd_mon_rf_lvl_sub()` delegates to the diversity sub demod. `cxd2880_tnrdmd_mon_internal_cpu_status()` and `_sub()` read the internal CPU status word.

## Control Flow
RF level requires active state, writes measurement control registers, waits 2-3 ms, checks status, reads the result, restores a demod control bit, and applies compensation. CPU status selects SYS bank `0x1a` and reads two bytes.

## State and Persistence
RF monitor temporarily toggles hardware measurement controls and returns a snapshot. The compensation callback pointer lives in `struct cxd2880_tnrdmd`.

## Dependencies and Integration Points
Used by integration init polling, SSI calculations, and frontend signal-strength reporting. Depends on register I/O and two's-complement conversion.

## Risks and Edge Cases
RF measurement returns `-EINVAL` if status bytes are nonzero, so callers must handle unavailable readings. Compensation callbacks can skew all SSI/signal output. Sub reads require diversity main mode.

## Test Signals
CPU status polling during init, RF readings at known signal levels, compensation callback tests, inactive-state rejection, and diversity sub RF reporting.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_mon.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_mon.h -->
# sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_mon.h

## Purpose
Declares common tuner-demod monitor helpers for RF level and internal CPU status.

## Important APIs, Types, and Functions
Declares `cxd2880_tnrdmd_mon_rf_lvl()`, `cxd2880_tnrdmd_mon_rf_lvl_sub()`, `cxd2880_tnrdmd_mon_internal_cpu_status()`, and `cxd2880_tnrdmd_mon_internal_cpu_status_sub()`.

## Control Flow
No executable flow. CPU status APIs are usable during initialization; RF level requires active state in the implementation.

## State and Persistence
No header state. Implementations read hardware and fill caller-provided output values.

## Dependencies and Integration Points
Includes common and tuner-demod headers. Used by integration initialization, standard-specific SSI/statistics, and frontend status paths.

## Risks and Edge Cases
Sub variants are valid only through a diversity-main object. Callers should not assume RF readings are available before active tune.

## Test Signals
Compile monitor consumers and exercise CPU status and RF level APIs across init, active, inactive, and diversity modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/media/dvb-frontends/cxd2880/cxd2880_tnrdmd_mon.h -->
