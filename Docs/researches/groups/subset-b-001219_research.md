# subset-b-001219 research

This grouped report covers the CAAM controller, job-ring and QI backends, RNG providers, descriptor construction APIs, DPSECI command wrappers, debugfs/error helpers, and key/PDB/PKC descriptor helpers. Each source file has a delimited section for deterministic splitting into `Docs/researches/<source_path>_research.md`.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamprng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamprng.c

Purpose: exposes CAAM SEC4 RNG hardware through the crypto RNG API as `prng-caam` with the generic `stdrng` name, using short CAAM job descriptors submitted to a job ring for reseed and byte generation.

Important APIs and control flow: `caam_prng_register()` checks the controller's RNG block count from era-dependent CHA/version registers before registering `crypto_register_rng()`. `caam_prng_generate()` allocates a CAAM job ring with `caam_jr_alloc()`, builds a descriptor with `init_job_desc()`, `append_operation(OP_ALG_ALGSEL_RNG)`, and `append_fifo_store(... FIFOST_TYPE_RNGSTORE)`, maps a temporary output buffer for DMA, enqueues the job, waits for the completion callback, unmaps, copies bytes to the caller, and frees the ring. `caam_prng_seed()` requires `slen == 0` and submits a finalize/reseed operation. `caam_prng_done()` converts nonzero JR status through `caam_jr_strstatus()`.

State and persistence behavior: only global software state is `caam_prng_alg.registered`; per-request state is a stack `completion` and error code. Persistent RNG state is in CAAM RNG state handles initialized by `ctrl.c`, not in this file. Each generate/seed call allocates and releases a job ring reference rather than retaining a per-tfm ring.

Dependencies and integration points: depends on `jr.c` for queueing, `desc_constr.h`/`desc.h` for descriptor words, `error.c` for status reporting, `intern.h` for controller private data, and crypto RNG registration. It is invoked from JR algorithm registration in `jr.c`.

Risks and test signals: risks include frequent allocation/free overhead, copying through a temporary zeroed buffer, mapping only `dlen` while allocating `aligned_dlen`, no timeout on job completion, and registration depending on `priv->jr[0]` being valid. Test signals are successful `prng-caam` registration only when RNG hardware exists, `crypto_rng_generate()` returning requested byte counts, zero-length seed acceptance only, CAAM error statuses surfacing as negative errors, and unregister balancing during last JR removal.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamprng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamrng.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/caamrng.c

Purpose: registers CAAM as a Linux `hwrng` provider named `rng-caam`, using CAAM job-ring descriptors to fetch 16-byte RNG chunks and an async FIFO for nonblocking reads.

Important APIs and control flow: `caam_rng_init()` checks RNG presence, opens a devres group, allocates `caam_rng_ctx`, and registers `devm_hwrng_register()`. `caam_init()` allocates sync/async descriptors, a kfifo sized to DMA cache alignment, initializes work, allocates a JR, and pre-fills the async FIFO. `caam_read()` either performs a synchronous `caam_rng_read_one()` when `wait` is true or drains the FIFO and schedules `caam_rng_worker()` when empty. `caam_rng_read_one()` maps the destination, builds an RNG descriptor, enqueues it, waits for completion, unmaps, and returns either an error or 16 bytes. `caam_cleanup()` flushes work, frees JR reference, and frees the FIFO.

State and persistence behavior: per-hwrng state tracks the JR device, controller device, two reusable descriptors, work item, and FIFO. Device-managed allocation binds most lifetime to the controller, while `cleanup` releases ring/FIFO resources when hwrng unregisters. RNG entropy/state itself persists in hardware state handles instantiated by `ctrl.c`.

Dependencies and integration points: depends on Linux `hw_random`, kfifo DMA helpers, workqueues, CAAM descriptors, JR enqueue/free, and `caam_jr_strstatus()`. It is registered once by `jr.c` when the first job ring appears and cleaned up on JR removal/suspend.

Risks and test signals: `caam_rng_read_one()` ignores caller `len` and always requests 16 bytes, so buffers must be at least that large; no completion timeout exists; async fill silently drops errors; devres group cleanup must run on all registration failures. Test signals include `/dev/hwrng` reads in wait and non-wait paths, FIFO refill scheduling, suspend/remove cleanup without JR leaks, optional RNG self-test under `CONFIG_CRYPTO_DEV_FSL_CAAM_RNG_TEST`, and no registration when RNG block count is zero.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/caamrng.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/compat.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/compat.h

Purpose: central compatibility include for CAAM driver sources. It pulls common Linux, networking, DMA, OF, crypto API, and algorithm headers into CAAM compilation units.

