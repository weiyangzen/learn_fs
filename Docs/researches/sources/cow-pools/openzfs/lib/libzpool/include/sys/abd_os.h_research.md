# File Research: sources/cow-pools/openzfs/lib/libzpool/include/sys/abd_os.h

Defines libzpool's OS-specific ABD storage layouts:
- `struct abd_scatter` contains `abd_offset`, `abd_iovcnt`, and a variable-length `struct iovec abd_iov[1]`.
- `struct abd_linear` contains a raw `void *abd_buf`.

These layouts match `lib/libzpool/abd_os.c` and let common ABD code access linear and scatter storage through OS-specific fields.
