## sources/distributed-fs/ceph-client/fs/smb/smbdirect/rw.c

Purpose: Implements server-side SMBDirect RDMA read/write transfer execution against remote SMBDirect buffer descriptors, using Linux `rdma_rw_ctx` helpers and the socket's negotiated RDMA RW credits.

Important APIs and functions: `smbdirect_connection_rdma_xmit()` is exported and performs RDMA READ when `is_read` is true or RDMA WRITE otherwise. Internal helpers calculate and wait for RW credits, convert a kernel buffer to scatterlist entries, free RDMA IO contexts, and handle read/write completions.

Control flow: The API validates connected state and max read/write size, walks buffer descriptors to clamp descriptor lengths to local buffer length and calculate needed credits, waits for RW credits, allocates one `smbdirect_rw_io` per descriptor, builds a chained SG table over the local buffer, initializes an `rdma_rw_ctx` with remote offset/token and direction, concatenates WRs in reverse descriptor order, posts the first WR, waits for a completion, frees all contexts, restores credits, and wakes credit waiters.

State and persistence: Uses transient `smbdirect_rw_io` objects containing completion pointer, error, RDMA context, SG table, and inline SG storage. Persistent socket-level state is only the atomic RW credit count and negotiated `rw_io.credits.max/num_pages`. No durable persistence exists.

Dependencies and integration points: Depends on `rdma_rw_ctx_init`, `rdma_rw_ctx_wrs`, `rdma_rw_ctx_destroy`, IB send posting, scatterlist helpers, virtual/kmap page conversion, SMBDirect buffer descriptor layout, and credit helpers in `socket.c`/`connection.c`. It is called by upper SMB server logic after clients provide RDMA descriptors.

Risks and edge cases: The debug log prints remaining `buf_len` after descriptor walking, which may be zero and not the original length. Completion waits on a single stack completion shared by all descriptor contexts and then reads the last message error; multi-WR error attribution deserves scrutiny. `smbdirect_connection_rdma_get_sg_list()` uses `kmap_to_page()` for non-vmalloc buffers and requires valid kernel mappings. Descriptor length zero fails, overlarge total transfer fails, and credit restoration must occur on all allocation/posting error paths.

Test signals: RDMA READ and WRITE with one and multiple descriptors, descriptor length clamping, zero descriptor length, transfer larger than negotiated maximum, vmalloc and direct-mapped buffers, credit exhaustion/interruption, post-send failure, CQ error/flush, and disconnect while waiting for RW credits or completion.
