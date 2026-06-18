## sources/distributed-fs/beegfs-rust/shared/src/conn.rs

### Purpose
Declares the connection module tree and shared TCP/UDP buffer-size constants for BeeGFS network communication.

### Important APIs, Types, and Functions
- Public modules: `incoming`, `msg_dispatch`, and `outgoing`.
- Private modules: `async_queue`, `store`, and `stream`.
- `TCP_BUF_LEN` is `4 * 1024 * 1024`, matching BeeGFS C++ worker buffer sizes.
- `UDP_BUF_LEN` is `65536`, matching BeeGFS datagram buffer sizes and kept below the TCP size.

### Control Flow and State
No runtime control flow beyond module organization. Constants shape allocation size in incoming/outgoing TCP buffers, UDP datagram buffers, and pooled message buffers.

### Dependencies and Integration Points
The submodules use these constants for socket reads/writes, pooled buffers, and datagram handling. The values must stay aligned with the C/C++ BeeGFS codebase for protocol compatibility and expected maximum message size.

### Risks and Edge Cases
If BeeGFS upstream changes buffer sizes, this crate can reject or truncate valid traffic or allocate more than needed. Fixed 4 MiB buffers per stream/request can create memory pressure under high concurrency.

### Test Signals
No local tests. Integration tests with large messages near TCP/UDP boundaries would exercise these constants.