Important APIs and control flow: this header defines no functions, state, or macros beyond the include guard. Its practical API is transitive: CAAM files include `compat.h` to gain declarations for `struct device`, interrupts, platform/OF helpers, DMA mapping, IOMMU, spinlocks, debugfs, circular buffers, clocks, XFRM, and crypto framework types such as skcipher, aead, hash, akcipher, RSA, AES, DES, GCM, SHA, MD5, ChaCha, and Poly1305.

State and persistence behavior: none. It affects compile-time dependency visibility only.

Dependencies and integration points: included by controller, RNG, JR, QI, error, and key-generation code. It reduces per-file include verbosity but also couples unrelated CAAM modules to a broad header surface.

Risks and test signals: risks are hidden dependencies, slower incremental builds, accidental reliance on indirect includes, and harder include hygiene when kernel APIs move. Test signals are successful allmodconfig-style CAAM builds and the ability to remove unnecessary direct/indirect headers only with full CAAM API coverage.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/compat.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.c

Purpose: top-level CAAM controller platform driver. It maps controller/page registers, detects hardware capabilities and era, configures clocks/DMA/QI, instantiates RNG state handles, initializes debugfs, and populates child job-ring devices.

Important APIs and control flow: descriptor helpers build RNG4 instantiate/deinstantiate jobs; `run_descriptor_deco0()` acquires DECO0 and runs descriptors without JR/QI. `caam_ctrl_rng_init()` detects RNG version, programs TRNG parameters with `kick_trng()`, loops entropy delay on `-EAGAIN`, instantiates handles, records driver-owned handles, and enables RDB. `caam_probe()` allocates `caam_drv_private`, detects i.MX/OP-TEE/MC conditions, enables clocks, maps registers, discovers JR children, chooses endianness and pointer size, sets `caam_dpaa2`/QI/blob flags, initializes QI if present, sets DMA mask, creates debugfs, initializes RNG when page0 is accessible, logs ID/era, and calls `devm_of_platform_populate()`.

State and persistence behavior: exports global `caam_dpaa2`; initializes globals `caam_little_end`, `caam_ptr_sz`, and `caam_imx` through other modules. Per-controller state lives in `caam_drv_private`, including register bases, capability flags, clock handles, IOMMU domain, RNG handle mask, debugfs blobs, and PM save state. Suspend/resume saves MCR/SCFGR and LIODN registers when CAAM loses state and reruns RNG init after restore.

Dependencies and integration points: integrates with OF compatibles `fsl,sec-v4.0`/`fsl,sec4.0`, i.MX SoC matching, OP-TEE and Management Complex policy, QMan/QI, FSL MC versioning, debugfs, DMA/IOMMU, clocks, and JR child platform drivers. The initialized controller private data is consumed by JR, RNG, crypto API, blob, QI, and debugfs modules.

Risks and test signals: risks include register access restrictions under OP-TEE, MC firmware ownership of RNG, fragile era/capability detection, DECO0 polling with busy waits, no security violation IRQ handler despite parsing it, TRNG entropy-delay platform quirks, and assuming child DT order for JR aliases. Test signals are probe on i.MX, Layerscape, DPAA2 and OP-TEE systems, correct DMA mask selection, RNG state-handle instantiation/deinstantiation, QI enablement only when QMan is ready, suspend/resume with and without CAAM power loss, and debugfs/perf counters matching hardware.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.h

Purpose: minimal public controller header for backend-level CAAM state shared with other modules.

Important APIs and control flow: declares `extern bool caam_dpaa2`, which tells non-controller code whether the probed CAAM instance is DPAA2-capable. There are no functions or inline helpers.

State and persistence behavior: the actual variable is defined and exported in `ctrl.c`; it is set during controller probe from compile-time parameter registers and then read by helpers such as DMA mask selection in `intern.h`.

Dependencies and integration points: included by `intern.h`, `jr.c`, and controller-adjacent code that needs DPAA2 mode knowledge without depending on full controller internals.

Risks and test signals: risk is global singleton state in a driver that otherwise represents per-device data, which can be wrong if multiple heterogeneous CAAM instances existed. Test signals are correct `caam_dpaa2` value before JR probing and DMA mask setup, and no stale value after probe deferral/failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/ctrl.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.c

Purpose: provides controller and QI debugfs visibility for CAAM performance counters, fault registers, optional key registers, and QI congestion counts.

Important APIs and control flow: `caam_debugfs_u32_get()` and `caam_debugfs_u64_get()` convert CAAM-endian register-backed values to CPU `u64` for read-only debugfs attributes. `caam_debugfs_init()` creates a `ctl` directory, publishes performance counters and fault registers from `struct caam_perfmon`, and, unless OP-TEE owns page0, exposes KEK/TKEK/TDSK register blobs. Under QI crypto API config, `caam_debugfs_qi_congested()` increments a static counter and `caam_debugfs_qi_init()` publishes it.

State and persistence behavior: debugfs dentries are stored in `ctrlpriv->ctl`; key blob wrappers live in controller private data. `times_congested` is a static process-wide counter. Removal is handled by `ctrl.c` with `debugfs_remove_recursive()` via devm action.

