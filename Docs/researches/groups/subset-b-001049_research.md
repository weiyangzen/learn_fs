# subset-b-001049 research

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-debugfs.c

Purpose: Implements the debugfs surface for regmap instances. It creates `/sys/kernel/debug/regmap/<map>/` entries for driver name, register dumps, printable register ranges, access flags, and cache controls, giving developers a live inspection path into regmap-backed devices.

Important APIs/types/functions: `struct regmap_debugfs_node` tracks maps registered before the debugfs root exists. `regmap_debugfs_init()`, `regmap_debugfs_exit()`, and `regmap_debugfs_initcall()` own lifecycle. `regmap_read_debugfs()` formats register/value dumps, while `regmap_debugfs_get_dump_start()` and `regmap_next_readable_reg()` map file offsets to sparse printable registers. `regmap_access_show()` exposes readable/writeable/volatile/precious flags. Cache controls are implemented by `regmap_cache_only_write_file()` and `regmap_cache_bypass_write_file()`.

Control flow: initialization defers maps into `regmap_debugfs_early_list` until the root directory is created. For active maps, the code builds a directory name from device/name or a dummy ID, registers debugfs files, adds range-specific files from `map->range_tree`, and delegates to cache backend debugfs hooks. Reads clamp allocation to `PAGE_SIZE << MAX_PAGE_ORDER`, build or reuse an offset cache, skip precious/unreadable/uncached registers, call `regmap_read()`, and copy formatted text to userspace. Cache toggles parse booleans, mutate regmap state under `map->lock`, and may trigger `regcache_sync()`.

State and persistence behavior: Debugfs state is runtime-only. Persistent state lives in `map->debugfs_name`, `map->debugfs_dummy_id`, `map->debugfs_off_cache`, and boolean cache flags. The offset cache persists across debugfs reads until `regmap_debugfs_exit()` frees it. The early list persists only until `regmap_debugfs_initcall()` drains it.

Dependencies and integration points: Depends on debugfs, IDA, list/mutex primitives, uaccess helpers, `regmap_readable()`, `regmap_writeable()`, `regmap_volatile()`, `regmap_precious()`, `regmap_cached()`, and regcache APIs. Integrates with regmap core lifecycle and cache backend-specific debugfs initialization.

Risks: Debugfs reads can perform live hardware reads and affect timing-sensitive devices. Write support and forced field writes are intentionally hidden behind source edits because they can taint the kernel and alter hardware behind drivers. Offset-cache correctness depends on stable readable/cache policy and `debugfs_tot_len`. Cache-only disable can initiate a sync from debugfs and expose device errors. Debugfs is skipped when map locking is disabled to avoid races.

Test signals: No direct test file here, but observable signals include debugfs file creation/removal, sparse register range output, skipped precious registers, cache-only/cache-bypass transitions, dummy ID cleanup, and successful early-list replay after root creation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-fsi.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-fsi.c

Purpose: Provides regmap bus support for FSI slave devices, selecting byte, 16-bit, or 32-bit accessors and endian conversions from `regmap_config`.

Important APIs/types/functions: Defines `regmap_fsi8`, `regmap_fsi16`, `regmap_fsi16le`, `regmap_fsi32`, and `regmap_fsi32le` `struct regmap_bus` instances. `regmap_get_fsi_bus()` selects the bus. Exported wrappers `__regmap_init_fsi()` and `__devm_regmap_init_fsi()` call the regmap core with `fsi_dev->slave` as bus context.

Control flow: Bus selection accepts register widths of 8, 16, or 32 bits and value widths of 8, 16, or 32 bits. For 16/32-bit values it consults `regmap_get_val_endian()` and maps little/native or big/default/native to the matching accessor. Read callbacks issue `fsi_slave_read()`, convert if needed, and return an unsigned value. Write callbacks validate 8/16-bit value bounds where truncation is possible, convert if needed, then call `fsi_slave_write()`.

State and persistence behavior: The adapter owns no heap state and stores no persistent state beyond the regmap created by the core. FSI slave state remains in the underlying FSI subsystem and hardware.

Dependencies and integration points: Depends on `<linux/fsi.h>`, regmap core, endian helpers, and `struct fsi_device`. Integrates with FSI slave read/write APIs and the standard managed/unmanaged regmap initialization pattern.

