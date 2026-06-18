## sources/distributed-fs/ceph-client/drivers/accel/ivpu/ivpu_fw_log.c

### Purpose
`ivpu_fw_log.c` parses and prints firmware tracing ring buffers stored in ivpu BOs, and tracks read positions for incremental debugfs reads.

### Important APIs, Types, And Functions
The module parameter `ivpu_fw_log_level` sets the default firmware log level. Public APIs are `ivpu_fw_log_print()`, `ivpu_fw_log_mark_read()`, and `ivpu_fw_log_reset()`. Internal helpers validate tracing buffer headers, split printable lines, handle wrap-around, and walk all log buffers in a BO.

### Control Flow
Printing walks critical and verbose log BOs from offset zero, repeatedly validates a `vpu_tracing_buffer_header`, and prints either all data or only unread data. Ring-buffer wrap handling compares firmware `write_index`/`wrap_count` with driver `read_index`/`read_wrap_count`. Mark-read advances read fields to current write positions; reset clears read positions.

### State, Persistence, And Dependencies
Persistent state is in firmware-owned tracing buffer headers inside cached/mappable BOs, including write/read indexes and wrap counts. The driver writes read indexes back to shared memory. Dependencies include firmware boot tracing ABI, ivpu GEM virtual mappings, DRM printers, and ctype filtering.

### Integration Points
Debugfs `fw_log`, coredump generation, fallback coredump logging, and firmware boot diagnostics all call this file. Firmware boot params point firmware at the log BO addresses and sizes.

### Risks
Corrupted log headers must not cause overreads; size and canary checks guard this. Read-index writes are shared with firmware and need memory-order expectations. Line splitting drops nonprintable characters except control characters and can emit partial lines at 255 characters.

### Test Signals
Test empty logs, single and multiple tracing buffers, wrap/no-wrap cases, only-new reads, corrupted canary/header size/size bounds, mark-read/reset behavior, and coredump/debugfs output formatting.