Dependencies and integration points: depends on debugfs, CAAM register endian helpers, `intern.h` private state, and QI congestion callback in `qi.c`. It is initialized from controller probe and QI init.

Risks and test signals: exposing internal keys in debugfs is intentionally skipped under OP-TEE but remains sensitive in non-secure debug builds; reads are raw register snapshots without locking; `times_congested` is not atomic. Test signals include expected files under `/sys/kernel/debug/<dev>/ctl`, monotonically increasing performance counters, fault register visibility after error injection, no key blobs with OP-TEE, and QI congestion count increments under congestion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.h

Purpose: declares debugfs integration points for controller and QI code while compiling to no-op stubs when debugfs or QI support is disabled.

Important APIs and control flow: exposes `caam_debugfs_init()`, `caam_debugfs_qi_congested()`, and `caam_debugfs_qi_init()` under the matching Kconfig conditions. The fallback inline functions accept the same arguments and do nothing.

State and persistence behavior: none in the header; it defines the conditional interface boundary.

Dependencies and integration points: forward-declares `struct dentry`, `struct caam_drv_private`, and `struct caam_perfmon`. Included by `ctrl.c` and `qi.c` so those files can call debugfs hooks without preprocessor clutter.

Risks and test signals: risks are signature drift between real and stub variants and missing coverage in non-debugfs builds. Test signals are clean builds with `CONFIG_DEBUG_FS` and `CONFIG_CRYPTO_DEV_FSL_CAAM_CRYPTO_API_QI` in all enabled/disabled combinations and no runtime dependency on debugfs availability.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/desc.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/desc.h

Purpose: defines CAAM descriptor command encodings, protocol IDs, algorithm selectors, scatter/gather bits, operation fields, math/jump/move fields, and protocol constants used by descriptor builders throughout the driver.

Important APIs and control flow: the file is macro-only. It establishes command opcodes (`CMD_KEY`, `CMD_LOAD`, `CMD_FIFO_STORE`, `CMD_OPERATION`, `CMD_JUMP`, etc.), descriptor header bits (`HDR_ONE`, length/share/start fields), key/load/store/fifo pointer formats, protocol IDs for IPsec, SRTP, MACsec, WiFi, WiMAX, SSL/TLS/DTLS, blob, DKP, RSA/DSA, algorithm selectors and AAIs for AES/DES/MDHA/RNG/SNOW/Kasumi/CRC/ChaCha/Poly1305/PKHA, sequence pointer flags, math source/destination encodings, jump tests, NFIFO entries, and frame descriptor command bits.

State and persistence behavior: none at runtime; these constants define the ABI between software-generated descriptor words and CAAM hardware. Any change affects every descriptor emitted by `desc_constr.h` and algorithm-specific descriptor builders.

Dependencies and integration points: consumed by controller RNG descriptors, crypto API descriptor constructors, PKC/RSA, QI shared descriptors, key split generation, and error decoding. It also sets `MAX_CAAM_DESCSIZE` and SG table flags that influence buffer sizing and DMA layout.

Risks and test signals: risks include silent hardware misprogramming from one-bit macro mistakes, legacy protocol constants for weak TLS/SSL/RC4/DES modes still being available, duplicate-looking TLS private-suite values, and no type safety around OR-composed fields. Test signals are descriptor hex dumps matching hardware manuals, crypto self-tests across block/hash/AEAD/PKC/protocol modes, hardware rejection indexes mapping to intended command words, and compile coverage for 32-bit and 64-bit pointer modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/desc.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/desc_constr.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/desc_constr.h

Purpose: inline helper library for constructing CAAM job and shared descriptors in memory with correct endian conversion, runtime pointer width, header length updates, jumps, immediate data, math commands, sequence pointers, and split-key protocol snippets.

Important APIs and control flow: `init_desc()`, `init_job_desc()`, `init_sh_desc()`, and PDB variants initialize descriptor headers. `desc_len()`, `desc_bytes()`, `desc_end()`, and `sh_desc_pdb()` inspect layout. `append_cmd()`, `append_ptr()`, `append_data()`, generated `append_key/load/fifo_load/fifo_store/operation/seq_*` helpers, `append_store()`, `set_jump_tgt_here()`, and math macros append command words and grow the header length. `desc_inline_query()` decides which data items fit inside a shared descriptor after reserving job descriptor space. `append_proto_dkp()` emits Derived Key Protocol commands for split HMAC keys.

State and persistence behavior: relies on global `caam_little_end` and `caam_ptr_sz`, initialized during controller probe, to encode pointers and u64 immediates. The descriptor buffer state is the header length word; helpers mutate it in place and do not allocate.