Risks: Unsupported endian combinations return `-EOPNOTSUPP`; drivers must provide compatible `reg_bits`, `val_bits`, and endian settings. Native endian branches are compile-time dependent. 32-bit non-LE path uses host-order `u32`, while little-endian-selected path explicitly stores big-endian typed temporaries to match FSI byte ordering expectations.

Test signals: Useful tests would instantiate all supported value sizes and endianness settings, verify unsupported configurations fail, and check 8/16-bit writes reject out-of-range values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-fsi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i2c.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i2c.c

Purpose: Implements regmap access over I2C and SMBus, choosing the best available transfer method for a client adapter and honoring adapter length quirks.

Important APIs/types/functions: Key bus implementations are `regmap_i2c`, `regmap_i2c_smbus_i2c_block`, `regmap_i2c_smbus_i2c_block_reg16`, `regmap_smbus_byte_word_reg16`, `regmap_smbus_byte`, `regmap_smbus_word`, and `regmap_smbus_word_swapped`. `regmap_get_i2c_bus()` selects and possibly clones a bus. `__regmap_init_i2c()` and `__devm_regmap_init_i2c()` export initialization.

Control flow: Selection prefers raw I2C transfers, then SMBus I2C block for 8-bit values with 8- or 16-bit registers, then a byte/word fallback for 16-bit EEPROM-style addresses, then SMBus word or byte operations. Raw I2C writes use `i2c_master_send()`, gather writes use two-message `I2C_M_NOSTART` when supported, and reads use write-then-read messages. SMBus paths validate register/value sizes and translate partial transfers into `-EIO`. If adapter quirks cap message sizes, the code duplicates the bus definition, sets `free_on_exit`, and adjusts max raw read/write sizes.

State and persistence behavior: No per-client state is owned except optional cloned `struct regmap_bus` data freed by the regmap core when `free_on_exit` is set. Underlying device state is external.

Dependencies and integration points: Depends on I2C/SMBus APIs, adapter functionality flags, adapter quirks, endian selection, and regmap core formatting. This is the canonical I2C bridge for many kernel drivers using `devm_regmap_init_i2c()`.

Risks: Transfer capability fallback changes semantics and maximum raw lengths. The SMBus 16-bit register fallback supports only single-byte writes. The reg16 SMBus read path uses a write-byte-data address setup followed by current-address byte reads, so it assumes devices auto-increment as described. Incorrect endian settings for SMBus word values lead to swapped data. Gather write may fall back through the core when `I2C_FUNC_NOSTART` is absent.

Test signals: Exercise adapter capability matrices, quirk truncation, big/little 16-bit word values, partial-transfer `-EIO`, and reg16 EEPROM-style reads/writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i2c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i3c.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i3c.c

Purpose: Adds basic regmap transport support for I3C devices using SDR transfers.

Important APIs/types/functions: `regmap_i3c_write()` issues one outbound `struct i3c_xfer`; `regmap_i3c_read()` issues a write register phase followed by a read phase; `regmap_i3c` is the bus definition. `__regmap_init_i3c()` and `__devm_regmap_init_i3c()` are exported wrappers.

Control flow: The write path wraps the whole formatted regmap buffer as one I3C write transfer. The read path builds two transfers: register bytes out, value bytes in. Both call `i3c_device_do_xfers(..., I3C_SDR)` and return its status directly. Initialization passes `&i3c->dev` as both device and bus context.

State and persistence behavior: The file owns no persistent state or allocations. Transfer state is stack-local per operation.

Dependencies and integration points: Depends on I3C device/master APIs and the regmap core. It integrates where I3C client drivers want the same register formatting, caching, and locking services as I2C/SPI regmap users.

Risks: Only SDR mode is used. The transport does not advertise endian defaults, async I/O, gather write, or raw size caps, leaving those to regmap defaults and controller behavior. Any device requiring dynamic address handling or private transfer modes needs logic outside this adapter.

Test signals: Confirm a formatted register write transfer is produced, a read produces exactly two SDR transfers, errors propagate, and managed/unmanaged initialization uses the correct device context.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-i3c.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-irq.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-irq.c

Purpose: Implements a generic nested IRQ controller for devices whose interrupt status, mask, ack, wake, and type registers are accessed through regmap.

