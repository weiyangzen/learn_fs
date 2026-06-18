# Research: subset-b-005965

Grouped research for Linux kernel trace-event headers under `sources/distributed-fs/ceph-client/include/trace/events`. Each section preserves the source path in its title and is delimited for deterministic splitting into source-tree-aligned per-file research documents.

<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fscache.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fscache.h

Purpose: FS-Cache object lifecycle, access accounting, invalidation, and resize tracepoints for cache, volume, and cookie debugging.

Important APIs/types/functions: Declares trace-event macros/classes `trace:fscache_access`, `trace:fscache_access_cache`, `trace:fscache_access_volume`, `trace:fscache_acquire`, `trace:fscache_active`, `trace:fscache_cache`, `trace:fscache_cookie`, `trace:fscache_invalidate`, `trace:fscache_relinquish`, `trace:fscache_resize`, `trace:fscache_volume`. Defines or exports symbolic enums/helpers `a`, `fscache_access_trace`, `fscache_active_trace`, `fscache_cache_trace`, `fscache_cookie_trace`, `fscache_volume_trace`. Representative payload fields include `cache:unsigned int`, `cookie:unsigned int`, `flags:u8`, `n_accesses:int`, `n_active:int`, `new_size:loff_t`, `old_size:loff_t`, `ref:int`, `retire:bool`, `usage:int`, `v_n_cookies:int`, `v_ref:int`, `volume:unsigned int`, `where:enum fscache_cache_trace`, `where:enum fscache_cookie_trace`, `where:enum fscache_volume_trace`, `why:enum fscache_access_trace`, `why:enum fscache_active_trace`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Defines cache/volume/cookie/access enum namespaces, exports them with TRACE_DEFINE_ENUM, and emits tracepoints as FS-Cache references, active users, I/O accesses, acquire/relinquish, invalidate, and resize transitions happen. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The event payloads persist only in ftrace/perf buffers, but they snapshot debug IDs, refcounts, active/access counters, volume cookie counts, flags, retire state, and object sizes from live FS-Cache state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/fscache.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Incorrect enum/string mapping, stale debug IDs after object teardown, and racing counter snapshots can mislead cache coherency or lifetime investigations. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise FS-Cache acquire/relinquish, lookup, read/write, invalidate, resize, cache withdrawal, and failure paths with tracefs enabled and verify symbolic reasons and counts. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fscache`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fscache.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsi.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fsi.h

Purpose: Generic FSI bus tracing for master read/write operations, results, breaks, scans, slave discovery, and device creation.

Important APIs/types/functions: Declares trace-event macros/classes `trace:fsi_dev_init`, `trace:fsi_master_break`, `trace:fsi_master_read`, `trace:fsi_master_rw_result`, `trace:fsi_master_scan`, `trace:fsi_master_unregister`, `trace:fsi_master_write`, `trace:fsi_slave_init`, `trace:fsi_slave_invalid_cfam`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:__u32`, `cfam_id:__u32`, `chip_id:int`, `data:__u32`, `id:int`, `idx:int`, `link:int`, `master_idx:int`, `master_n_links:int`, `n_links:int`, `ret:int`, `scan:bool`, `size:__u32`, `size:size_t`, `type:int`, `unit:int`, `version:int`, `write:bool`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Callers bracket master I/O and bus management with read/write/result/break/scan/unregister/slave/device events so failures can be correlated by master index, link, address, size, and return code. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace records contain ephemeral bus topology and transaction fields such as master index, link, CFAM id, engine type, unit, version, data, and error code. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Because FSI is low-level service-processor plumbing, missing traces around error returns or endian conversion makes field failures hard to isolate. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run scan/discovery plus read/write error injection on FSI masters and check result events line up with transfer arguments and return codes. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fsi`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsi.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsi_master_aspeed.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fsi_master_aspeed.h

Purpose: Aspeed FSI master OPB/CFAM tracing for MMIO reads, writes, OPB errors, and CFAM reset sequencing.

Important APIs/types/functions: Declares trace-event macros/classes `trace:fsi_master_aspeed_cfam_reset`, `trace:fsi_master_aspeed_opb_error`, `trace:fsi_master_aspeed_opb_read`, `trace:fsi_master_aspeed_opb_write`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:uint32_t`, `irq_status:uint32_t`, `mesrb0:uint32_t`, `mresp0:uint32_t`, `mstap0:uint32_t`, `result:uint32_t`, `size:size_t`, `start:bool`, `status:uint32_t`, `val:uint32_t`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The driver records OPB address/value/size on reads and writes, emits status/result/error register snapshots, and marks CFAM reset start/end. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: No persistent state is owned; trace records snapshot OPB/FSI register status words and reset phase while hardware state changes externally. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Register snapshots must match hardware documentation; printing the wrong status word can hide bus fault causes. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Trigger successful OPB access, OPB timeout/error, and CFAM reset paths on Aspeed hardware or emulation and validate decoded addresses and status fields. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fsi_master_aspeed`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsi_master_aspeed.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsi_master_ast_cf.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fsi_master_ast_cf.h

Purpose: AST ColdFire-assisted FSI master tracing for coprocessor commands, SRAM requests/responses, CRC failures, busy polling, and address optimization.

Important APIs/types/functions: Declares trace-event macros/classes `trace:fsi_master_acf_cmd_abs_addr`, `trace:fsi_master_acf_cmd_rel_addr`, `trace:fsi_master_acf_cmd_same_addr`, `trace:fsi_master_acf_copro_command`, `trace:fsi_master_acf_copro_response`, `trace:fsi_master_acf_crc_rsp_error`, `trace:fsi_master_acf_poll_response_busy`, `trace:fsi_master_acf_send_request`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:u32`, `bits:u8`, `busy_count:int`, `crc_ok:bool`, `master_idx:int`, `msg:uint64_t`, `op:uint32_t`, `rbits:u8`, `rcrc:u8`, `rdata:u32`, `rel_addr:u32`, `retries:int`, `rtag:u8`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Command events follow request submission, coprocessor response, CRC validation, busy-loop retries, and absolute/relative/same-address command construction. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace entries snapshot command words, response words, CRC bits, retry counts, relative addresses, and master index without storing state outside tracing buffers. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: FSI command bit packing is dense; mismatched bit lengths, CRC interpretation, or relative-address traces can send debugging toward the wrong transaction. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Validate read/write, BUSY retry, CRC error, and absolute/relative/same-address cases with firmware/hardware tests and compare traces to wire-format commands. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fsi_master_ast_cf`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsi_master_ast_cf.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsi_master_gpio.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fsi_master_gpio.h

Purpose: GPIO bit-banged FSI master tracing for bit input/output, break clocks, CRC/busy handling, and address command forms.

Important APIs/types/functions: Declares trace-event macros/classes `trace:fsi_master_gpio_break`, `trace:fsi_master_gpio_clock_zeros`, `trace:fsi_master_gpio_cmd_abs_addr`, `trace:fsi_master_gpio_cmd_rel_addr`, `trace:fsi_master_gpio_cmd_same_addr`, `trace:fsi_master_gpio_crc_cmd_error`, `trace:fsi_master_gpio_crc_rsp_error`, `trace:fsi_master_gpio_in`, `trace:fsi_master_gpio_out`, `trace:fsi_master_gpio_poll_response_busy`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:u32`, `bits:int`, `busy:int`, `clocks:int`, `master_idx:int`, `msg:uint64_t`, `rel_addr:u32`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events are emitted while shifting FSI bits through GPIOs, sending breaks, polling responses, reporting CRC command/response errors, and selecting absolute/relative/same-address encodings. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: State is external GPIO pin state and FSI protocol state; trace payloads store bit counts, messages, addresses, busy counts, and master index samples. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: High-volume bit tracing can perturb timing, and off-by-one bit counts or reversed bit order make protocol traces deceptive. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run bit-banged read/write/break operations with CRC and busy retries, then compare trace messages against expected FSI frame encoding. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fsi_master_gpio`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsi_master_gpio.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsi_master_i2cr.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fsi_master_i2cr.h

Purpose: I2C-responder FSI master tracing for command/status/log words and I2C transport errors.

Important APIs/types/functions: Declares trace-event macros/classes `trace:i2cr_i2c_error`, `trace:i2cr_read`, `trace:i2cr_status`, `trace:i2cr_status_error`, `trace:i2cr_write`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:unsigned short`, `bus:int`, `command:unsigned char`, `data:unsigned char`, `error:uint64_t`, `log:uint64_t`, `rc:int`, `status:uint64_t`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The tracepoints record I2C command/address/data flow, status/log reads, decoded error words, and return codes from I2C operations. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Only trace-buffer snapshots are kept; live persistence belongs to the I2C adapter, responder device, and FSI master state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: I2C bus number/address reuse and compact status words can obscure which responder failed unless every error path emits consistent data. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Test responder read/write/status operations with NACK, timeout, and status-error injection while checking bus/address/command fields. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fsi_master_i2cr`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsi_master_i2cr.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsverity.h -->
# sources/distributed-fs/ceph-client/include/trace/events/fsverity.h

Purpose: fs-verity tracing for enablement, Merkle tree construction completion, data block verification, Merkle cache hits, and Merkle block verification.

Important APIs/types/functions: Declares trace-event macros/classes `trace:fsverity_enable`, `trace:fsverity_merkle_hit`, `trace:fsverity_tree_done`, `trace:fsverity_verify_data_block`, `trace:fsverity_verify_merkle_block`. Defines or exports symbolic enums/helpers none. Representative payload fields include `data_pos:u64`, `data_size:u64`, `file_digest:u8`, `hblock_idx:unsigned long`, `hidx:unsigned int`, `ino:u64`, `level:unsigned int`, `levels:unsigned int`, `merkle_block:unsigned int`, `num_levels:unsigned int`, `root_hash:u8`, `tree_size:u64`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The events follow the fs-verity lifecycle from enabling an inode through tree building and per-block verification at data and Merkle levels. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace payloads snapshot inode numbers, tree/data sizes, Merkle tree levels, data positions, hash block indexes, and cache-hit metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Incorrect level/block indexing in traces can mask integrity bugs or make cache-hit accounting look correct when verification used a different block. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Enable fs-verity on test files, read verified ranges, force Merkle cache hits/misses, and corrupt data/Merkle blocks to confirm traces and failures. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/fsverity`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/fsverity.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/gpio.h -->
# sources/distributed-fs/ceph-client/include/trace/events/gpio.h