Dependencies and integration points: used by almost every CAAM algorithm path, RNG descriptors, QI shared descriptors, and PKC builders. Its pointer-width constants (`DESC_JOB_IO_LEN`, `MAX_SDLEN`) constrain QI shared descriptor size.

Risks and test signals: helpers do not bounds-check against `MAX_CAAM_DESCSIZE`, so callers must allocate enough words; wrong `caam_ptr_sz` corrupts descriptor layout; immediate-data helpers round lengths to words; command option combinations are mostly unchecked. Test signals include descriptor length matching bytes appended, correct 32/64-bit pointer encodings, DKP split-key generation, shared descriptor inline/reference decisions at boundary sizes, and CAAM hardware accepting descriptors without header/length errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/desc_constr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.c

Purpose: adds debugfs visibility for DPAA2 DPSECI frame queues by reporting pending frame and byte counts for each Rx and Tx virtual FQID.

Important APIs and control flow: `dpseci_dbg_fqs_show()` prints a heading for the DPSECI device, iterates `priv->num_pairs`, queries each Rx queue FQID and Tx queue FQID with `dpaa2_io_query_fq_count()`, and emits pending frame/byte counts. `DEFINE_SHOW_ATTRIBUTE()` creates file operations. `dpaa2_dpseci_debugfs_init()` creates a debugfs directory named after the device and adds `fq_stats`; `dpaa2_dpseci_debugfs_exit()` recursively removes it.

State and persistence behavior: stores the debugfs root in `dpaa2_caam_priv->dfs_root`; all displayed counts are live DPAA2 IO queries, not cached state.

Dependencies and integration points: depends on DPAA2 CAAM private data from `caamalg_qi2.h`, `dpaa2_io_query_fq_count()`, debugfs, and seq_file. It complements the DPSECI Management Complex API in `dpseci.c`.

Risks and test signals: query failures are silently skipped, output can be stale immediately after printing, and access depends on debugfs lifetime matching DPSECI object removal. Test signals include `fq_stats` listing all queue pairs, nonzero pending counts during load, graceful behavior when queries fail, and clean removal without dangling debugfs entries.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.h

Purpose: declares DPAA2 DPSECI debugfs helpers and provides stubs when debugfs is disabled.

Important APIs and control flow: exposes `dpaa2_dpseci_debugfs_init()` and `dpaa2_dpseci_debugfs_exit()` for `struct dpaa2_caam_priv`; fallback inline functions no-op under non-debugfs builds.

State and persistence behavior: none in the header. It fixes the conditional interface for DPSECI debugfs lifecycle.

Dependencies and integration points: includes `caamalg_qi2.h` for `dpaa2_caam_priv` and `linux/dcache.h` for debugfs dentry types. Used by DPAA2 CAAM code that owns DPSECI devices.

Risks and test signals: risks are coupling a debugfs header to a large DPAA2 CAAM private header and signature mismatch between stubs and implementation. Test signals are clean builds with debugfs enabled/disabled and correct init/exit pairing during DPSECI probe/remove.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci-debugfs.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.c

Purpose: Management Complex command wrapper for DPAA2 Data Path SEC Interface objects. It opens/closes DPSECI sessions, enables/disables/resets objects, reads attributes, configures queues and congestion notification, and retrieves SEC accelerator capabilities.

Important APIs and control flow: each function allocates `struct fsl_mc_command`, encodes a command header with `mc_encode_cmd_header()`, fills little-endian command parameters from `dpseci_cmd.h`, sends via `mc_send_command()`, and decodes response fields. `dpseci_open()` returns an MC token for later calls. Queue functions set/read destination, priority, user context, order-preservation, and FQID fields. Attribute calls decode DPSECI object queues/options, SEC hardware accelerator counts, and API version. Congestion calls translate destination type/unit bitfields and threshold/message fields.

State and persistence behavior: no driver-owned persistent state; state lives in the MC object identified by token and in the caller's structs. The token returned by open is the session capability required for subsequent commands.

Dependencies and integration points: depends on `linux/fsl/mc.h`, command IDs/layouts from `dpseci_cmd.h`, public structs from `dpseci.h`, and DPAA2 CAAM code that manages DPSECI devices.

Risks and test signals: risks include strict ABI dependence on MC firmware command versions, endian/layout mistakes, unvalidated queue indices, and callers needing to close tokens on all paths. Test signals include API version 5.3 compatibility, successful open/enable/disable/reset, queue FQID retrieval matching DPL configuration, SEC capability fields matching hardware, and congestion notification round-trips.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.h

Purpose: public DPSECI API header describing object limits, queue configuration, destination types, attributes, SEC capability data, congestion notification configuration, and function prototypes for MC commands.