Important APIs/types/functions: `struct regmap_irq_chip_data` stores runtime buffers, domain, lock, regmap, chip config, parent IRQ, wake count, and register mapping callback. Exported APIs include `regmap_add_irq_chip_fwnode()`, `regmap_add_irq_chip()`, `regmap_del_irq_chip()`, devm variants, `regmap_irq_get_irq_reg_linear()`, `regmap_irq_set_type_config_simple()`, `regmap_irq_chip_get_base()`, `regmap_irq_get_virq()`, and `regmap_irq_get_domain()`. Core handlers are `regmap_irq_sync_unlock()`, `regmap_irq_enable()`, `regmap_irq_disable()`, `regmap_irq_set_type()`, `regmap_irq_set_wake()`, `read_irq_data()`, and `regmap_irq_thread()`.

Control flow: Add validates chip geometry, allocates status/mask/wake/type/config buffers, initializes all interrupts masked, syncs hardware mask/unmask registers or calls `handle_mask_sync`, optionally acks masked pending interrupts, initializes wake registers, stores level-trigger baseline state, creates an IRQ domain, and requests a threaded parent IRQ. The IRQ thread optionally runs pre/post callbacks and runtime PM, reads status via no-status, main-status/sub-status, bulk, or per-register paths, handles level-change filtering, masks disabled IRQs, acks pending status early, and dispatches nested IRQs through the domain. Bus lock/unlock batches enable/disable/type/wake changes and writes them to hardware on unlock.

State and persistence behavior: Runtime state persists in heap-allocated buffers until deletion or devres release. `mask_buf`, `wake_buf`, `type_buf`, and `config_buf` stage software state; sync-unlock persists it to device registers. `prev_status_buf` stores previous level status. `wake_count` is a delta propagated to the parent IRQ wake state.

Dependencies and integration points: Depends on IRQ domain APIs, nested threaded IRQ handling, regmap reads/writes/update_bits/bulk reads, runtime PM, devres, firmware nodes, and lockdep keys. It integrates with driver-provided `struct regmap_irq_chip` metadata and callbacks.

Risks: Chip configuration must match register stride, masks, and number of registers or interrupts can be missed or storm. `clear_on_unmask` conflicts with ack modes and is rejected. Bulk status reads are used only for linear stride-1 layouts. Ack polarity and clear-ack behavior are hardware-specific and dangerous if misdeclared. Runtime PM errors are logged but some paths continue. Devm release depends on storing the correct `d->irq`.

Test signals: Strong tests cover add-time validation, initial masking/ack/wake writes, enable/disable batching, type-in-mask and config callbacks, main-status subregister reads, level status edge detection, wake propagation, holes in IRQ lists, and devm release/removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-irq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-kunit.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-kunit.c

Purpose: Provides a KUnit suite for regmap core and cache behavior using in-memory RAM and raw-RAM regmap buses as deterministic fixtures.

Important APIs/types/functions: `struct regmap_test_priv` stores the KUnit device and default-callback tracking. `struct regmap_test_param` drives cache type, value endian, base register, and fast I/O. `gen_regmap()` creates `regmap_init_ram()` maps; `gen_raw_regmap()` creates `regmap_init_raw_ram()` maps. The suite registers many `KUNIT_CASE_PARAM()` tests across `REGCACHE_NONE`, `FLAT`, `FLAT_S`, `RBTREE`, and `MAPLE`.

Control flow: Test init creates a KUnit device and stores the test in driver data. Parameter generators cover regular, real-cache-only, sparse-cache, flat-cache, and raw endian cases. Tests fill random RAM buffers, create regmaps, perform regmap API operations, and compare returned values with mock hardware arrays plus `read[]`/`written[]` side effects. Raw tests additionally validate endian conversion and byte-oriented raw buffers. Exit drops the KUnit device reference.

State and persistence behavior: State is test-scoped and freed via `kunit_add_action_or_reset()` invoking `regmap_exit()`. RAM fixture state includes hardware values, read/write tracking, optional no-increment register predicates, and callback invocation flags. Cache state is intentionally manipulated through `regcache_cache_only()`, `regcache_cache_bypass()`, `regcache_mark_dirty()`, `regcache_sync()`, and `regcache_drop_region()`.

Dependencies and integration points: Depends on KUnit, KUnit device helpers, random bytes, internal regmap interfaces, RAM/raw-RAM buses, and all major regcache implementations. It is the strongest local executable specification for regmap cache semantics in this subset.

