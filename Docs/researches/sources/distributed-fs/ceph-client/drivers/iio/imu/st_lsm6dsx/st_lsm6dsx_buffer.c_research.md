<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_buffer.c -->
# sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_buffer.c

Purpose: hardware FIFO support for ST LSM6DSx devices. It configures FIFO ODR, decimators, watermarks, hardware timestamps, and reads both legacy pattern FIFOs and newer tagged FIFOs into IIO buffers.

Important APIs/functions: exported `st_lsm6dsx_update_watermark()`, `st_lsm6dsx_resume_fifo()`, `st_lsm6dsx_read_fifo()`, `st_lsm6dsx_read_tagged_fifo()`, `st_lsm6dsx_flush_fifo()`, `st_lsm6dsx_update_fifo()`, and `st_lsm6dsx_fifo_setup()`. Internal helpers compute decimator values, pattern sample counts, FIFO mode/ODR, timestamp reset, block reads, tagged sample routing, and buffer sysfs `sampling_frequency`.

Control flow: buffer preenable calls device-specific `update_fifo(sensor, true)`. `st_lsm6dsx_update_fifo()` under `conf_lock` optionally flushes existing FIFO, enables the sensor, programs FIFO ODR, recomputes decimators/SIP, updates watermark, resumes FIFO, and updates `fifo_mask`. IRQ handling in core calls the settings-selected read routine. Pattern FIFO reads status, rounds length to whole patterns, reads pattern chunks, reconstructs gyro/accel/ext samples and timestamp samples, discards settling samples, and pushes timestamped scans. Tagged FIFO reads tagged tuples, decodes source tags, updates timestamp on timestamp tags, and routes data tags to the correct IIO device.

State and persistence: updates `hw->fifo_mask`, `hw->sip`, `hw->ts_sip`, per-sensor `sip`, `decimator`, `samples_to_discard`, `watermark`, `hwfifo_odr_mHz`, and `ts_ref`. Hardware FIFO mode, watermark registers, decimator registers, and timestamp counter state persist until reconfigured or reset.

Dependencies and integration: depends on `st_lsm6dsx.h` settings callbacks and locks, regmap, IIO kfifo buffers, scan buffers in `st_lsm6dsx_hw`, and core IRQ dispatch.

Risks: pattern math is sensitive to ODR ratios, decimators, timestamp sample insertion, and ext sensor ordering. Watermark writes combine high-register existing bits with a 16-bit bulk write. The source has duplicated/extra braces and duplicate `case ST_LSM6DSX_EXT2_TAG` lines in the viewed copy, which are compile-risk signals if not masked by local context. FIFO flush ignores the return from the read routine and then bypasses FIFO.

Test signals: enabling/disabling accel, gyro, and external FIFO channels; watermark clamping and register values; FIFO ODR sysfs; pattern FIFO with mismatched ODRs; tagged FIFO source routing; timestamp reset rollover handling; samples-to-discard behavior; and IRQ-driven FIFO drain loops.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/drivers/iio/imu/st_lsm6dsx/st_lsm6dsx_buffer.c -->