Important APIs and control flow: defines `DPSECI_MAX_QUEUE_NUM`, `DPSECI_ALL_QUEUES`, `DPSECI_OPT_HAS_CG`, queue option bits, destination enum (`NONE`, `DPIO`, `DPCON`), `dpseci_cfg`, `dpseci_attr`, Rx/Tx queue config/attr structs, `dpseci_sec_attr`, congestion unit/mode flags, and prototypes implemented in `dpseci.c` for open/close/enable/disable/reset/is_enabled/get/set operations.

State and persistence behavior: no runtime state; it models MC object state and wire-level configuration passed by callers.

Dependencies and integration points: forward-declares `struct fsl_mc_io` and is consumed by DPAA2 CAAM object management. Its structs must match DPSECI command layouts and firmware semantics.

Risks and test signals: risks are ABI drift against MC firmware, incomplete validation of priority/destination ranges by callers, and confusion between Rx from SEC and Tx to SEC queue naming. Test signals are compile compatibility with `dpseci.c`, successful configuration of all queues or one queue, congestion group operation when `DPSECI_OPT_HAS_CG` is set, and accurate SEC accelerator counts used by algorithm registration.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci_cmd.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci_cmd.h

Purpose: private DPSECI command ABI header containing command version constants, encoded command IDs, field access macros, and packed command/response parameter structures used by `dpseci.c`.

Important APIs and control flow: defines DPSECI API version 5.3, command base versions, `DPSECI_CMD_V1/V2()`, command IDs for open/close, API version, enable/disable/reset, queue get/set, SEC attributes, and congestion notification. `dpseci_set_field()` and `dpseci_get_field()` update sub-byte fields using generated masks. Structures describe command payloads such as `dpseci_cmd_open`, `dpseci_cmd_queue`, `dpseci_rsp_get_tx_queue`, `dpseci_rsp_get_sec_attr`, `dpseci_rsp_get_api_version`, and `dpseci_cmd_congestion_notification`.

State and persistence behavior: none; it is compile-time wire-format definition.

Dependencies and integration points: consumed only by the DPSECI command wrapper and must match `linux/fsl/mc.h` command parameter storage and MC firmware layout.

Risks and test signals: risks include ABI breakage if structure padding differs from firmware expectations, field macros OR-ing into uncleared variables, and command version mismatch for `GET_SEC_ATTR`. Test signals are MC command success for every wrapper, sparse/endian-clean builds, and round-trip queue/congestion fields preserving sub-byte values.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/dpseci_cmd.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/error.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/error.c

Purpose: central CAAM error reporting and global hardware-format state. It decodes JR/QI/DECO/CCB status words into kernel logs and negative errno values, exports scatterlist debug dumping, and owns global endian/pointer/SoC flags.

Important APIs and control flow: `caam_dump_sg()` hex-dumps scatterlists under DEBUG and is a no-op otherwise. Globals `caam_little_end`, `caam_imx`, and `caam_ptr_sz` are exported and initialized elsewhere. Static tables map descriptor errors, QI errors, CHA IDs, CCB error IDs, and RNG-specific errors to text. `report_ccb_status()` returns `-EBADMSG` for ICV check failures without noisy logs, otherwise ratelimits detailed logs. `report_deco_status()` and `report_qi_status()` decode descriptor/QI errors. `caam_strstatus()` dispatches based on status source and returns negative errno.

State and persistence behavior: exported globals are process-wide CAAM hardware format state; static decode tables are immutable. Error reporting has no per-device persistence beyond log side effects.

Dependencies and integration points: called by JR callbacks, RNG/PRNG, key generation, and QI2 paths through `caam_jr_strstatus()`/`caam_qi2_strstatus()` macros. Uses register status bit definitions from `regs.h` and descriptor constants from `desc.h`.

Risks and test signals: risks include singleton endian/pointer state, `qi_v2` currently unused in dispatch, some source reporters unimplemented, possible out-of-range `err_id_list` indexing for unexpected CCB err IDs, and sensitive data in DEBUG dumps. Test signals include correct errno mapping for ICV failures, readable logs for injected descriptor/CCB/QI errors, no crashes on unknown status values, and correct global initialization before descriptor construction.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/error.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/error.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/error.h

Purpose: public error-reporting header for CAAM modules.

Important APIs and control flow: declares `caam_strstatus()`, convenience macros `caam_jr_strstatus()` and `caam_qi2_strstatus()`, `caam_dump_sg()`, and inline `is_mdha()` for checking whether an algorithm selector targets MDHA hash hardware. It also defines `CAAM_ERROR_STR_MAX`.

State and persistence behavior: none in the header; it references error-reporting functions and constants implemented in `error.c`.

Dependencies and integration points: includes `desc.h` for operation selector constants and is used by callbacks and descriptor builders that need consistent status-to-errno conversion or MDHA detection.

Risks and test signals: risks include `CAAM_ERROR_STR_MAX` not being tied to actual emitted strings and `caam_qi2_strstatus()` passing a flag not currently distinguished by `caam_strstatus()`. Test signals are compile coverage across JR, QI2, RNG, and key-generation users and correct behavior for MDHA versus non-MDHA algtype masks.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/error.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/intern.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/intern.h