Risks: Random data can hide deterministic edge cases if no fixed seed is captured, but assertions mostly compare exact in-memory transformations. Some raw tests disable locking for rbtree/maple cache types, so race properties are not exercised. Test coverage focuses on mock memory transports rather than real bus timing/failures.

Test signals: Covers basic read/write, bulk, multi, bypassed reads, volatile/cache-only interplay, readonly/writeonly policy, defaults and default callbacks, patches, stride validation, range windows, stress insertion, cache bypass, dirty sync, cache-only sync, default optimization, readonly sync, patch sync, drop-region behavior with sparse caches, cache presence including zero values, range window cache sync, raw default/raw write/raw sync/no-increment/raw range behavior, and endian variants.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-kunit.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mdio.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mdio.c

Purpose: Provides regmap support for MDIO devices using Clause 22 and Clause 45 register access.

Important APIs/types/functions: `regmap_mdio_c22_read/write()` and `regmap_mdio_c45_read/write()` implement bus callbacks. `regmap_mdio_c22_bus` and `regmap_mdio_c45_bus` are selected by `__regmap_init_mdio()` and `__devm_regmap_init_mdio()`.

Control flow: Clause 22 is selected for `reg_bits == 5` and `val_bits == 16`; reads validate the register fits five bits, call `mdiodev_read()`, mask to 16 bits, and return. Clause 45 is selected for `reg_bits == 21`; the encoded register is split into device address and 16-bit register number, then `mdiodev_c45_read/write()` is used. Unsupported configurations return `-EOPNOTSUPP`.

State and persistence behavior: No internal state or allocation is owned by this adapter. It delegates persistence entirely to the MDIO device and regmap core.

Dependencies and integration points: Depends on MDIO helpers, bit masks, regmap core, and the `REGMAP_MDIO_C45_*` encoding contract exposed by regmap headers.

Risks: Out-of-range registers return `-ENXIO`. Clause 45 callers must encode device address and register number correctly. Value writes are not range-checked beyond the underlying MDIO API, so callers should use 16-bit regmap value widths.

Test signals: Validate Clause 22 and 45 selection, register mask rejection, value masking on reads, C45 devad/regnum split, and managed/unmanaged init failure on unsupported config.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mdio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mmio.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mmio.c

Purpose: Implements regmap access for memory-mapped I/O regions, including endian-specific accessors, no-increment transfers, optional relaxed MMIO, I/O port mode, and optional clock gating.

Important APIs/types/functions: `struct regmap_mmio_context` stores base address, value width, endian flag, optional clock, and selected read/write callbacks. Public APIs are `__regmap_init_mmio_clk()`, `__devm_regmap_init_mmio_clk()`, `regmap_mmio_attach_clk()`, and `regmap_mmio_detach_clk()`. Helper selection occurs in `regmap_mmio_gen_context()`.

Control flow: Context generation validates register bits, pad bits, minimum stride, and incompatible relaxed/I/O port settings. It selects read/write functions by value endian, value width, relaxed mode, and I/O port mode. Optional clocks are acquired and prepared. Normal read/write enable the clock, perform one accessor call, then disable it. No-increment operations use `reads*`/`writes*` helpers for little-endian or byte data, with explicit byte swapping for big-endian multi-byte values. Freeing unprepares and possibly puts the clock.

State and persistence behavior: Persistent runtime state is the allocated context held by the regmap. Attached clocks are marked with `attached_clk` so free does not `clk_put()` externally owned clocks. Hardware register persistence is the MMIO region itself; regmap cache behavior is handled by the core.

Dependencies and integration points: Depends on Linux I/O accessors, clock framework, endian/swab helpers, and regmap bus callbacks. Integrates with device drivers that expose `void __iomem *` register windows.

Risks: Wrong endian/width/stride settings directly corrupt register access. Relaxed MMIO is forbidden with I/O port mode. `regmap_mmio_detach_clk()` sets `ctx->clk = NULL`; later read/write checks use `IS_ERR(ctx->clk)`, so callers must avoid normal access after detach unless a new valid clock state is expected. No bounds checking is done against the mapped resource size. Big-endian no-increment paths emulate operations because native optimized helpers are unavailable.