Purpose: Generic GPIO tracing for direction changes and value get/set operations.

Important APIs/types/functions: Declares trace-event macros/classes `trace:gpio_direction`, `trace:gpio_value`. Defines or exports symbolic enums/helpers none. Representative payload fields include `err:int`, `get:int`, `gpio:unsigned`, `in:int`, `value:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. GPIO core users emit direction and value events with GPIO number, input/output or get/set direction, value, and error code. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The tracepoint owns no GPIO state; it records samples from gpiolib transitions and line values. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Legacy global GPIO numbers may be ambiguous on systems with many chips, and high-frequency value tracing can be noisy. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Toggle GPIO direction and values through gpiod/gpiolib paths, including failing requests, and verify event ordering and error reporting. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/gpio`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/gpio.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/gpu_mem.h -->
# sources/distributed-fs/ceph-client/include/trace/events/gpu_mem.h

Purpose: GPU memory accounting tracepoint for per-process and per-GPU total allocation updates.

Important APIs/types/functions: Declares trace-event macros/classes `trace:gpu_mem_total`. Defines or exports symbolic enums/helpers none. Representative payload fields include `gpu_id:uint32_t`, `pid:uint32_t`, `size:uint64_t`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. A single event records gpu_id, process id, and total size as GPU drivers update memory accounting. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Persistent accounting is maintained by drivers; the trace entry is a sampled total in the tracing ring. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Drivers must agree on gpu_id and size units or cross-driver memory dashboards become inconsistent. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Allocate/free GPU buffers in a driver using this tracepoint and verify totals return to baseline per pid and GPU. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/gpu_mem`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/gpu_mem.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/habanalabs.h -->
# sources/distributed-fs/ceph-client/include/trace/events/habanalabs.h

Purpose: Habana Labs accelerator tracepoints for MMU mapping, DMA allocation/mapping, communications, and register access.

Important APIs/types/functions: Declares trace-event macros/classes `class:habanalabs_comms_template`, `class:habanalabs_dma_alloc_template`, `class:habanalabs_dma_map_template`, `class:habanalabs_mmu_template`, `class:habanalabs_reg_access_template`, `event:habanalabs_comms_protocol_cmd`, `event:habanalabs_comms_send_cmd`, `event:habanalabs_comms_wait_status`, `event:habanalabs_comms_wait_status_done`, `event:habanalabs_dma_alloc`, `event:habanalabs_dma_free`, `event:habanalabs_dma_map_page`, `event:habanalabs_dma_unmap_page`, `event:habanalabs_elbi_read`, `event:habanalabs_elbi_write`, `event:habanalabs_mmu_map`, `event:habanalabs_mmu_unmap`, `event:habanalabs_rreg32`, `event:habanalabs_wreg32`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:u32`, `caller:const char *`, `cpu_addr:u64`, `dir:int`, `dma_addr:u64`, `dname`, `flush_pte:u8`, `len:u32`, `op_str:char *`, `page_size:u32`, `phys_addr:u64`, `size:u32`, `val:u32`, `virt_addr:u64`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Event classes share layouts for map/unmap, DMA alloc/free, DMA map/unmap, communications send/receive, and read/write register accesses. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace entries snapshot device name, virtual/physical/DMA addresses, sizes, handles, opcodes, register offsets, masks, and values; device state persists in the driver. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Address-bearing traces may expose sensitive topology, and stale mappings or mismatched masks can hide IOMMU/register bugs. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise MMU map/unmap, DMA buffer lifecycle, command communication, and register read/write paths under tracefs and compare with driver debug output. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/habanalabs`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/habanalabs.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/handshake.h -->
# sources/distributed-fs/ceph-client/include/trace/events/handshake.h

Purpose: Network handshake and TLS record tracepoints for kernel TLS handshake request lifecycle, file descriptor handoff, errors, alerts, completion, and content types.

Important APIs/types/functions: Declares trace-event macros/classes `class:handshake_alert_class`, `class:handshake_error_class`, `class:handshake_event_class`, `class:handshake_fd_class`, `event:name`, `trace:handshake_complete`, `trace:tls_contenttype`. Defines or exports symbolic enums/helpers `TLS_ALERT_DESC_##x`, `TLS_ALERT_LEVEL_FATAL`, `TLS_ALERT_LEVEL_WARNING`, `TLS_RECORD_TYPE_##x`. Representative payload fields include `daddr:__u8`, `description:unsigned long`, `err:int`, `fd:int`, `level:unsigned long`, `netns_ino:unsigned int`, `req:const void *`, `saddr:__u8`, `sk:const void *`, `status:int`, `type:unsigned long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Event classes record request ids, socket addresses, file descriptors, negative errors, TLS alert level/description, session status, peer identity, and content type decode. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The tracepoint stores no session; it snapshots handshake request/socket/TLS values while the handshake service and TLS stack own state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/net.h>`, `#include <net/tls_prot.h>`, `#include <linux/tracepoint.h>`, `#include <trace/events/net_probe_common.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Stringified peer names and socket addresses can be privacy-sensitive, and missing enum coverage for TLS alerts/content types reduces diagnosis value. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run successful and failing kTLS handshakes, fd handoff, alert paths, and TLS record receipt while verifying address and enum printing. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/handshake`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/handshake.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/host1x.h -->
# sources/distributed-fs/ceph-client/include/trace/events/host1x.h

Purpose: NVIDIA Tegra host1x tracepoints for CDMA push buffers, channel submission, syncpoint waits, and wait-check timing.

Important APIs/types/functions: Declares trace-event macros/classes `class:host1x`, `event:host1x_cdma_begin`, `event:host1x_cdma_end`, `event:host1x_channel_open`, `event:host1x_channel_release`, `trace:host1x_cdma_push`, `trace:host1x_cdma_push_gather`, `trace:host1x_cdma_push_wide`, `trace:host1x_channel_submit`, `trace:host1x_channel_submit_complete`, `trace:host1x_channel_submitted`, `trace:host1x_syncpt_load_min`, `trace:host1x_syncpt_wait_check`, `trace:host1x_wait_cdma`. Defines or exports symbolic enums/helpers none. Representative payload fields include `bo:struct host1x_bo *`, `cmdbuf:bool`, `cmdbuf:u32`, `cmdbufs:u32`, `count:int`, `eventid:u32`, `id:u32`, `min:u32`, `name:const char *`, `offset:u32`, `op1:u32`, `op2:u32`, `op3:u32`, `op4:u32`, `relocs:u32`, `syncpt_base:u32`, `syncpt_id:u32`, `syncpt_incrs:u32`, `syncpt_max:u32`, `thresh:u32`, `val:u32`, `words:u32`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Submission paths emit CDMA pushes/gathers, channel submit/submitted/complete, CDMA waits, syncpoint min loads, and syncpoint wait checks with timestamps. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace records snapshot channel ids, job ids, syncpoint ids/thresholds, gather offsets/words, and ktime values; host1x hardware and jobs hold real state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/ktime.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Wrong syncpoint or timestamp capture makes GPU job scheduling bugs difficult to correlate with fence completion. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Submit host1x jobs with gathers and syncpoint waits, then verify push order, thresholds, and completion timestamps. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/host1x`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/host1x.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/huge_memory.h -->
# sources/distributed-fs/ceph-client/include/trace/events/huge_memory.h

Purpose: Transparent huge page and khugepaged tracing for PMD scans, page collapse, file collapse, isolation, swapin, and scan summaries.

Important APIs/types/functions: Declares trace-event macros/classes `trace:mm_collapse_huge_page`, `trace:mm_collapse_huge_page_isolate`, `trace:mm_collapse_huge_page_swapin`, `trace:mm_khugepaged_collapse_file`, `trace:mm_khugepaged_scan`, `trace:mm_khugepaged_scan_file`, `trace:mm_khugepaged_scan_pmd`. Defines or exports symbolic enums/helpers `a`. Representative payload fields include `addr:unsigned long`, `filename`, `full_scan_finished:bool`, `hpfn:unsigned long`, `index:pgoff_t`, `is_shmem:bool`, `isolated:int`, `mm:struct mm_struct *`, `none_or_zero:int`, `nr:int`, `pfn:unsigned long`, `present:int`, `progress:unsigned int`, `referenced:int`, `result:int`, `ret:int`, `status:int`, `swap:int`, `swapped_in:int`, `unmapped:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events follow khugepaged as it scans VMAs/files, isolates candidate pages, swaps in missing pages, attempts collapse, and records result enums. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace entries capture mm/vma addresses, pfn/isolate counts, writable flags, file indexes, HPAGE_PMD order, node, and result codes; VM state lives elsewhere. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include  <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Result enums must stay synchronized with THP code, and traces can sample rapidly changing memory layout under mmap/page-table locks. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run THP collapse tests for anonymous and file-backed memory, including failure reasons, swapin, and isolation counts. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/huge_memory`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/huge_memory.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/hugetlbfs.h -->
# sources/distributed-fs/ceph-client/include/trace/events/hugetlbfs.h

Purpose: hugetlbfs tracepoints for inode allocation/free/eviction, attribute changes, and fallocate operations.

Important APIs/types/functions: Declares trace-event macros/classes `class:hugetlbfs__inode`, `event:hugetlbfs_evict_inode`, `event:hugetlbfs_free_inode`, `trace:hugetlbfs_alloc_inode`, `trace:hugetlbfs_fallocate`, `trace:hugetlbfs_setattr`. Defines or exports symbolic enums/helpers none. Representative payload fields include `blocks:blkcnt_t`, `d_len:unsigned int`, `d_name`, `dev:dev_t`, `dir:u64`, `ia_mode:unsigned int`, `ia_size:loff_t`, `ia_valid:unsigned int`, `ino:u64`, `len:loff_t`, `mode:__u16`, `mode:int`, `nlink:unsigned int`, `offset:loff_t`, `old_size:loff_t`, `ret:int`, `seals:unsigned int`, `size:loff_t`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The header uses inode event classes plus setattr/fallocate events to expose huge page size, inode numbers, blocks, mode, uid/gid, offsets, lengths, and return codes. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Persistent state is inode/page cache/filesystem state; trace buffers hold sampled metadata during operations. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Large offsets and huge-page alignment failures must be printed accurately or capacity and reservation bugs are hard to reproduce. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Mount hugetlbfs, create/unlink files, change attributes, and run fallocate punch/allocate cases while checking trace metadata. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/hugetlbfs`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/hugetlbfs.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/hw_pressure.h -->
# sources/distributed-fs/ceph-client/include/trace/events/hw_pressure.h

