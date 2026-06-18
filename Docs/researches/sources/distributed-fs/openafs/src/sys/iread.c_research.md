# sources/distributed-fs/openafs/src/sys/iread.c

## Purpose
`iread.c` is a legacy diagnostic program that reads bytes from an inode on hard-coded `/vicepa` using the old `xiread` interface.

## Important APIs, types, and functions
The only routine is K&R-style `main`, calling `stat`, `xiread`, `atoi`, and printing the returned buffer.

## Control flow
It stats `/vicepa`, expects three arguments after decrementing `argc`, calls `xiread(dev, inode, 17, offset, buf, count)`, then prints the count and data.

## State and persistence behavior
It reads vice inode contents without modifying persistent state.

## Dependencies and integration points
It depends on legacy exported `xiread` syscall symbols and the `/vicepa` test partition convention.

## Risks
The fixed 50,000-byte buffer is not bounds-checked against the requested count. `/vicepa` and parameter `17` are hard-coded. It prints data as a C string even if the read data is not NUL-terminated.

## Test signals
Run on disposable legacy builds with small read sizes, invalid offsets/counts, missing `/vicepa`, and binary payloads to verify output safety.