Test signals: Validate config rejection, accessor selection, clock prepare/enable/disable/unprepare paths, big-endian no-increment byte swapping, relaxed vs ordered access, and attached clock ownership.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-mmio.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-ram.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-ram.c

Purpose: Provides a fast in-memory regmap bus for testing regular register read/write behavior.

Important APIs/types/functions: `regmap_ram_write()` stores values and marks `written[reg]`; `regmap_ram_read()` loads values and marks `read[reg]`; `regmap_ram_free_context()` frees fixture buffers; `__regmap_init_ram()` exports map creation.

Control flow: Initialization requires `config->max_register`, allocates read/write tracking arrays sized to `max_register + 1`, and calls `__regmap_init()` with a fast `regmap_bus`. On init failure it frees tracking arrays. Runtime reads/writes directly index `data->vals`.

State and persistence behavior: State is entirely in `struct regmap_ram_data`: backing values and read/write tracking booleans. It persists for the lifetime of the regmap and is freed by the bus `free_context` callback.

Dependencies and integration points: Depends on internal regmap test structures and regmap core. It is used heavily by `regmap-kunit.c` to distinguish cache hits from hardware accesses.

Risks: It assumes callers provide a correctly sized `vals` array and valid register indices. It is intended for tests only and does no bounds checking in callbacks. Missing `max_register` is rejected with `-EINVAL`.

Test signals: Read/write side effects in `read[]` and `written[]`, cache-hit tests that expect no hardware read, and init failure paths for missing max register or allocation failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-ram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-raw-ram.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-raw-ram.c

Purpose: Provides an in-memory raw regmap bus for testing byte-formatted register/value transfers, endian conversion, and no-increment behavior.

Important APIs/types/functions: `decode_reg()` decodes 16-bit register bytes according to configured endian. `regmap_raw_ram_gather_write()`, `regmap_raw_ram_write()`, and `regmap_raw_ram_read()` implement raw bus callbacks. `__regmap_init_raw_ram()` exports initialization.

Control flow: Initialization requires 16-bit register addresses and a nonzero max register, allocates read/write tracking arrays, stores register endian, and calls `__regmap_init()`. Writes validate two-byte register fields and even value lengths, decode the target register, then either copy all bytes into sequential `u16` storage or, for a no-increment register, store only the last value at the fixed register. Reads mirror that behavior, either copying sequential values or repeating the fixed register value through the destination buffer.

State and persistence behavior: Persistent fixture state is the caller-provided `vals` buffer plus allocated tracking arrays and optional `noinc_reg` predicate. The bus frees all of them at context teardown.

Dependencies and integration points: Depends on regmap core raw callbacks, endian helpers, and `struct regmap_ram_data`. It is paired with the KUnit raw tests.

Risks: Allocation failure for `written` after `read` leaks `read` in the current init path. Runtime callbacks assume register ranges fit the backing buffer. Pointer arithmetic on `void *` follows kernel C extensions. It is test-only and unsuitable as a checked production memory transport.

Test signals: Raw KUnit cases validate endian defaults, raw writes vs single reads, no-increment semantics, raw sync from cache-only state, and range window handling.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-raw-ram.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sccb.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sccb.c

Purpose: Implements regmap support for SCCB-style camera sensor register access using compatible I2C/SMBus operations.

Important APIs/types/functions: `sccb_is_available()` checks required adapter functionality. `regmap_sccb_read()` performs SCCB read sequencing. `regmap_sccb_write()` uses SMBus byte-data writes. `regmap_get_sccb_bus()`, `__regmap_init_sccb()`, and `__devm_regmap_init_sccb()` provide selection and initialization.

Control flow: The bus is available only for 8-bit register and 8-bit value configs with SMBus byte and write-byte-data functionality. Reads lock the I2C segment, perform a write-byte phase to set the register, then perform a byte read phase, store the returned byte, and unlock. Writes call `i2c_smbus_write_byte_data()` directly.

State and persistence behavior: The adapter owns no heap or persistent state. It uses the I2C adapter bus lock only during each read transaction.

Dependencies and integration points: Depends on I2C/SMBus internals, adapter functionality flags, and regmap core. It integrates with sensor drivers that expose SCCB as a variant of I2C rather than a native kernel SCCB bus.