Purpose: Hardware pressure tracing for CPU scheduler thermal/pressure updates.

Important APIs/types/functions: Declares trace-event macros/classes `trace:hw_pressure_update`. Defines or exports symbolic enums/helpers none. Representative payload fields include `cpu:int`, `hw_pressure:unsigned long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. A compact event records CPU id, new hardware pressure value, and whether the update is capped as scheduler topology updates capacity pressure. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The scheduler owns persistent capacity state; tracing captures point-in-time pressure updates. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Bad CPU ids or pressure scaling in traces can lead to incorrect scheduler performance diagnosis. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Drive thermal/capacity pressure updates and verify trace values match scheduler debugfs or capacity instrumentation. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/hw_pressure`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/hw_pressure.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/hwmon.h -->
# sources/distributed-fs/ceph-client/include/trace/events/hwmon.h

Purpose: Hardware monitoring sysfs attribute tracing for numeric and string attribute show/store paths.

Important APIs/types/functions: Declares trace-event macros/classes `class:hwmon_attr_class`, `event:hwmon_attr_show`, `event:hwmon_attr_store`, `trace:hwmon_attr_show_string`. Defines or exports symbolic enums/helpers none. Representative payload fields include `attr_name`, `index:int`, `label`, `val:long long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Shared attribute classes record device name, attribute name, index/channel, value, and return code; a separate string show event records text values. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace events snapshot hwmon attribute I/O; hwmon device drivers own sensor state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Sensor labels can contain user-visible strings, and trace coverage depends on drivers routing through hwmon core helpers. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Read/write hwmon sysfs attributes across numeric and string sensors and verify values and errors in trace output. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/hwmon`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/hwmon.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/i2c.h -->
# sources/distributed-fs/ceph-client/include/trace/events/i2c.h

Purpose: I2C master transfer tracing for write/read request payloads, read replies, and transfer results.

Important APIs/types/functions: Declares trace-event macros/classes `trace:i2c_read`, `trace:i2c_reply`, `trace:i2c_result`, `trace:i2c_write`. Defines or exports symbolic enums/helpers none. Representative payload fields include `adapter_nr:int`, `addr:__u16`, `buf:__u8`, `flags:__u16`, `len:__u16`, `msg_nr:__u16`, `nr_msgs:__u16`, `ret:__s16`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. TRACE_EVENT_FN hooks register/unregister trace callbacks around adapter transfers, copying message buffers for write/read/reply and logging final result counts/errors. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The tracepoint snapshots adapter number, message address/flags/length, buffer bytes, and return code; I2C core and adapter own transaction state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/i2c.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Buffer capture can expose device data and must handle zero-length or invalid buffers safely; callback enablement affects overhead. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run combined write/read transfers, SMBus-like messages, NACK/timeouts, and trace enable/disable cycles with buffer content validation. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/i2c`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/i2c.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/i2c_slave.h -->
# sources/distributed-fs/ceph-client/include/trace/events/i2c_slave.h

Purpose: I2C slave callback tracing for read/write requested, processed, received, and stop events.

Important APIs/types/functions: Declares trace-event macros/classes `trace:i2c_slave`. Defines or exports symbolic enums/helpers `I2C_SLAVE_READ_PROCESSED`, `I2C_SLAVE_READ_REQUESTED`, `I2C_SLAVE_STOP`, `I2C_SLAVE_WRITE_RECEIVED`, `I2C_SLAVE_WRITE_REQUESTED`. Representative payload fields include `adapter_nr:int`, `addr:__u16`, `buf:__u8`, `event:enum i2c_slave_event`, `len:__u16`, `ret:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The single event maps slave event enums to strings and records adapter number, slave address, event type, and value byte. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Slave driver state persists elsewhere; trace entries capture callback invocations and byte values. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/i2c.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Event ordering is protocol-sensitive and byte values may be stale or undefined for some slave events if used incorrectly. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise slave read/write/stop callbacks against a test master and verify enum names and byte values. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/i2c_slave`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/i2c_slave.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ib_mad.h -->
# sources/distributed-fs/ceph-client/include/trace/events/ib_mad.h

Purpose: InfiniBand MAD tracing for send queueing, send/receive completion, agent registration, and OPA SMI/IB route handling.

Important APIs/types/functions: Declares trace-event macros/classes `class:ib_mad_agent_template`, `class:ib_mad_opa_ib_template`, `class:ib_mad_opa_smi_template`, `class:ib_mad_send_template`, `event:ib_mad_create_agent`, `event:ib_mad_error_handler`, `event:ib_mad_handle_ib_smi`, `event:ib_mad_handle_opa_smi`, `event:ib_mad_handle_out_ib_smi`, `event:ib_mad_handle_out_opa_smi`, `event:ib_mad_ib_send_mad`, `event:ib_mad_recv_done_agent`, `event:ib_mad_send_done_agent`, `event:ib_mad_send_done_resend`, `event:ib_mad_unregister_agent`, `trace:ib_mad_recv_done_handler`, `trace:ib_mad_send_done_handler`. Defines or exports symbolic enums/helpers none. Representative payload fields include `agent_priv:void *`, `attr_id:u16`, `attr_mod:u32`, `base_version:u8`, `class_specific:u16`, `class_version:u8`, `dev_index:u32`, `dlid:u32`, `dr_dlid:u32`, `dr_slid:u32`, `hi_tid:u32`, `hop_cnt:u8`, `hop_ptr:u8`, `initial_path:u8`, `length:u32`, `max_retries:int`, `method:u8`, `mgmt_class:u8`, `mgmt_class_version:u8`, `mkey:u64`, `port_num:u8`, `qp_num:u32`, `retries_left:int`, `retry:int`, `return_path:u8`, `rqkey:u32`, `rqpn:u32`, `sl:u8`, ... plus 7 more.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Event classes cover send templates, send/receive done handlers, MAD agent lifecycle, and OPA SMI/IB packet routing with device/port/qpn/status/transaction metadata. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace records snapshot MAD headers, wc status, agent ids, device names, ports, qp numbers, base versions, classes, methods, attributes, and route fields. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <rdma/ib_mad.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: MAD headers are protocol-dense; wrong byte order or missing route fields can invalidate fabric-management debugging. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run MAD agent registration plus send/receive completions, including timeout/error statuses and OPA route cases. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/ib_mad`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ib_mad.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ib_umad.h -->
# sources/distributed-fs/ceph-client/include/trace/events/ib_umad.h

Purpose: Userspace InfiniBand MAD tracing for user MAD send/receive/read/write/ioctl-style transitions.

