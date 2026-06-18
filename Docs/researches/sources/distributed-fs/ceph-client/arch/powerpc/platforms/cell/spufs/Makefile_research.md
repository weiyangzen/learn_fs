# sources/distributed-fs/ceph-client/arch/powerpc/platforms/cell/spufs/Makefile

Purpose: builds the `spufs` kernel object when `CONFIG_SPU_FS` is enabled and wires together the VFS, scheduler, context-switch, fault, syscall, and optional coredump pieces. It also owns the unusual SPU-side helper build, where `spu_save.c`, `spu_restore.c`, and their crt0 assembly are compiled with an SPU cross toolchain, object-copied into dump headers, and included by `switch.c`.

Important build APIs and artifacts: `spufs-y` lists core objects; `spufs-$(CONFIG_COREDUMP)` adds `coredump.o`; `CFLAGS_sched.o := -I$(src)` exposes local trace headers; `clean-files` removes generated `spu_save_dump.h` and `spu_restore_dump.h`. The SPU tool variables default to `spu-gcc`, `spu-ld`, and `spu-objcopy`.

Control flow and dependencies: `switch.o` depends on generated dump headers, so host context switching cannot build until SPU-side save/restore images exist. Risks include missing SPU cross tools, stale generated headers, and include-path drift between kernel headers and SPU helper compilation. Test signals are successful kernel build with `CONFIG_SPU_FS`, generated dump headers present, and `switch.o` rebuilding when SPU helper sources change.