Risks: It uses `__i2c_smbus_xfer()` while holding a segment lock to express SCCB’s two-phase read sequence. Only 8/8 formats are supported. Future native SCCB adapter support would need a new algorithm callback. Incorrect adapter functionality reporting results in `-ENOTSUPP`.

Test signals: Validate bus selection, read lock/unlock around both phases, propagation of either phase failure, and write-byte-data use for writes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sccb.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw-mbq.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw-mbq.c

Purpose: Adds SoundWire SDCA Multi-Byte Quantity regmap support, including variable MBQ sizes and deferrable busy handling.

Important APIs/types/functions: `struct regmap_mbq_context` stores device, slave, readable callback, MBQ config, and max value size. `regmap_sdw_mbq_size()`, `regmap_sdw_mbq_deferrable()`, `regmap_sdw_mbq_poll_busy()`, `regmap_sdw_mbq_write_impl()`, and `regmap_sdw_mbq_read_impl()` implement MBQ-specific behavior. Exported wrappers are `__regmap_init_sdw_mbq()` and `__devm_regmap_init_sdw_mbq()`.

Control flow: Config validation requires 32-bit registers, zero pad bits, and value widths that fit `unsigned int`. Read/write determine per-register MBQ size, perform multi-byte accesses using `SDW_SDCA_MBQ_CTL(reg)` for upper bytes and the base register for the low byte, and retry once if the SoundWire operation returns `-ENODATA`. Deferrable controls may poll the function busy bit via `read_poll_timeout(sdw_read_no_pm, ...)`; otherwise the code sleeps for the configured timeout before retrying.

State and persistence behavior: Context is device-managed allocation. It persists MBQ policy callbacks and the value-size ceiling. No register state is cached here beyond what regmap core may provide.

Dependencies and integration points: Depends on SoundWire no-PM read/write APIs, SDCA register macros, polling/sleep helpers, and regmap bus callbacks. Integrates with drivers using SDCA MBQ controls over SoundWire.

Risks: `config->readable_reg` is stored and called when polling busy; configs without it would be unsafe if a deferrable transaction reaches `regmap_sdw_mbq_poll_busy()`. Invalid MBQ callback sizes fail with `-EINVAL`. The retry model handles only one busy wait and one retry, so repeated device busy states propagate. Non-deferrable controls that defer are only warned, not rejected.

Test signals: Cover config rejection, fixed and callback MBQ sizes, byte ordering across MBQ control registers, `-ENODATA` retry, busy polling timeout, and readable-vs-sleep fallback.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw-mbq.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw.c

Purpose: Provides general SoundWire regmap support for 32-bit little-endian register addresses and byte payloads.

Important APIs/types/functions: `regmap_sdw_write()`, `regmap_sdw_gather_write()`, and `regmap_sdw_read()` wrap `sdw_nwrite_no_pm()` and `sdw_nread_no_pm()`. `regmap_sdw_config_check()` validates supported regmap formats. Exported wrappers are `__regmap_init_sdw()` and `__devm_regmap_init_sdw()`.

Control flow: The normal write path expects the first four bytes of the formatted buffer to be the destination address and writes the remaining bytes. Gather write decodes the separate register buffer and writes the value buffer. Read decodes the register buffer and reads requested bytes. Initialization rejects non-32-bit register addresses, nonzero pad bits, and `can_multi_write` because only bulk writes are supported.

State and persistence behavior: No adapter-owned persistent state exists. Each transfer decodes its address from the current buffer and delegates to SoundWire.

Dependencies and integration points: Depends on SoundWire slave helpers, little-endian decoding, regmap core formatting, and no-PM SoundWire access APIs.

Risks: Callers must use 32-bit register fields and no pad bits. Multi-register writes are rejected because the transport does not implement regmap multi-write semantics. Address bytes are always little-endian.

Test signals: Validate config rejection, write/gather/read address decoding, value length calculation, and propagation of SoundWire errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-sdw.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-slimbus.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-slimbus.c

Purpose: Implements regmap transport for SLIMbus devices with 16-bit register addresses and 8-bit values.

Important APIs/types/functions: `regmap_slimbus_write()` and `regmap_slimbus_read()` call `slim_write()` and `slim_read()`. `regmap_get_slimbus()` selects the bus. `__regmap_init_slimbus()` and `__devm_regmap_init_slimbus()` export initialization.