Important APIs/types/functions: Declares trace-event macros/classes `class:ib_umad_template`, `event:ib_umad_read_recv`, `event:ib_umad_read_send`, `event:ib_umad_write`. Defines or exports symbolic enums/helpers none. Representative payload fields include `attr_id:u16`, `attr_mod:u32`, `base_version:u8`, `class_specific:u16`, `class_version:u8`, `dev_index:u32`, `flow_label:u32`, `gid:u8`, `gid_index:u8`, `grh_present:u8`, `hop_limit:u8`, `id:u32`, `length:u32`, `lid:u16`, `mad_status:u16`, `method:u8`, `mgmt_class:u8`, `path_bits:u8`, `pkey_index:u16`, `port_num:u8`, `qkey:u32`, `qpn:u32`, `retires:u32`, `sl:u8`, `status:u32`, `tid:u64`, `timeout_ms:u32`, `traffic_class:u8`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. A shared template records device, port, agent id, status, timeout, retries, length, qpn/qkey, lids, pkeys, and method/class metadata. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The kernel umad layer owns queueing and userspace file state; traces are sampled request/response payload metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Trace output can expose fabric addressing and management payload shape, and length/status mismatches can confuse user/kernel boundary debugging. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise umad send/receive with valid and failing agents and verify lengths, qpn/qkey, LID, and status fields. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/ib_umad`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ib_umad.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/icmp.h -->
# sources/distributed-fs/ceph-client/include/trace/events/icmp.h

Purpose: ICMP send tracing for generated IPv4 ICMP errors and control messages.

Important APIs/types/functions: Declares trace-event macros/classes `trace:icmp_send`. Defines or exports symbolic enums/helpers none. Representative payload fields include `code:int`, `daddr:__u8`, `dport:__u16`, `saddr:__u8`, `skbaddr:const void *`, `sport:__u16`, `type:int`, `ulen:unsigned short`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The event records SKB address, source/destination addresses, ICMP type/code, interface index, and original IP header fields when icmp_send is invoked. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Network stack state persists in the skb and routes; trace entries snapshot selected header and device data. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/icmp.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Malformed or non-linear skbs can make header extraction delicate, and addresses may be sensitive in production traces. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Trigger TTL exceeded, port unreachable, fragmentation-needed, and filtered cases and verify addresses and ICMP type/code output. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/icmp`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/icmp.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/initcall.h -->
# sources/distributed-fs/ceph-client/include/trace/events/initcall.h

Purpose: Kernel initcall tracing for initcall level, start, and finish timing/results.

Important APIs/types/functions: Declares trace-event macros/classes `trace:initcall_finish`, `trace:initcall_level`, `trace:initcall_start`. Defines or exports symbolic enums/helpers none. Representative payload fields include `level`, `ret:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Boot-time initcall execution emits level changes, function start pointers, and finish events with return value and duration. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: No persistent state is owned; tracing snapshots boot sequencing and timing metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Function pointer printing depends on kallsyms/symbolization, and long initcall durations need correct units. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Boot with initcall tracing enabled and compare start/finish nesting, levels, return codes, and durations with dmesg initcall debug. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/initcall`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/initcall.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/intel-sst.h -->
# sources/distributed-fs/ceph-client/include/trace/events/intel-sst.h

Purpose: Intel SST audio DSP IPC tracing for message headers, mailbox transfers, and mailbox metadata.

Important APIs/types/functions: Declares trace-event macros/classes `class:sst_ipc_mailbox`, `class:sst_ipc_mailbox_info`, `class:sst_ipc_msg`, `event:sst_ipc_inbox_rdata`, `event:sst_ipc_inbox_read`, `event:sst_ipc_inbox_wdata`, `event:sst_ipc_inbox_write`, `event:sst_ipc_msg_rx`, `event:sst_ipc_msg_tx`, `event:sst_ipc_outbox_rdata`, `event:sst_ipc_outbox_read`, `event:sst_ipc_outbox_wdata`, `event:sst_ipc_outbox_write`. Defines or exports symbolic enums/helpers none. Representative payload fields include `offset:unsigned int`, `size:unsigned int`, `val:unsigned int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Event classes track IPC messages, mailbox payload buffers, and mailbox info for send/receive/irq/work paths with timestamps and sizes. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: DSP firmware/driver owns persistent mailbox state; trace buffers store headers, pointer addresses, mailbox bytes, and ktime samples. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/types.h>`, `#include <linux/ktime.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Mailbox payload capture can be verbose and must respect buffer sizes; firmware ABI changes can make message decode stale. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise SST IPC send/response, IRQ receive, and mailbox dump paths while checking sizes and timing. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/intel-sst`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/intel-sst.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/intel_ifs.h -->
# sources/distributed-fs/ceph-client/include/trace/events/intel_ifs.h

Purpose: Intel In-Field Scan tracing for scan status and SBAF status reporting.

Important APIs/types/functions: Declares trace-event macros/classes `trace:ifs_sbaf`, `trace:ifs_status`. Defines or exports symbolic enums/helpers none. Representative payload fields include `batch:int`, `bundle:u16`, `pgm:u16`, `start:u16`, `status:u64`, `stop:u16`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The events record CPU/package context, batch/test ids, status chunks, control/error fields, and ktime for IFS diagnostics. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Hardware scan status persists in model-specific registers; tracing snapshots the decoded values at status points. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/ktime.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Incorrect package/CPU association or status decoding can misclassify silicon self-test failures. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run IFS status and SBAF reporting paths on supported hardware or mocked MSR reads and validate status fields. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/intel_ifs`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/intel_ifs.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/intel_ish.h -->
# sources/distributed-fs/ceph-client/include/trace/events/intel_ish.h

Purpose: Intel Integrated Sensor Hub transport tracing for raw dump buffers.

Important APIs/types/functions: Declares trace-event macros/classes `trace:ishtp_dump`. Defines or exports symbolic enums/helpers none. Representative payload fields include `message`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. A single dump event records the provided byte buffer through the tracing array/dynamic data mechanism. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: ISH protocol state remains in the transport driver; trace records are transient byte snapshots. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Raw buffer dumps can expose firmware data and must be bounded by correct length handling. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Enable ISH tracing during host/firmware traffic and verify buffer length, data truncation behavior, and no overread. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/intel_ish`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/intel_ish.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/io_uring.h -->
# sources/distributed-fs/ceph-client/include/trace/events/io_uring.h

Purpose: io_uring tracing for ring creation, registration, request submission/defer/link/failure/completion, polling, task work, CQ overflow, and short writes.

Important APIs/types/functions: Declares trace-event macros/classes `trace:io_uring_complete`, `trace:io_uring_cqe_overflow`, `trace:io_uring_cqring_wait`, `trace:io_uring_create`, `trace:io_uring_defer`, `trace:io_uring_fail_link`, `trace:io_uring_file_get`, `trace:io_uring_link`, `trace:io_uring_local_work_run`, `trace:io_uring_poll_arm`, `trace:io_uring_queue_async_work`, `trace:io_uring_register`, `trace:io_uring_req_failed`, `trace:io_uring_short_write`, `trace:io_uring_submit_req`, `trace:io_uring_task_add`, `trace:io_uring_task_work_run`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr3:u64`, `addr:u64`, `buf_index:u16`, `cflags:u32`, `cflags:unsigned`, `count:int`, `count:unsigned int`, `cq_entries:u32`, `ctx:void *`, `data:unsigned long long`, `error:int`, `events:int`, `extra1:u64`, `extra2:u64`, `fd:int`, `file_index:u32`, `flags:u32`, `flags:u8`, `flags:unsigned long long`, `fpos:u64`, `got:u64`, `hashed:bool`, `ioprio:u8`, `len:u32`, `link:void *`, `loops:unsigned int`, `mask:int`, `min_events:int`, ... plus 22 more.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Request lifecycle paths emit context/request pointers, user_data, opcodes via io_uring_get_opcode, SQ/CQ sizes, registration counts, CQE results, poll masks, task-work counts, and malformed SQE fields. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The io_ring_ctx and io_kiocb own state; trace entries snapshot request/cqe/sqe data, including CQE32 extras when configured. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <uapi/linux/io_uring.h>`, `#include <linux/io_uring_types.h>`, `#include <linux/io_uring.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Pointer/user_data traces are correlators but can expose process structure; races around request reuse make event ordering important. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run io_uring setup/register, fixed file use, linked operations, async work, poll, overflow, malformed SQE, short-write, and CQE32 tests with trace correlation. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/io_uring`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/io_uring.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/iocost.h -->
# sources/distributed-fs/ceph-client/include/trace/events/iocost.h

Purpose: blk-iocost controller tracing for iocg activation/inactivation, inuse updates, vrate adjustment, and debt forgiveness.

