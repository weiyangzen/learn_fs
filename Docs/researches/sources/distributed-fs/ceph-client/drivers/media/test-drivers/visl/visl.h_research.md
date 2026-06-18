# sources/distributed-fs/ceph-client/drivers/media/test-drivers/visl/visl.h

## Purpose
`visl.h` is the central VISL header. It defines driver constants, global module-parameter declarations, debug-print helpers, device/context structures, codec/format descriptors, and shared control lookup APIs.

## Important APIs, types, and functions
Key constants include `VISL_NAME`, `VISL_M2M_NQUEUES`, and `TPG_STR_BUF_SZ`. `struct visl_ctrls` and `struct visl_coded_format_desc` describe registered controls and coded-format capabilities. `enum visl_codec` identifies the currently selected codec.

`struct visl_dev` owns the V4L2 device, video device, optional media device, device mutex, mem2mem device, and optional debugfs state. `struct visl_ctx` owns a V4L2 file handle, control handler, vb2 mutex, source/capture queue data, current codec, coded/decoded formats, TPG state, stream timing, and text buffer. `struct visl_blob` describes a debugfs bitstream blob. `visl_file_to_ctx()` maps a file to its context.

## Control flow
The header provides the shared types used by open/release, format negotiation, decode execution, debugfs, and tracepoints. Runtime behavior is implemented in the corresponding `.c` files.

## State and persistence
`struct visl_dev` is device-lifetime state; `struct visl_ctx` is per-open state; `struct visl_q_data.sequence` is per-queue streaming state. Global module parameters are declared here and defined in `visl-core.c`.

## Dependencies and integration points
It depends on Linux list/debugfs headers, V4L2 controls/device APIs, and the V4L2 TPG API. Every VISL implementation file includes or depends on it.

## Risks and test signals
Risks include conditional debugfs fields requiring matching stubs, global module-parameter effects across contexts, and structure changes affecting many files. Build coverage across debugfs/media-controller configurations and open/stream/close tests are important signals.