Purpose: shared private header for CAAM backend modules, defining job-ring/controller private structures, queue sizing, optional algorithm-registration hooks, PM save state, and DMA mask selection.

Important APIs and control flow: defines `JOBR_DEPTH`, interrupt coalescing constants, `CRYPTO_ENGINE_MAX_QLEN`, `struct caam_jrentry_info`, JR state/dequeue params/private data, controller save state, and `struct caam_drv_private` with controller register bases, capability flags, clocks, debugfs state, RNG handle state, and PM state. Provides Kconfig-guarded prototypes or no-op stubs for symmetric/hash/PKC/RNG/PRNG/QI algorithm registration. `caam_get_dma_mask()` chooses 32-, 36-, 40-, or 49-bit masks from `caam_ptr_sz`, `caam_dpaa2`, and compatible strings.

State and persistence behavior: structures here are the main long-lived driver state allocated by `ctrl.c` and `jr.c`. The header itself owns no state but fixes cross-module layout and expectations.

Dependencies and integration points: included by controller, JR, RNG/PRNG, debugfs, error-adjacent code, and algorithm modules. It bridges platform probing, crypto-engine queueing, PM, debugfs, and optional Kconfig APIs.

Risks and test signals: risks include global assumptions embedded in `caam_get_dma_mask()`, `JOBR_DEPTH` needing to remain a power of two for circular macros, stubbed algorithm init hiding disabled features, and structure layout changes affecting many modules. Test signals include successful builds for all Kconfig permutations, correct JR ring wrap behavior, DMA mask matching hardware pointer mode, PM save/restore on supported SoCs, and registration/unregistration balance with multiple JRs.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/intern.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.c

Purpose: CAAM Job Ring backend driver. It probes hardware JRs, manages DMA input/output rings, enqueues descriptors, services completions, owns JR allocation among clients, and registers CAAM crypto/RNG algorithms when the first JR becomes active.

Important APIs and control flow: `caam_jr_probe()` maps JR registers, sets DMA mask, starts a crypto engine, maps IRQ, initializes rings, adds the JR to the global list, and calls `register_algs()`. `caam_jr_enqueue()` maps the descriptor, reserves an input slot under `inplock`, records callback metadata, writes descriptor DMA address to the input ring, uses a full `wmb()`, updates head and hardware job-add, and returns `-EINPROGRESS`. IRQ handling masks interrupts, acknowledges status, and schedules `caam_jr_dequeue()` tasklet, which matches output descriptors to software entries, unmaps descriptors, advances tail across out-of-order completions, removes output entries, and invokes callbacks. PM paths remove/add JRs from allocation list, flush or restart hardware, save ring DMA addresses, and reinitialize hwrng.

State and persistence behavior: global `driver_data.jr_list` and `active_devs` coordinate JR allocation and one-time algorithm registration. Per-JR state includes coherent rings, entry metadata, head/tail indices, input availability, tasklet, IRQ, crypto engine, tfm reference count, and PM ring addresses.

Dependencies and integration points: integrates with OF JR child nodes, crypto-engine, tasklets/IRQs, DMA mapping, controller private data, algorithm modules, hwrng/PRNG, QI algapi, and `jr.h` exported APIs used by all JR-backed operations.

Risks and test signals: risks include `BUG()` on JR hardware errors or unmatched completions, no enqueue retry in callers unless implemented above, tasklet-era interrupt handling, busy remove when `tfm_count` is nonzero, strict ring depth power-of-two assumptions, and subtle memory ordering around CAAM reads. Test signals include descriptor completion under load, out-of-order completion matching, `-ENOSPC` behavior at full ring, suspend/resume with in-flight jobs flushed, one-time algorithm registration across multiple JRs, and no DMA leaks on enqueue/dequeue failures.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.h

Purpose: public JR backend API for CAAM clients that submit descriptors directly to job rings.

Important APIs and control flow: declares `caam_jr_alloc()` to obtain a least-used JR device, `caam_jr_free()` to release the reference, and `caam_jr_enqueue()` to submit a DMA-mappable job descriptor with completion callback and caller context.

State and persistence behavior: no state in the header. The implementation increments/decrements per-JR `tfm_count` and uses the JR software/hardware rings in `jr.c`.

Dependencies and integration points: included by RNG, PRNG, key generation, and algorithm modules. It is the boundary between descriptor construction code and the hardware ring transport.

Risks and test signals: risks are callers forgetting `caam_jr_free()`, assuming `caam_jr_enqueue()` returns zero rather than `-EINPROGRESS` on success, and descriptors/data not being DMA-safe. Test signals are balanced alloc/free counts, correct callback invocation with original descriptor/context, and error handling for no JR, full ring, or descriptor DMA mapping failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/jr.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.c