Important APIs/types/functions: Declares trace-event macros/classes `class:iocg_inuse_update`, `class:iocost_iocg_state`, `event:iocost_inuse_adjust`, `event:iocost_inuse_shortage`, `event:iocost_inuse_transfer`, `event:iocost_iocg_activate`, `event:iocost_iocg_idle`, `trace:iocost_ioc_vrate_adj`, `trace:iocost_iocg_forgive_debt`. Defines or exports symbolic enums/helpers none. Representative payload fields include `busy_level:int`, `cgroup`, `cur_period:u64`, `devname`, `hweight_active:u64`, `hweight_inuse:u64`, `inuse:u32`, `last_period:u64`, `new_debt:u64`, `new_delay:u64`, `new_hweight_inuse:u64`, `new_inuse:u32`, `new_vrate:u64`, `now:u64`, `nr_lagging:int`, `nr_shortages:int`, `old_debt:u64`, `old_delay:u64`, `old_hweight_inuse:u64`, `old_inuse:u32`, `old_vrate:u64`, `read_missed_ppm:u32`, `rq_wait_pct:u32`, `usage_pct:u32`, `vnow:u64`, `vrate:u64`, `vtime:u64`, `weight:u32`, ... plus 1 more.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Event classes record cgroup path, device major/minor, active/debt/inuse/weight/hweight/vtime metrics, and controller virtual-rate changes. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The block cgroup controller owns persistent cost model state; traces sample iocg/ioc fields during recalculation and forgiveness. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Cgroup path resolution and high-resolution virtual time values can be expensive or misleading if sampled after state changes. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run blk-iocost workloads with active/inactive cgroups, weight changes, debt, and vrate adjustment while checking metrics. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/iocost`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/iocost.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/iommu.h -->
# sources/distributed-fs/ceph-client/include/trace/events/iommu.h

Purpose: IOMMU tracing for group/device lifecycle, map/unmap operations, and IOMMU errors.

Important APIs/types/functions: Declares trace-event macros/classes `class:iommu_device_event`, `class:iommu_error`, `class:iommu_group_event`, `event:add_device_to_group`, `event:attach_device_to_domain`, `event:io_page_fault`, `event:remove_device_from_group`, `trace:map`, `trace:unmap`. Defines or exports symbolic enums/helpers none. Representative payload fields include `device`, `driver`, `flags:int`, `gid:int`, `iova:u64`, `paddr:u64`, `size:size_t`, `unmapped_size:size_t`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Group/device events record group ids and device names; map/unmap events record IOVA, physical address, size, and protection; error events capture reason and addresses. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: IOMMU domains and page tables persist outside tracing; trace entries hold transient translation metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Address traces can expose DMA layout, and protection/size mismatches can hide security-critical mapping bugs. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise device attach/detach, DMA map/unmap, and fault/error paths on an IOMMU-enabled system. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/iommu`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/iommu.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ipi.h -->
# sources/distributed-fs/ceph-client/include/trace/events/ipi.h

Purpose: Inter-processor interrupt tracing for send targets, raises, and handler entry/exit.

Important APIs/types/functions: Declares trace-event macros/classes `class:ipi_handler`, `event:ipi_entry`, `event:ipi_exit`, `trace:ipi_raise`, `trace:ipi_send_cpu`, `trace:ipi_send_cpumask`. Defines or exports symbolic enums/helpers none. Representative payload fields include `callback:void *`, `callsite:void *`, `cpu:unsigned int`, `reason:const char *`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record target CPU or cpumask and callback names/reasons; handler classes bracket IPI handling. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: IPI delivery state is architecture/scheduler state; trace records sample requested targets and handler activity. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Callback string lifetime and cpumask formatting must remain valid; high-frequency IPIs can produce large traces. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Trigger reschedule, function-call, and custom IPIs and compare send/raise/handler ordering across CPUs. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/ipi`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ipi.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/irq.h -->
# sources/distributed-fs/ceph-client/include/trace/events/irq.h

Purpose: IRQ, softirq, and tasklet tracepoints for hard IRQ handler entry/exit and bottom-half lifecycle.

Important APIs/types/functions: Declares trace-event macros/classes `class:softirq`, `class:tasklet`, `event:softirq_entry`, `event:softirq_exit`, `event:softirq_raise`, `event:tasklet_entry`, `event:tasklet_exit`, `trace:irq_handler_entry`, `trace:irq_handler_exit`. Defines or exports symbolic enums/helpers `sirq##_SOFTIRQ`. Representative payload fields include `func:void *`, `irq:int`, `name`, `ret:int`, `tasklet:void *`, `vec:unsigned int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Hard IRQ events record irq number, action name, and return; softirq and tasklet classes record vector/action and handler function addresses for raise/entry/exit. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Interrupt controller and softirq subsystem own state; tracing records execution samples. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: High-rate IRQ tracing can perturb latency, and enum/vector names must stay synchronized with softirq definitions. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Generate hard IRQs, softirqs, and tasklets while validating entry/exit pairs and handler names. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/irq`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/irq.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/irq_matrix.h -->
# sources/distributed-fs/ceph-client/include/trace/events/irq_matrix.h

Purpose: IRQ matrix allocator tracing for global and per-CPU vector accounting.

Important APIs/types/functions: Declares trace-event macros/classes `class:irq_matrix_cpu`, `class:irq_matrix_global`, `class:irq_matrix_global_update`, `event:irq_matrix_alloc`, `event:irq_matrix_alloc_managed`, `event:irq_matrix_assign`, `event:irq_matrix_assign_system`, `event:irq_matrix_free`, `event:irq_matrix_offline`, `event:irq_matrix_online`, `event:irq_matrix_remove_managed`, `event:irq_matrix_remove_reserved`, `event:irq_matrix_reserve`, `event:irq_matrix_reserve_managed`. Defines or exports symbolic enums/helpers none. Representative payload fields include `allocated:unsigned int`, `available:unsigned int`, `bit:int`, `cpu:unsigned int`, `global_available:unsigned int`, `global_reserved:unsigned int`, `managed:unsigned int`, `online:bool`, `online_maps:unsigned int`, `total_allocated:unsigned int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record matrix online/available/allocated/reserved counts, global updates, and CPU-local vector allocation/free/reservation transitions. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The irq_matrix object owns persistent vector allocation; trace entries sample counters and CPU id. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Counter snapshots must be taken while allocator state is coherent or CPU hotplug/vector leak debugging becomes unreliable. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Stress IRQ vector allocation/free, CPU hotplug, managed vectors, and reservation paths with tracefs enabled. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/irq_matrix`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/irq_matrix.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/iscsi.h -->
# sources/distributed-fs/ceph-client/include/trace/events/iscsi.h

Purpose: iSCSI transport/session logging tracepoints using shared formatted-message classes.

Important APIs/types/functions: Declares trace-event macros/classes `class:iscsi_log_msg`, `event:iscsi_dbg_conn`, `event:iscsi_dbg_eh`, `event:iscsi_dbg_session`, `event:iscsi_dbg_sw_tcp`, `event:iscsi_dbg_tcp`, `event:iscsi_dbg_trans_conn`, `event:iscsi_dbg_trans_session`. Defines or exports symbolic enums/helpers none. Representative payload fields include `dname`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events mirror iSCSI debug categories such as session, connection, endpoint, TCP, error, and login logging with dynamically formatted messages. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Trace buffers hold formatted strings; iSCSI session/connection state remains in transport structures. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Formatted logging must avoid unbounded strings and may expose target/session identifiers. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise login, connection recovery, command errors, endpoint teardown, and TCP transport logs with tracing enabled. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/iscsi`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/iscsi.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/jbd2.h -->
# sources/distributed-fs/ceph-client/include/trace/events/jbd2.h

Purpose: JBD2 journaling tracepoints for checkpointing, transaction commit phases, handle lifecycle, stats, log tail updates, superblock writes, stalls, and shrinker activity.

Important APIs/types/functions: Declares trace-event macros/classes `class:jbd2_commit`, `class:jbd2_handle_start_class`, `class:jbd2_journal_shrink`, `event:jbd2_commit_flushing`, `event:jbd2_commit_locking`, `event:jbd2_commit_logging`, `event:jbd2_drop_transaction`, `event:jbd2_handle_restart`, `event:jbd2_handle_start`, `event:jbd2_shrink_count`, `event:jbd2_shrink_scan_enter`, `event:jbd2_start_commit`, `trace:jbd2_checkpoint`, `trace:jbd2_checkpoint_stats`, `trace:jbd2_end_commit`, `trace:jbd2_handle_extend`, `trace:jbd2_handle_stats`, `trace:jbd2_lock_buffer_stall`, `trace:jbd2_run_stats`, `trace:jbd2_shrink_checkpoint_list`, `trace:jbd2_shrink_scan_exit`, `trace:jbd2_submit_inode_data`, ... plus 2 more. Defines or exports symbolic enums/helpers none. Representative payload fields include `block_nr:unsigned long`, `blocks:__u32`, `blocks_logged:__u32`, `buffer_credits:int`, `chp_time:unsigned long`, `count:unsigned long`, `dev:dev_t`, `dirtied_blocks:int`, `dropped:__u32`, `first_tid:tid_t`, `flushing:unsigned long`, `forced_to_close:__u32`, `freed:unsigned long`, `handle_count:__u32`, `head:tid_t`, `ino:ino_t`, `interval:int`, `last_tid:tid_t`, `line_no:unsigned int`, `locked:unsigned long`, `logging:unsigned long`, `next_tid:tid_t`, `nr_freed:unsigned long`, `nr_shrunk:unsigned long`, `nr_to_scan:unsigned long`, `request_delay:unsigned long`, `requested_blocks:int`, `result:int`, ... plus 11 more.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The header defines commit event classes and numerous events that follow transaction start/lock/flush/commit/checkpoint, inode data submission, handle extend/stats, run/checkpoint stats, and journal shrink scans. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Journal state persists in jbd2 structures and on-disk logs; trace entries snapshot device, transaction ids, block counts, handles, credits, timings, shrinker counts, and errors. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/jbd2.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Transaction id ordering and block count units are critical; missing a phase trace can make commit latency attribution wrong. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run ext4/jbd2 workloads with fsync, checkpoint pressure, shrinker activity, handle credit extension, and writeback stalls while checking transaction timelines. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/jbd2`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/jbd2.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/kmem.h -->
# sources/distributed-fs/ceph-client/include/trace/events/kmem.h

