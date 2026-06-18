# sources/distributed-fs/ceph-client/samples/auxdisplay/cfag12864b-example.c

Purpose: userspace framebuffer demo for a 128x64 Crystalfontz CFAG12864B LCD.

Important APIs/types/functions: defines LCD geometry macros, framebuffer address/bit helpers, globals `cfag12864b_fd`, `cfag12864b_mem`, and `cfag12864b_buffer`, and functions `cfag12864b_init`, `cfag12864b_exit`, `set`, `unset`, `isset`, `not`, `fill`, `clear`, `format`, `blit`, `example`, and `main`.

Control flow: `main` opens and mmaps the framebuffer path, runs six interactive drawing examples, blits the local buffer after each one, waits for Enter, and unmaps/closes at exit. Drawing functions manipulate a packed 1-bit-per-pixel local buffer before `memcpy` transfers it to mmaped device memory.

State and persistence: state is a process-local shadow buffer plus the mmaped framebuffer. The display persists visually in hardware until overwritten, but the program stores no files.

Dependencies and integration: depends on the auxdisplay framebuffer driver exposing a compatible `/dev/fb*`, POSIX `open`, `mmap`, `munmap`, and framebuffer write permissions.

Risks: bounds checks are compiled out unless `CFAG12864B_DOCHECK` is defined. The program assumes exact device geometry and byte layout. It waits on stdin after each demo, making it unsuitable for unattended tests without input.

Test signals: run against a compatible framebuffer, visually verify point/clear/row/fill/column/invert examples, and use sanitizers or bounds-enabled builds for coordinate helper tests.
