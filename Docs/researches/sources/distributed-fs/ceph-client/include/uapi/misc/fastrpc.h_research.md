<!-- BEGIN_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/fastrpc.h -->
# sources/distributed-fs/ceph-client/include/uapi/misc/fastrpc.h

Purpose: defines Qualcomm FastRPC userspace ioctls and payloads for creating DSP processes, invoking remote methods, and mapping DMA/shared memory into DSP address spaces.

Important APIs and types: ioctls allocate/free DMA buffers, invoke calls, attach/create process domains, mmap/munmap legacy buffers, map/unmap memory, and query DSP capabilities. Map flags distinguish static, fd-backed, delayed, and no-CPU-map mappings. Process attributes include debug, ptrace, CRC, unsigned module, adaptive QoS, system process, and privileged mode. Payload structs include invoke args, create/static-create, DMA allocation, mmap, mem_map/unmap, and capability query.

Control flow, state, and persistence: userspace creates or attaches to a DSP process, maps buffers, invokes remote handles with argument arrays, and unmaps/frees resources. DSP process and mappings persist until explicit teardown or fd close.

Dependencies and integration points: integrates Qualcomm remoteproc/DSP services, DMA-BUF/fd passing, SMMU mappings, and userspace RPC runtimes.

Risks and test signals: high-risk areas are user pointer validation, fd lifetime, cache maintenance responsibility, secure mappings, typo-preserved ABI fields, and DSP virtual address returns. Test invoke marshalling, map/unmap variants, process creation, capability query, invalid fd/length, and secure-map access.
<!-- END_FILE_RESEARCH: sources/distributed-fs/ceph-client/include/uapi/misc/fastrpc.h -->