Purpose: Kernel memory allocation/free tracing for slab, kmalloc, page allocator, watermark/reserve setup, fragmentation, per-cpu drains, and RSS stats.

Important APIs/types/functions: Declares trace-event macros/classes `class:mm_page`, `event:mm_page_alloc_zone_locked`, `trace:kfree`, `trace:kmalloc`, `trace:kmem_cache_alloc`, `trace:kmem_cache_free`, `trace:mm_calculate_totalreserve_pages`, `trace:mm_page_alloc`, `trace:mm_page_alloc_extfrag`, `trace:mm_page_free`, `trace:mm_page_free_batched`, `trace:mm_page_pcpu_drain`, `trace:mm_setup_per_zone_lowmem_reserve`, `trace:mm_setup_per_zone_wmarks`, `trace:rss_stat`. Defines or exports symbolic enums/helpers `a`. Representative payload fields include `accounted:bool`, `alloc_migratetype:int`, `alloc_order:int`, `bytes_alloc:size_t`, `bytes_req:size_t`, `call_site:unsigned long`, `change_ownership:int`, `curr:unsigned int`, `fallback_migratetype:int`, `fallback_order:int`, `gfp_flags:unsigned long`, `lowmem_reserve:long`, `member:int`, `migratetype:int`, `mm_id:unsigned int`, `name`, `node:int`, `node_id:int`, `order:unsigned int`, `percpu_refill:int`, `pfn:unsigned long`, `ptr:const void *`, `size:long`, `totalreserve_pages:unsigned long`, `upper_name`, `watermark_high:unsigned long`, `watermark_low:unsigned long`, `watermark_min:unsigned long`, ... plus 1 more.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Allocation/free events record call sites, pointers, requested/allocated bytes, gfp flags, slab names, page order/migratetype, pfn, zone/node, reserves, and RSS member changes. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Allocator state persists in slab/page allocator/mm structures; trace entries are samples of allocation and accounting transitions. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/types.h>`, `#include <linux/tracepoint.h>`, `#include <trace/events/mmflags.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Pointer exposure, high volume, and gfp/migratetype symbolic drift are main risks; page reuse makes correlation time-sensitive. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run slab/kmalloc/page allocation stress, compaction/fragmentation scenarios, watermark initialization, and RSS accounting tests with trace filters. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/kmem`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/kmem.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ksm.h -->
# sources/distributed-fs/ceph-client/include/trace/events/ksm.h

Purpose: Kernel Samepage Merging tracepoints for scans, enter/exit, merge/remove events, and advisor decisions.

Important APIs/types/functions: Declares trace-event macros/classes `class:ksm_enter_exit_template`, `class:ksm_scan_template`, `event:ksm_enter`, `event:ksm_exit`, `event:ksm_start_scan`, `event:ksm_stop_scan`, `trace:ksm_advisor`, `trace:ksm_merge_one_page`, `trace:ksm_merge_with_ksm_page`, `trace:ksm_remove_ksm_page`, `trace:ksm_remove_rmap_item`. Defines or exports symbolic enums/helpers none. Representative payload fields include `cpu_percent:unsigned int`, `err:int`, `ksm_page:void *`, `mm:void *`, `pages_to_scan:unsigned long`, `pfn:unsigned long`, `rmap_entries:u32`, `rmap_item:void *`, `scan_time:s64`, `seq:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events cover scan start/stop, mm enter/exit, merging with KSM pages, removing rmap/items, and advisor output such as scan time/pages/advice. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: KSM tree/rmap/mm state persists in mm/ksm internals; traces snapshot mm pointers, pfn/pages, stable/unstable counts, and advisor metrics. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: KSM traces include process memory pointers and can race with mm teardown; advisor fields need consistent units. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Enable KSM, merge identical pages, unmerge/remove mappings, and run advisor mode while verifying scan and merge counters. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/ksm`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/ksm.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/kvm.h -->
# sources/distributed-fs/ceph-client/include/trace/events/kvm.h

Purpose: Generic KVM tracepoints for userspace exits, vCPU wakeups, IRQ injection/ack, MMIO, FPU transitions, async page faults, halt polling, dirty rings, memory attributes, and HVA aging.

Important APIs/types/functions: Declares trace-event macros/classes `class:kvm_async_get_page_class`, `class:kvm_async_pf_nopresent_ready`, `event:kvm_async_pf_not_present`, `event:kvm_async_pf_ready`, `event:kvm_async_pf_repeated_fault`, `event:kvm_try_async_get_page`, `trace:kvm_ack_irq`, `trace:kvm_age_hva`, `trace:kvm_async_pf_completed`, `trace:kvm_dirty_ring_exit`, `trace:kvm_dirty_ring_push`, `trace:kvm_dirty_ring_reset`, `trace:kvm_fpu`, `trace:kvm_halt_poll_ns`, `trace:kvm_mmio`, `trace:kvm_set_irq`, `trace:kvm_test_age_hva`, `trace:kvm_unmap_hva_range`, `trace:kvm_userspace_exit`, `trace:kvm_vcpu_wakeup`, `trace:kvm_vm_set_mem_attributes`. Defines or exports symbolic enums/helpers none. Representative payload fields include `address:unsigned long`, `attr:unsigned long`, `dirty_index:u32`, `end:gfn_t`, `end:unsigned long`, `errno:int`, `gfn:u64`, `gpa:u64`, `grow:bool`, `gsi:unsigned int`, `gva:__u64`, `gva:u64`, `hva:unsigned long`, `index:int`, `irq_source_id:int`, `irqchip:unsigned int`, `len:u32`, `level:int`, `load:u32`, `new:unsigned int`, `ns:__u64`, `offset:u64`, `old:unsigned int`, `pin:unsigned int`, `reason:__u32`, `reset_index:u32`, `slot:u32`, `start:gfn_t`, ... plus 8 more.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events are emitted from VM/vCPU paths to track exit reasons, IRQ chip/pin/level, MMIO direction/len/value, async page-fault tokens/gfn, halt polling windows, dirty ring activity, memory attribute changes, and mmu-notifier range handling. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: KVM VM/vCPU/MMU state persists elsewhere; trace records snapshot ids, addresses, gfns, attributes, and return booleans. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Architecture-neutral fields may not capture arch-specific context, and pointer/address traces can expose guest memory layout. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run KVM selftests or VMs covering MMIO, IRQ injection, async PF, halt polling, dirty ring logging, memory attributes, and MMU notifier aging. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/kvm`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/kvm.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/kyber.h -->
# sources/distributed-fs/ceph-client/include/trace/events/kyber.h

Purpose: Kyber I/O scheduler tracing for latency measurement, token depth adjustment, and throttling.

Important APIs/types/functions: Declares trace-event macros/classes `trace:kyber_adjust`, `trace:kyber_latency`, `trace:kyber_throttled`. Defines or exports symbolic enums/helpers none. Representative payload fields include `denominator:u8`, `depth:unsigned int`, `dev:dev_t`, `domain:char`, `numerator:u8`, `percentile:u8`, `samples:unsigned int`, `type:char`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record block device names, scheduling domain, latency target/actual, queue depth adjustments, and throttled requests. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Scheduler state persists in kyber queues/domains; traces sample latency controller decisions. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/blkdev.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Device name/domain mismatch or timing unit errors can lead to wrong scheduler tuning conclusions. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run mixed read/write latency workloads under Kyber and verify latency, adjustment, and throttling events. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/kyber`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/kyber.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/libata.h -->
# sources/distributed-fs/ceph-client/include/trace/events/libata.h

Purpose: libata tracepoints and decode helpers for ATA queued command issue/complete, taskfile load/exec, BMDMA, error handling, resets, SFF state machine, and data transfer.