Control flow: Bus selection accepts only `val_bits == 8` and `reg_bits == 16`. Write interprets the first two bytes of the formatted data as the address and writes the rest of the payload. Read interprets the two-byte register buffer and reads `val_size` bytes. Both use little-endian regmap defaults.

State and persistence behavior: No private state or allocations are owned. The SLIMbus device and hardware retain all external state.

Dependencies and integration points: Depends on SLIMbus APIs and regmap core. It allows SLIMbus client drivers to use standard regmap caching and formatting.

Risks: No explicit `reg_size` or `count` validation is performed in callbacks; the core must supply correctly formatted buffers. Only one address/value format is supported. Endianness relies on the host interpretation of `*(u16 *)`.

Test signals: Validate format rejection, address decode passed to `slim_read/write`, payload length as `count - 2`, and error propagation.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-slimbus.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi-avmm.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi-avmm.c

Purpose: Implements a regmap bus for SPI slaves containing an SPI-to-Avalon-MM bridge, translating regmap reads/writes through transaction, packet, and physical protocol layers.

Important APIs/types/functions: `struct spi_avmm_bridge` holds the SPI device, word length, transaction/physical buffers, and optional word-swap callback. `br_trans_tx_prepare()`, `br_pkt_phy_tx_prepare()`, `br_do_tx()`, `br_do_rx_and_pkt_phy_parse()`, `br_rd_trans_rx_parse()`, `br_wr_trans_rx_parse()`, and `do_reg_access()` form the protocol pipeline. `regmap_spi_avmm_write/read/gather_write()` expose regmap callbacks. Exported wrappers are `__regmap_init_spi_avmm()` and `__devm_regmap_init_spi_avmm()`.

Control flow: Access begins by formatting a transaction header with operation code, byte size, and 32-bit address. Writes append little-endian 32-bit values. Packet/physical preparation wraps data in SOP/channel/EOP framing, escapes reserved bytes, pads to SPI word length, and moves EOP toward the aligned tail to avoid losing early slave responses. TX sends the prepared buffer. RX repeatedly reads one SPI word, swaps if using 32-bit words, skips idle bytes, parses SOP/channel/escape/EOP, times out after sustained invalid data, and fills the transaction buffer. Read responses are raw little-endian values; write responses are validated transaction headers.

State and persistence behavior: Bridge context is allocated per regmap and freed by the bus. Buffers are reused per access and invalidated by resetting lengths before each operation. SPI mode and bits-per-word are configured during context generation, trying 32-bit then falling back to 8-bit.

Dependencies and integration points: Depends on SPI sync read/write APIs, byte swapping, regmap raw bus callbacks, and the Intel SPI slave to Avalon bridge protocol. Regmap max raw read/write are capped by protocol constants.

Risks: This is protocol-heavy and sensitive to byte escaping, alignment, timeout policy, channel number, and 8-vs-32-bit SPI word ordering. Only one write value is supported (`MAX_WRITE_CNT == 1`) while reads allow up to 256 values. Parser errors return `-EFAULT`; sustained idle returns `-ETIMEDOUT`. The code mutates SPI mode/bits-per-word during setup, which may conflict with board expectations if shared assumptions exist.

Test signals: Strong tests should encode/decode reserved bytes, EOP padding with 32-bit words, timeout and last-try behavior, invalid channel/error cases, read count validation, write response validation, SPI setup fallback, and raw length caps.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi-avmm.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi.c

Purpose: Provides the standard SPI regmap transport, including synchronous write/read, gather writes, async writes, and transfer-size limits.

Important APIs/types/functions: `struct regmap_async_spi` embeds regmap async state, `spi_message`, and two transfers. `regmap_spi_write()`, `regmap_spi_gather_write()`, `regmap_spi_async_write()`, `regmap_spi_async_alloc()`, and `regmap_spi_read()` implement callbacks. `regmap_get_spi_bus()` may clone the bus to set max raw sizes. Exported wrappers are `__regmap_init_spi()` and `__devm_regmap_init_spi()`.

Control flow: Simple writes call `spi_write()`. Gather writes build a two-transfer message for register and value buffers and call `spi_sync()`. Async writes populate the preallocated async object, add the register transfer and optional value transfer, set a completion callback that reports `async->m.status`, and call `spi_async()`. Reads use `spi_write_then_read()`. Bus selection clones the static bus when `spi_max_transfer_size()` is finite, adjusts max raw read/write against `spi_max_message_size()` and register reserve size, and marks it `free_on_exit`.

