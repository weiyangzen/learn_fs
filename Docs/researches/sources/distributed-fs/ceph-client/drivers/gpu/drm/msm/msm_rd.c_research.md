# sources/distributed-fs/ceph-client/drivers/gpu/drm/msm/msm_rd.c

## Purpose
Implements MSM debugfs RD capture streams used by freedreno/cffdump tooling. The `rd` file streams submitted command buffers, and `hangrd` captures offending submits during GPU hangs. Optional `rd_full` captures full buffer contents.

## Important APIs, Types, and Functions
- `enum rd_sect_type` defines the binary section protocol.
- `struct msm_rd_state` stores device, open flag, read/write mutexes, waitqueue, circular buffer, and storage.
- `msm_rd_debugfs_init()` creates `rd` and `hangrd`; `msm_rd_debugfs_cleanup()` frees them.
- `rd_open()` enforces single-open, resets FIFO, and writes GPU/chip id sections.
- `rd_read()` drains the circular buffer to userspace.
- `rd_write()` and `rd_write_section()` produce binary sections with blocking backpressure.
- `msm_rd_dump_submit()` serializes submit metadata, BO GPU addresses/contents, and command stream addresses.
- `snapshot_buf()` writes `RD_GPUADDR` and optional `RD_BUFFER_CONTENTS`.

## Control Flow
Userspace opens a debugfs file, causing the FIFO to reset and GPU id metadata to be emitted. Producers call `msm_rd_dump_submit()` under `gpu->lock`; it skips work if the stream is not open, serializes messages, task/fence identity, BO snapshots, and command-stream address sections. In VM_BIND mode it iterates all GPUVAs in the submit VM and honors `MSM_VMA_DUMP`; legacy mode iterates submit BOs and commands, snapshotting command buffers even when full BO dump is disabled. Readers block until FIFO data is available and wake producers as space opens.

## State and Persistence
State is transient debugfs memory in `priv->rd` and `priv->hangrd`. The circular buffer is only 512 bytes and blocks producers when full while open. `rd_full` is a module parameter controlling capture depth. Output persistence is up to userspace redirecting the stream.

## Dependencies and Integration Points
Depends on debugfs, waitqueues, circular buffer macros, MSM GEM vaddr helpers, GPU parameter hooks, submit structures, VM_BIND GPUVA iteration, and hang recovery in `msm_gpu.c`. `msm_gem_submit.c` dumps normal submits; hang recovery dumps offending submits.

## Risks
Risks include blocking producers if userspace opens but does not read, capturing large buffer contents with `rd_full`, object lifetime during snapshots, and VM_BIND iteration requiring the VM reservation lock. The code uses separate read/write mutexes, waitqueue backpressure, and checks `rd->open` while writing.

## Test Signals
Read `rd` while running workloads and verify cffdump can parse GPU/chip ids, BO addresses, command streams, and optional contents. Force a hang and inspect `hangrd`. Test VM_BIND dumps, `rd_full`, close while producer waits, and single-open rejection.