Important APIs/types/functions: Declares trace-event macros/classes `class:ata_eh_action_template`, `class:ata_exec_command_template`, `class:ata_link_reset_begin_template`, `class:ata_link_reset_end_template`, `class:ata_port_eh_begin_template`, `class:ata_qc_complete_template`, `class:ata_qc_issue_template`, `class:ata_sff_hsm_template`, `class:ata_sff_template`, `class:ata_transfer_data_template`, `event:ata_bmdma_setup`, `event:ata_bmdma_start`, `event:ata_bmdma_stop`, `event:ata_eh_about_to_do`, `event:ata_eh_done`, `event:ata_exec_command`, `event:ata_link_hardreset_begin`, `event:ata_link_hardreset_end`, `event:ata_link_postreset`, `event:ata_link_softreset_begin`, `event:ata_link_softreset_end`, `event:ata_port_freeze`, ... plus 21 more. Defines or exports symbolic enums/helpers none. Representative payload fields include `ata_dev:unsigned int`, `ata_port:unsigned int`, `bytes:unsigned int`, `class:unsigned int`, `cmd:unsigned char`, `ctl:unsigned char`, `deadline:unsigned long`, `dev:unsigned char`, `dev_state:unsigned char`, `eh_action:unsigned int`, `eh_err_mask:unsigned int`, `error:unsigned char`, `feature:unsigned char`, `flags:unsigned int`, `flags:unsigned long`, `hob_feature:unsigned char`, `hob_lbah:unsigned char`, `hob_lbal:unsigned char`, `hob_lbam:unsigned char`, `hob_nsect:unsigned char`, `host_stat:unsigned char`, `hsm_state:unsigned char`, `hsm_state:unsigned int`, `lbah:unsigned char`, `lbal:unsigned char`, `lbam:unsigned char`, `nsect:unsigned char`, `offset:unsigned int`, ... plus 6 more.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The header provides opcode/status/protocol/class/HSM symbolic printers plus trace classes for queued commands, completions, exec commands, EH actions, reset begin/end, port freeze/thaw, SFF HSM states, and PIO/ATAPI data movement. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: ATA port/device/qc state persists in libata; traces snapshot taskfile registers, tags, protocols, qc flags, host status, EH masks/actions, reset classes, offsets, and byte counts. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/ata.h>`, `#include <linux/libata.h>`, `#include <linux/tracepoint.h>`, `#include <linux/trace_seq.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: ATA register byte order, subcommand decode, and qc/device lifetime are delicate; bad symbolic decoding can hide hardware/driver faults. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Exercise ATA read/write/NCQ, failed completions, BMDMA, hard/soft reset, error recovery, SFF PIO, and ATAPI transfer paths with traces enabled. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/libata`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/libata.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/lock.h -->
# sources/distributed-fs/ceph-client/include/trace/events/lock.h

Purpose: Lockdep/lock tracing for acquire, acquired, release, contention begin, and contention end events.

Important APIs/types/functions: Declares trace-event macros/classes `class:lock`, `event:lock_acquired`, `event:lock_contended`, `event:lock_release`, `trace:contention_begin`, `trace:contention_end`, `trace:lock_acquire`. Defines or exports symbolic enums/helpers none. Representative payload fields include `flags:unsigned int`, `lock_addr:void *`, `lockdep_addr:void *`, `name`, `ret:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The events record lockdep map names/classes, subclass/try/read/check flags, caller ip, wait context, and contention timing/flags. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Lock state is owned by lockdep and primitives; trace entries sample lock operation metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/sched.h>`, `#include <linux/tracepoint.h>`, `#include <linux/lockdep.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Tracing lock operations is high-volume and reentrancy-sensitive; class/name pointers must remain valid. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run lockdep tests and contention microbenchmarks to validate acquire/release pairing and contention duration fields. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/lock`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/lock.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/maple_tree.h -->
# sources/distributed-fs/ceph-client/include/trace/events/maple_tree.h

Purpose: Maple tree tracing for operations, reads, and writes over tree nodes/ranges.

Important APIs/types/functions: Declares trace-event macros/classes `trace:ma_op`, `trace:ma_read`, `trace:ma_write`. Defines or exports symbolic enums/helpers none. Representative payload fields include `fn:const char *`, `index:unsigned long`, `last:unsigned long`, `max:unsigned long`, `min:unsigned long`, `node:void *`, `piv:unsigned long`, `val:void *`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record operation name, tree/node pointers, index/last ranges, slots, and values during maple-tree reads/writes. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Maple tree storage is persistent in caller-owned structures; trace entries are transient snapshots of traversal/update state. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Pointer/range traces are useful but can expose address-space layout; stale node pointers after mutation require careful ordering. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run maple tree insert/find/erase/split tests and verify read/write range and node event consistency. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/maple_tree`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/maple_tree.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mce.h -->
# sources/distributed-fs/ceph-client/include/trace/events/mce.h

Purpose: Machine Check Exception record tracing for x86 MCE hardware error reports.

Important APIs/types/functions: Declares trace-event macros/classes `trace:mce_record`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:u64`, `apicid:u32`, `bank:u8`, `cpu:u32`, `cpuid:u32`, `cpuvendor:u8`, `cs:u8`, `ip:u64`, `ipid:u64`, `mcgcap:u64`, `mcgstatus:u64`, `microcode:u32`, `misc:u64`, `ppin:u64`, `socketid:u32`, `status:u64`, `synd:u64`, `tsc:u64`, `v_data:u8`, `walltime:u64`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. A single event records machine-check fields such as CPU, bank, status, address, misc, syndrome, ip, time, walltime, and severity/context data. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: MCE records may also be logged by architecture code; this tracepoint snapshots the struct mce passed to it. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/ktime.h>`, `#include <linux/tracepoint.h>`, `#include <asm/mce.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Hardware error data is critical and architecture-specific; truncation or format drift can break postmortem analysis. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Inject corrected/uncorrected MCEs where supported and compare trace records with mcelog/rasdaemon output. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mce`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mce.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mctp.h -->
# sources/distributed-fs/ceph-client/include/trace/events/mctp.h

Purpose: MCTP key lifecycle tracing for key acquisition and release reasons.

Important APIs/types/functions: Declares trace-event macros/classes `trace:mctp_key_acquire`, `trace:mctp_key_release`. Defines or exports symbolic enums/helpers `MCTP_TRACE_KEY_CLOSED`, `MCTP_TRACE_KEY_DROPPED`, `MCTP_TRACE_KEY_INVALIDATED`, `MCTP_TRACE_KEY_REPLIED`, `MCTP_TRACE_KEY_TIMEOUT`. Representative payload fields include `laddr:__u8`, `paddr:__u8`, `reason:int`, `tag:__u8`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record key pointer, local/peer endpoint ids, tag, owner, and symbolic release reasons such as timeout, replied, invalidated, closed, or dropped. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: MCTP routing/key state persists in the network subsystem; trace entries snapshot key lifecycle metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Key pointer reuse and endpoint/tag wraparound can confuse correlation in long traces. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run MCTP request/reply, timeout, socket close, invalidation, and drop cases while checking acquire/release matching. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mctp`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mctp.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mdio.h -->
# sources/distributed-fs/ceph-client/include/trace/events/mdio.h

Purpose: MDIO bus access tracing for PHY/device register reads and writes.

Important APIs/types/functions: Declares trace-event macros/classes `trace:mdio_access`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:u8`, `busid:char`, `read:char`, `regnum:unsigned`, `val:u16`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. A conditional trace event records bus id, PHY address, register, value, operation type, and error when the condition allows logging. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: MDIO controller/PHY registers own state; traces snapshot access arguments and results. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: MDIO traffic can be frequent during link polling, and clause/address encoding must be clear for diagnostics. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Read/write PHY registers with success and error injection and verify conditional trace emission and values. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mdio`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mdio.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/memcg.h -->
# sources/distributed-fs/ceph-client/include/trace/events/memcg.h

Purpose: Memory cgroup rstat tracepoints for stats/events flushing and flush summary.

Important APIs/types/functions: Declares trace-event macros/classes `class:memcg_rstat_events`, `class:memcg_rstat_stats`, `event:count_memcg_events`, `event:mod_memcg_lruvec_state`, `event:mod_memcg_state`, `trace:memcg_flush_stats`. Defines or exports symbolic enums/helpers none. Representative payload fields include `force:bool`, `id:u64`, `item:int`, `needs_flush:bool`, `stats_updates:s64`, `val:long`, `val:unsigned long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Event classes record memcg id/path, stat/event names, values, CPU, and flush details as rstat updates propagate. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: memcg/rstat state persists in cgroup structures; trace entries snapshot propagation and flush data. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/memcontrol.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Path resolution and high-frequency stat updates can add overhead; stale cgroup names after deletion can complicate analysis. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run memory pressure across cgroups, trigger rstat flushes, and validate stats/events values against cgroupfs. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/memcg`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/memcg.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/memory-failure.h -->
# sources/distributed-fs/ceph-client/include/trace/events/memory-failure.h

Purpose: Memory failure handling tracepoint for hardware-poison page outcome reporting.

Important APIs/types/functions: Declares trace-event macros/classes `trace:memory_failure_event`. Defines or exports symbolic enums/helpers `a`. Representative payload fields include `pfn:unsigned long`, `result:int`, `type:int`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. The event records pfn, page flags/type, mapping/index, action result, and recovery status when memory_failure handles a page. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Poison state persists in page flags and memory-failure machinery; trace entries snapshot classification and outcome. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <linux/mm.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Result/action enums must stay synchronized with memory-failure code or recovery triage becomes misleading. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Inject soft-offline/hwpoison events for anonymous, file, huge, and unmovable pages and verify action/result traces. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/memory_failure`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/memory-failure.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/migrate.h -->
# sources/distributed-fs/ceph-client/include/trace/events/migrate.h

Purpose: Page migration tracepoints for migration batches, migration start, and migration PTE install/remove.

