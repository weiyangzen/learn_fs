<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jitdump.c -->
# sources/distributed-fs/ceph-client/tools/perf/util/jitdump.c

## Purpose

`jitdump.c` converts JIT runtime dump files into ELF images and injected perf mmap2 events so perf can symbolize JIT-generated code.

## Important APIs, Types, and Functions

`struct jit_buf_desc` carries input/output perf data, session/machine, namespace info, jitdump buffers, debug/unwind side data, output directory, byte count, and timestamp mode. Public `jit_process()` is the main entry. Important internal functions are `jit_open()`, `jit_get_next_entry()`, `jit_process_dump()`, `jit_repipe_code_load()`, `jit_repipe_code_move()`, `jit_repipe_debug_info()`, `jit_repipe_unwinding_info()`, `jit_emit_elf()`, `jit_detect()`, `convert_timestamp()`, `jit_add_pid()`, and `jit_has_pid()`.

## Control Flow

`jit_process()` finds or creates the thread for the mmap, obtains namespace info, detects `.../jit-<pid>.dump`, and if matched initializes a descriptor and calls `jit_inject()`. Opening validates header magic, byte order, version, flags, timestamp mode, and clock requirements. The dump loop reads each record prefix and payload, byte-swaps if needed, and dispatches load/move/debug/unwind records. Code-load records write a `jitted-<pid>-<index>.so` ELF with optional debug/unwind data, synthesize a `PERF_RECORD_MMAP2`, process it into the machine, write it to output, and mark the generated DSO hit. Code-move records synthesize updated mmap2 records for moved code.

## State and Persistence Behavior

The code creates persistent generated ELF files beside the jitdump file and injects persistent mmap2 records into the output perf data stream. It also marks processed pids in thread private data so later anonymous or memfd JIT code maps can be stripped. Debug and unwind side data are buffered until consumed by the next code-load record.

## Dependencies and Integration Points

It depends on jitdump format definitions, `genelf` writing, perf data output, perf event processing, build-id marking, namespace mount handling, DSO/machine/thread state, time conversion, and mmap2 sample-id layout. It integrates primarily with `perf inject --jit`.

## Risks and Edge Cases

Header validation, cross-endianness, namespace pid translation, arch timestamp conversion, path sizing, and record size validation are sensitive. `jit_open()` contains a subtle read-extra path where buffer-size bookkeeping must remain correct. Generated mmap event sizing depends on aligned filename length and `machine->id_hdr_size`. Clockid validation rejects non-arch timestamps unless events used `CLOCK_MONOTONIC`. Debug/unwind records must precede the code load they describe.

## Test Signals

Tests should include native and byte-swapped jitdump files, arch and monotonic timestamp modes, invalid flags/version, namespace pid cases, code load with debug/unwind info, code move, unknown records, generated ELF symbolization, build-id generation, and anonymous-map suppression after a processed pid.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/tools/perf/util/jitdump.c -->