Purpose: generates MDHA split HMAC keys using CAAM hardware and a JR-backed descriptor, storing the resulting ipad/opad form back into caller-provided key storage.

Important APIs and control flow: `gen_split_key()` computes split key and padded lengths with helpers from `key_gen.h`, validates against `max_keylen`, allocates a descriptor, copies input key into output buffer, maps the output buffer bidirectionally, builds a descriptor that loads the key into class 2, starts MDHA HMAC init for the selected hash, triggers expansion with a zero-length FIFO load, and stores the split key with `FIFOST_TYPE_SPLIT_KEK`. It enqueues via `caam_jr_enqueue()` and waits for `split_key_done()`, which converts JR status through `caam_jr_strstatus()` and completes.

State and persistence behavior: all state is per-call: descriptor allocation, mapped key buffer, completion, and `alginfo` fields updated with split lengths. The generated split key persists only in `key_out` for the caller's transform context.

Dependencies and integration points: used by HMAC/authentication descriptor setup in CAAM crypto API modules. Depends on JR transport, descriptor helpers, MDHA operation constants, and error reporting.

Risks and test signals: risks include `split_key_len()` assuming valid MDHA hash selector index, key material copied and DMA-mapped in-place, no timeout, and descriptor buffer sizing tied to pointer width. Test signals include HMAC self-tests for MD5/SHA1/SHA2 variants, split key length/padding matching MDHA requirements, proper error on oversized keys, and no key corruption on DMA mapping failure.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.h

Purpose: declares split-key generation interfaces and inline helpers for MDHA HMAC split key sizing.

Important APIs and control flow: `split_key_len()` maps MDHA hash selector submasks to doubled pad sizes for MD5, SHA1, SHA224, SHA256, SHA384, and SHA512. `split_key_pad_len()` aligns the split key length to 16 bytes. `struct split_key_result` carries a completion and errno for asynchronous JR completion. Prototypes expose `split_key_done()` and `gen_split_key()`.

State and persistence behavior: no header-owned state; `split_key_result` is per-call state used by `key_gen.c`.

Dependencies and integration points: relies on `OP_ALG_ALGSEL_SHIFT/SUBMASK` constants from descriptor headers included before use. Consumed by CAAM hash/authentication setup code that needs hardware-expanded HMAC keys.

Risks and test signals: risks include no bounds check on the computed `mdpadlen` index for invalid alg selectors and implicit dependence on exactly six supported MDHA hashes. Test signals are correct split/padded lengths for every supported hash, rejected or unreachable invalid alg selectors, and generated split keys passing HMAC known-answer tests.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/key_gen.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/pdb.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/pdb.h

Purpose: defines CAAM Protocol Data Block layouts and option bits for hardware protocol descriptors, including IPsec ESP, WiFi, WiMAX, MACsec, TLS/DTLS/SSL, SRTP, DSA/ECDSA, and RSA.

Important APIs and control flow: the header is layout-only. It defines PDB option masks for ESP header manipulation, anti-replay, IV source, ESN, checksum, tunnel/header handling, protocol-specific structs for encapsulation/decapsulation variants, DECO override layout, TLS/DTLS sequence/IV structures, SRTP salt/ROC/anti-replay fields, DSA/ECDSA scatter-gather and length bits, RSA public/private key form selectors, RSA PDB structs, and `SIZEOF_RSA_*_PDB` macros that depend on runtime `caam_ptr_sz`.

State and persistence behavior: none directly; these structures are copied into descriptors or used to append descriptor PDB fields. Some PDBs contain DECO writeback regions such as sequence numbers or anti-replay scorecards, so caller-owned buffers may be modified by hardware.

Dependencies and integration points: consumed by protocol crypto modules and `pkc_desc.c`; depends on DMA address sizes and CAAM descriptor pointer width. RSA size macros integrate with descriptor PDB initialization helpers.

Risks and test signals: risks include C structure padding/endian mismatches with hardware PDB format, flexible IP header sizing mistakes, runtime pointer-size-dependent PDB length errors, typo/documentation drift in RSA CRT comments, and caller responsibility for DMA-safe/writeback buffers. Test signals include IPsec/TLS/SRTP/MACsec/WiFi protocol known-answer tests, RSA public/private form descriptors accepted by hardware, anti-replay/writeback state updates, and descriptor length checks in 32-bit and 64-bit pointer modes.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/pdb.h -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/pkc_desc.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/pkc_desc.c

Purpose: builds CAAM job descriptors for RSA public and private-key operations. Public key cryptography uses job descriptors directly because there is no shared descriptor for these operations.

