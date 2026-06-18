# sources/distributed-fs/ceph-client/scripts/gdb/linux/config.py

Purpose: Adds a GDB command to dump the kernel's embedded compressed configuration.

Important APIs/classes: `LxConfigDump` command registered as `lx-configdump`.

Control flow: Command accepts an optional filename defaulting to `config.txt`, evaluates `&kernel_config_data` and `&kernel_config_data_end`, reads that memory from the inferior, decompresses gzip data with `zlib.decompress(..., 16)`, writes the result in binary mode, and reports the filename.

State/persistence: Writes the requested output file on the host running GDB. No module cache.

Dependencies/integration: GDB Python API, `zlib`, `linux.utils.read_memoryview`, and kernel symbols from CONFIG_IKCONFIG.

Risks: Fails if `CONFIG_IKCONFIG` is disabled or symbols are unavailable. User-provided filename is used directly. Decompression assumes gzip-wrapped config data.

Test signals: Kernels with and without IKCONFIG, default and explicit filenames, corrupt config data, and remote inferior memory reads.
