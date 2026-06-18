<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-mgr-test.c -->
# sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-mgr-test.c

## Purpose
`fpga-mgr-test.c` is a KUnit suite for the FPGA manager core programming sequence. It uses a fake manager that records operation order, manager state at each callback, and whether header/image payloads are passed to write callbacks as expected for both linear buffers and scatter-gather tables.

## Important APIs, types, and functions
The test fixture uses `struct mgr_stats` to record callback sequence numbers and states, and `struct mgr_ctx` to hold `fpga_image_info`, `fpga_manager`, and the backing KUnit device. Fake ops are `op_parse_header()`, `op_write_init()`, `op_write()`, `op_write_sg()`, and `op_write_complete()` in `fake_mgr_ops`, with `.skip_header = true`. Tests exercise `fpga_mgr_get()`, `fpga_mgr_put()`, `fpga_mgr_lock()`, `fpga_mgr_unlock()`, `fpga_mgr_load()`, `fpga_image_info_alloc()`, and `devm_fpga_mgr_register()`.

## Control flow
Initialization allocates image info, registers a fake manager, and arranges KUnit cleanup. `init_test_buffer()` creates a synthetic image with a fixed header region and payload region. The buffer load test sets `img_info->buf/count`, calls `fpga_mgr_load()`, then validates callback order: parse header, write init, write, write complete. The SG test builds a scatterlist-backed image and validates that `write_sg` sees the complete image but skips the header internally when checking payload bytes. The lock test checks a second lock returns `-EBUSY`.

## State and persistence behavior
All state lives in KUnit allocations and `mgr_stats`. The manager core state machine is sampled at each callback but not persisted. Scatter-gather resources and image info are released through KUnit actions.

## Dependencies and integration points
The suite depends on KUnit, the FPGA manager core, scatterlist helpers, and module/KUnit test registration. It integrates through the real `fpga_mgr_load()` path and therefore observes manager state transitions, header parsing, data-size/header-size updates, lock exclusion, and callback dispatch behavior.

## Risks and edge cases
The fake callbacks always return success, so failure unwinding, partial writes, timeout handling, firmware request loading, and manager unregister races are not covered. The SG validation assumes header skipping is correctly represented by `HEADER_SIZE`; malformed headers and zero-length payloads are not tested.

## Test signals
Suite `fpga_mgr` should pass with header and payload match flags set, monotonically increasing callback sequence numbers, expected manager states captured at each callback, `-EBUSY` on recursive lock, and successful buffer and SG loads. Regressions point to manager sequencing, header skip handling, or lock/reference behavior.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/fpga/tests/fpga-mgr-test.c -->