Important APIs and control flow: `init_rsa_pub_desc()` initializes a job descriptor with RSA public PDB size, appends SG flags, input/output/modulus/exponent DMA pointers, input length, and `OP_PCLID_RSAENC_PUBKEY`. `init_rsa_priv_f1_desc()` appends encrypted input, output, modulus, private exponent, and private key form 1 operation. `init_rsa_priv_f2_desc()` appends private form 2 parameters including p/q and temporary buffers. `init_rsa_priv_f3_desc()` appends CRT coefficient, p/q, dp/dq, temporaries, length, and form 3 operation.

State and persistence behavior: no persistent state. The caller owns PDB contents, DMA mappings, temporary buffers, and descriptor memory; these helpers only append words to the descriptor.

Dependencies and integration points: depends on RSA PDB structs and size macros from CAAM PKC headers/PDB definitions and descriptor construction helpers. Called by CAAM akcipher/RSA implementation.

Risks and test signals: risks include no validation of key/input lengths, pointer DMA mapping, temporary buffer sizes, or descriptor capacity; wrong key form selection silently produces hardware errors. Test signals include RSA encrypt/decrypt/sign/verify known-answer tests for public, raw private, and CRT forms; descriptor dumps matching expected PDB order; and hardware error indexes pointing to intended fields on malformed keys.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/pkc_desc.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.c -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.c

Purpose: implements the legacy DPAA1 CAAM Queue Interface backend using QMan frame queues, per-CPU response queues, NAPI polling, congestion groups, and a small hot-path kmem cache.

Important APIs and control flow: `caam_qi_init()` allocates a congestion group, response FQs for QMan-affine CPUs, dummy netdev/NAPI contexts, a `caamqicache`, debugfs, and a devm shutdown action. `caam_drv_ctx_init()` validates shared descriptor length, builds and DMA-maps preheader/shared descriptor memory, chooses a QMan-affine CPU, binds a response FQ, and creates a scheduled request FQ. `caam_qi_enqueue()` DMA-maps the request SGT, builds a compound FD, retries `qman_enqueue()`, and refcounts the driver context. Completion callbacks from ERN or DQRR translate FDs back to requests, unmap SGTs, decrement refcounts, report errors, and invoke caller callbacks. `caam_drv_ctx_update()` switches to a new parked request FQ, drains the old FQ, updates the shared descriptor, schedules the new FQ, and kills the old one. `caam_drv_ctx_rel()` kills the request FQ and unmaps descriptor memory.

State and persistence behavior: per-CPU `pcpu_qipriv` stores NAPI/netdev/response FQ; `last_cpu` spreads contexts; global `qipriv.cgr`, `caam_congested`, and `qi_cache` persist for the backend lifetime. Per-crypto context state is `caam_drv_ctx` with shared descriptor DMA address, request/response FQs, refcount, CPU, operation type, and device.

Dependencies and integration points: depends on QMan portals/FQs/CGRs, NAPI/netdev shims, controller IOMMU domain, CAAM descriptor sizes, debugfs QI congestion tracking, and QI algorithm modules using `caam_drv_req`.

Risks and test signals: risks include complex FQ teardown races, limited retries under QMan congestion, response lookup through IOVA-to-virt assumptions, refcount drain timeout warnings, global congestion state, and partial failure cleanup across per-CPU setup. Test signals include high-throughput crypto via QI, congestion callback/debugfs increments, context update while requests are in flight, CPU affinity fallback, NAPI polling/rescheduling, clean shutdown of all FQs/CGR/cache, and no DMA leaks on enqueue errors.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.c -->

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.h -->
# sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.h

Purpose: public interface for the legacy CAAM/QI backend used by QI-aware CAAM crypto algorithms.

Important APIs and control flow: defines `CAAM_QI_MEMCACHE_SIZE`, exported `caam_congested`, callback type `caam_qi_cbk`, operation enum, opaque request/context relationship, `struct caam_drv_ctx` holding preheader/shared descriptor, request/response FQs, refcount, CPU, operation type, and device, and `struct caam_drv_req` holding a two-entry QMan S/G table, context, callback, and app context. Prototypes expose context init/update/release, enqueue, busy check, backend init, and QI cache allocation/free.

State and persistence behavior: no header state, but it describes the state allocated by `qi.c`. Request structures are caller-owned and must remain valid until callback; contexts persist for a crypto transform/session.

Dependencies and integration points: depends on QMan types, crypto alignment, CAAM descriptor constants, and descriptor construction helpers. Used by `caamalg_qi` style algorithms to submit frame-based CAAM work.

Risks and test signals: risks include callers mis-sizing/initializing `fd_sgt`, using requests after completion, failing to release contexts, mismatch between comment saying 256B and actual `CAAM_QI_MEMCACHE_SIZE` 768, and relying on global congestion for backpressure. Test signals include enqueue/completion callbacks with correct app context, context update preserving in-flight requests, cache allocation alignment, and busy/backpressure behavior under congestion.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/crypto/caam/qi.h -->