State and persistence behavior: Normal operations are stateless. Async write state persists in per-operation `struct regmap_async_spi` allocated by the callback and owned by regmap core. Cloned bus state persists for the regmap lifetime.

Dependencies and integration points: Depends on SPI core, regmap async interfaces, and regmap default big-endian register/value formatting. `read_flag_mask = 0x80` is advertised for devices using the common SPI read-bit convention.

Risks: Max transfer adjustment can underflow if reserve size exceeds limits, so controller quirks deserve scrutiny. Async buffers must remain valid until SPI completion; this relies on regmap async ownership rules. Devices with nonstandard read flags or endian formats must override config appropriately.

Test signals: Validate synchronous gather messages, async completion status propagation, optional value transfer handling, cloned max raw limits, read flag behavior, and managed/unmanaged init cleanup.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spmi.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spmi.c

Purpose: Implements regmap access over SPMI base and extended register commands.

Important APIs/types/functions: Base command callbacks are `regmap_spmi_base_read()`, `regmap_spmi_base_gather_write()`, and `regmap_spmi_base_write()`. Extended callbacks are `regmap_spmi_ext_read()`, `regmap_spmi_ext_gather_write()`, and `regmap_spmi_ext_write()`. Exported init APIs are `__regmap_init_spmi_base()`, `__devm_regmap_init_spmi_base()`, `__regmap_init_spmi_ext()`, and `__devm_regmap_init_spmi_ext()`.

Control flow: Base reads require one-byte register buffers and perform repeated single-byte `spmi_register_read()` calls. Base writes optimize address zero through `spmi_register_zero_write()` then write remaining bytes one by one. Extended reads/writes require two-byte register buffers and split transfers: addresses up to `0xff` use 16-byte extended commands, higher addresses use long extended commands in 8-byte chunks. Plain write callbacks split the combined reg/value buffer into gather-write form.

State and persistence behavior: No private state or allocations exist. Register address increments are local variables per transfer.

Dependencies and integration points: Depends on SPMI core APIs and regmap raw callbacks. Native endian defaults are used for register/value formatting.

Risks: The code uses `BUG_ON()` for invalid reg sizes/counts rather than returning errors, relying on regmap core formatting to be correct. Address chunks are constrained by SPMI command limits. Pointer increments on `void *` use kernel C extensions.

Test signals: Validate base register-zero optimization, sequential base byte loops, extended short/long chunk splitting at `0xff`, error propagation mid-transfer, and core-provided register size assumptions.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-spmi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-w1.c -->
# sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-w1.c

Purpose: Provides regmap support for 1-Wire slaves using simple command sequences for 8/8, 8/16, and 16/16 register/value formats.

Important APIs/types/functions: Read/write callbacks are `w1_reg_a8_v8_*`, `w1_reg_a8_v16_*`, and `w1_reg_a16_v16_*`. Bus definitions are `regmap_w1_bus_a8_v8`, `regmap_w1_bus_a8_v16`, and `regmap_w1_bus_a16_v16`. `regmap_get_w1_bus()`, `__regmap_init_w1()`, and `__devm_regmap_init_w1()` provide selection and initialization.

Control flow: Each operation obtains the `w1_slave` from the device, validates the register fits the selected address width, locks the master bus mutex, resets/selects the slave, emits either `W1_CMD_READ_DATA` or `W1_CMD_WRITE_DATA`, sends little-endian address bytes, and reads or writes little-endian value bytes. Reset/select failure returns `-ENODEV`.

State and persistence behavior: No adapter state is stored. The only transient state is the bus mutex and command bytes on the 1-Wire master.

Dependencies and integration points: Depends on W1 core primitives and regmap core. It allows simple 1-Wire device drivers to use regmap abstractions.

Risks: Values are not range-checked before byte writes, so regmap value width must constrain callers. All multi-byte values are little-endian by command order. The bus mutex serializes access, but slow 1-Wire transactions can block other devices on the master. Only three fixed format combinations are supported.

Test signals: Validate format selection, register bounds, reset/select failure handling, exact command/address/value byte sequences, and bus mutex coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/base/regmap/regmap-w1.c -->
