## sources/distributed-fs/ceph-client/drivers/scsi/st.h

### Purpose
Defines the private data model and state constants for the SCSI tape driver. It is the structural contract consumed by `st.c` for command status, request lifetime, buffering, mode definitions, partition status, statistics, per-tape state, EOF/read/write/ready states, door locking, and sense flags.

### Important APIs, Types, and Constants
- `struct st_cmdstatus` stores normalized SCSI result, sense header, residual/remainder, fixed/descriptor format, deferred state, and FMK/EOM/ILI flags.
- `struct st_request` wraps a SCSI command, sense buffer, result, owning tape, completion pointer, and mapped bio.
- `struct st_buffer` tracks reserved buffer pages, pinned user pages, direct-I/O state, buffered byte counts, read pointer, async request, command status, and request mapping data.
- `struct st_modedef` stores per-mode behavior and defaults plus cdev/device pointers for auto-rewind and non-rewind nodes.
- `struct st_partstat` stores per-partition read/write state, EOF state, setmark status, last visited block, and driver-estimated block/file numbers.
- `struct scsi_tape_stats` contains atomic read/write/other counts, bytes, residual count, in-flight count, timing totals, and last request sizes.
- `struct scsi_tape` is the main per-device object with SCSI device pointer, lock/completion, buffer, mode array, partition states, readiness/write protection, block/density/compression/default flags, media/reset counters, debug counters, name, kref, and stats pointer.
- Constants define four modes, four partitions, maximum tape entries, EOF/EOM/EOD transitions, rw states, ready states, door lock states, QFA commands, option trinary values, and sense flag masks.

### Control Flow and State
This header contains no executable control flow, but the constants encode the state machine used by `st.c`. EOF states progress through filemark hit, filemark consumed, EOM/EOD transitions, and error/early-warning states. Ready and door-lock states gate open/read/write/ioctl behavior.

### Dependencies and Integration Points
It depends on completions, mutexes, krefs, and SCSI command definitions. It is private to the tape driver and is paired with `st_options.h` for default values.

### Risks and Test Signals
Because the state structures are broad and shared across many `st.c` paths, changes can silently break close semantics, statistics, or ioctl reporting. Test signals should check MTIOCGET fields after read/write/filemark/EOM paths, kref release after remove, direct-I/O mapping cleanup, and sysfs stats consistency.
