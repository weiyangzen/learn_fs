# sources/distributed-fs/ceph-client/include/uapi/linux/uio.h

Purpose: Defines scatter/gather vector structures and UIO limits for userspace/kernel transfer APIs.

Important APIs/types/functions: `struct iovec` carries `void __user *iov_base` and `__kernel_size_t iov_len`. The file also exposes devmem/dmabuf fragment/token structures (`dmabuf_cmsg`, `dmabuf_token`) for passing dma-buf-backed memory metadata, plus `UIO_FASTIOV` and `UIO_MAXIOV` constants.

Control flow: System calls such as `readv`, `writev`, `sendmsg`, and `recvmsg` iterate iovec arrays to copy or map data. DMABUF token metadata is consumed by networking/device-memory paths that return fragment ownership information.

State and persistence behavior: Iovecs and tokens are transient call arguments or ancillary data. No state is stored by the header.

Dependencies and integration points: Includes `linux/compiler.h` for `__user` and `linux/types.h`; integrates with VFS, sockets, networking, and dma-buf/development memory APIs.

Risks: Overflow when summing lengths, pointer validation, maximum vector counts, and compat pointer sizing are central. New token structs must preserve alignment and reserved fields.

Test signals: Vectored I/O boundary tests, `UIO_MAXIOV` enforcement, zero-length vectors, compat syscalls, ancillary DMABUF metadata round trips, and overflow/fault injection.