Important APIs/types/functions: Declares trace-event macros/classes `class:migration_pte`, `event:remove_migration_pte`, `event:set_migration_pte`, `trace:mm_migrate_pages`, `trace:mm_migrate_pages_start`. Defines or exports symbolic enums/helpers `a`. Representative payload fields include `addr:unsigned long`, `failed:unsigned long`, `large_folio_split:unsigned long`, `mode:enum migrate_mode`, `order:int`, `pte:unsigned long`, `reason:int`, `succeeded:unsigned long`, `thp_failed:unsigned long`, `thp_split:unsigned long`, `thp_succeeded:unsigned long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record mode/reason/result counts, migration start parameters, and migration PTE old/new PFNs for install/remove operations. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Migration state persists in page tables and page structs; trace entries snapshot migration decisions and PTE transitions. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: PFN exposure and result enum drift are risks; migration can be concurrent with reclaim/compaction/NUMA balancing. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run NUMA balancing, compaction, memory hotplug, and mbind/move_pages migration cases and validate result counts and PTE traces. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/migrate`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/migrate.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mlxsw.h -->
# sources/distributed-fs/ceph-client/include/trace/events/mlxsw.h

Purpose: mlxsw Spectrum ACL TCAM tracing for ATCAM spill, vregion rehash, migration, migration completion, and rollback failure.

Important APIs/types/functions: Declares trace-event macros/classes `trace:mlxsw_sp_acl_atcam_entry_add_ctcam_spill`, `trace:mlxsw_sp_acl_tcam_vregion_migrate`, `trace:mlxsw_sp_acl_tcam_vregion_migrate_end`, `trace:mlxsw_sp_acl_tcam_vregion_rehash`, `trace:mlxsw_sp_acl_tcam_vregion_rehash_rollback_failed`. Defines or exports symbolic enums/helpers none. Representative payload fields include `aregion:const void *`, `mlxsw_sp:const void *`, `vregion:const void *`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events expose region/vregion identifiers, region sizes, hints, chunk counts, and error conditions during TCAM rehash/migration. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: mlxsw ACL state persists in driver TCAM structures and hardware; traces snapshot control-plane transitions. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: TCAM resource traces are hardware-specific; missing rollback failures can hide ACL programming inconsistencies. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Program ACL sets that force spill, rehash, migrate, and rollback-failure paths on mlxsw test hardware or mocks. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mlxsw`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mlxsw.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mmap.h -->
# sources/distributed-fs/ceph-client/include/trace/events/mmap.h

Purpose: MM mmap tracepoints for unmapped-area search results and exit_mmap teardown.

Important APIs/types/functions: Declares trace-event macros/classes `trace:exit_mmap`, `trace:vm_unmapped_area`. Defines or exports symbolic enums/helpers none. Representative payload fields include `addr:unsigned long`, `align_mask:unsigned long`, `align_offset:unsigned long`, `flags:unsigned long`, `high_limit:unsigned long`, `length:unsigned long`, `low_limit:unsigned long`, `mm:struct mm_struct *`, `mt:struct maple_tree *`, `total_vm:unsigned long`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record unmapped area info/result fields and mm teardown state as address-space mappings are selected and destroyed. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: VMA/mm state persists in memory-management structures; trace entries snapshot addresses, lengths, flags, pgoff, and mm counters. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Address traces expose process layout and must be interpreted with ASLR and concurrent VMA changes in mind. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run mmap/munmap/brk and process-exit workloads, including top-down/bottom-up allocation failures, and validate ranges. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mmap`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mmap.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mmap_lock.h -->
# sources/distributed-fs/ceph-client/include/trace/events/mmap_lock.h

Purpose: mmap_lock tracepoints for lock acquisition attempts and returned status with memcg context.

Important APIs/types/functions: Declares trace-event macros/classes `class:mmap_lock`, `event:name`, `trace:mmap_lock_acquire_returned`. Defines or exports symbolic enums/helpers none. Representative payload fields include `memcg_id:u64`, `mm:struct mm_struct *`, `success:bool`, `write:bool`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Shared lock classes record mm pointer, write/read mode, caller ip, memcg path, and acquisition result. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: The rwsem/mmap_lock owns state; trace entries sample contention/acquisition metadata. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/memcontrol.h>`, `#include <linux/tracepoint.h>`, `#include <linux/types.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Lock tracing can be high-volume and caller IP symbolization must be accurate to identify contention sites. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run mmap_lock contention tests with reads/writes and verify acquire/release/result sequences. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mmap_lock`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mmap_lock.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mmc.h -->
# sources/distributed-fs/ceph-client/include/trace/events/mmc.h

Purpose: MMC core request tracing for command/data/stop request start and completion.

Important APIs/types/functions: Declares trace-event macros/classes `trace:mmc_request_done`, `trace:mmc_request_start`. Defines or exports symbolic enums/helpers none. Representative payload fields include `blk_addr:unsigned int`, `blksz:unsigned int`, `blocks:unsigned int`, `bytes_xfered:unsigned int`, `can_retune:unsigned int`, `cmd_arg:u32`, `cmd_err:int`, `cmd_flags:unsigned int`, `cmd_opcode:u32`, `cmd_resp:u32`, `cmd_retries:unsigned int`, `data_err:int`, `data_flags:unsigned int`, `doing_retune:unsigned int`, `hold_retune:int`, `mrq:struct mmc_request *`, `name`, `need_retune:int`, `retune_now:unsigned int`, `retune_period:unsigned int`, `sbc_arg:u32`, `sbc_err:int`, `sbc_flags:unsigned int`, `sbc_opcode:u32`, `sbc_resp:u32`, `sbc_retries:unsigned int`, `stop_arg:u32`, `stop_err:int`, ... plus 5 more.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Request start/done events record host name, command opcode/arg/flags/retries/error, data block counts/sizes/flags/errors, stop command, and SBC info. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: MMC host/card/request state persists in the MMC core and driver; trace entries snapshot request structures at start and completion. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/blkdev.h>`, `#include <linux/mmc/core.h>`, `#include <linux/mmc/host.h>`, `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Requests can include optional data/stop/SBC pieces; traces must handle NULL members and completion mutation correctly. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Run reads, writes, erase, tuning/error-retry, and command-only requests on MMC/SD/eMMC devices and compare start/done fields. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mmc`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mmc.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mmflags.h -->
# sources/distributed-fs/ceph-client/include/trace/events/mmflags.h

Purpose: Shared memory-management trace formatting helpers for GFP flags, page flags, VMA flags, compaction status, migrate types, and related enums.

Important APIs/types/functions: Declares trace-event macros/classes none. Defines or exports symbolic enums/helpers `___GFP_##a##_BIT`, `___GFP_LAST_BIT`, `___GFP_UNUSED_BIT`, `a`. Representative payload fields include none.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. This header does not declare trace events; it defines TRACE_DEFINE_ENUM entries and __def_gfpflag_names, show_gfp_flags, show_vma_flags, show_page_flags, and related symbolic helper macros consumed by other trace headers. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: It owns no runtime state; its persistent contract is compile-time symbolic mapping from bit values/enums to trace output strings. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/node.h>`, `#include <linux/mmzone.h>`, `#include <linux/compaction.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: If new flags are added without updating these helpers, memory traces become incomplete or misleading; configuration-specific flags need guarded definitions. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Build with varied MM configs and inspect kmem/compaction/migration trace output for correct flag decoding. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/mmflags`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/mmflags.h -->


<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/module.h -->
# sources/distributed-fs/ceph-client/include/trace/events/module.h

Purpose: Kernel module tracepoints for load, free, reference count changes, and module request events.

Important APIs/types/functions: Declares trace-event macros/classes `class:module_refcnt`, `event:module_get`, `event:module_put`, `trace:module_free`, `trace:module_load`, `trace:module_request`. Defines or exports symbolic enums/helpers none. Representative payload fields include `ip:unsigned long`, `name`, `refcnt:int`, `taints:unsigned int`, `wait:bool`.

Control flow: As a trace-event header, control flow is compile-time macro expansion plus runtime calls from subsystem code into generated tracepoint stubs. Events record module name, taints, reference count, caller ip, wait flag, and requested module name during module lifecycle and kmod requests. Each section is guarded by the usual trace header include pattern, defines `TRACE_SYSTEM`, and includes `trace/define_trace.h` outside the guard so the trace generator can instantiate definitions exactly once.

State and persistence behavior: Module subsystem owns live module/refcount state; trace entries snapshot lifecycle transitions and request strings. These headers do not implement durable storage; generated tracepoints copy selected values into per-CPU tracing buffers and rely on callers to pass objects that remain valid during `TP_fast_assign`.

Dependencies: `#include <linux/tracepoint.h>`, `#include <trace/define_trace.h>` The file also depends on Linux tracepoint infrastructure macros such as `TRACE_EVENT`, `DECLARE_EVENT_CLASS`, `DEFINE_EVENT`, `TP_STRUCT__entry`, `TP_fast_assign`, and `TP_printk`.

Integration points: Integrated by subsystem C files that include this header before tracepoint calls and by ftrace/perf/tracefs users that consume the generated event format files. For this Ceph-client source snapshot, these headers are broader Linux-kernel instrumentation dependencies rather than Ceph-specific client logic.

Risks: Module names and request strings can be user-influenced; refcount traces must avoid using freed module memory. General trace-header risks include format-string ABI drift, enum/string drift, pointer lifetime mistakes in `TP_fast_assign`, high event volume, and sensitive address or payload data appearing in trace buffers.

Test signals: Load/unload modules, change references, and trigger request_module success/failure paths while verifying trace order and strings. Also build with tracing enabled, inspect `/sys/kernel/tracing/events/module`-style event format output where applicable, and run subsystem tests with trace filters to confirm fields, symbolic decoders, and event ordering.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/trace/events/module.h -->
